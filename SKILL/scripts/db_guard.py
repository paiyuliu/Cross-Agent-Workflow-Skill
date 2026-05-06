#!/usr/bin/env python3
"""Guard database reads and produce confirmation plans for writes."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from typing import Any

try:
    from log_action import append_action
except Exception:  # pragma: no cover
    append_action = None


READ_PREFIXES = ("select", "with", "pragma", "explain", "show", "describe")
WRITE_PREFIXES = ("insert", "update", "delete", "merge", "create", "alter", "drop", "truncate", "grant", "revoke", "call", "exec")


def redact_url(url: str) -> str:
    return re.sub(r"://([^:/@\s]+):([^@\s]+)@", r"://\1:***@", url)


def normalize_sql(sql: str) -> str:
    return " ".join(sql.strip().split())


def first_word(sql: str) -> str:
    match = re.match(r"^\s*(\w+)", sql, re.IGNORECASE)
    return match.group(1).lower() if match else ""


def is_read(sql: str) -> bool:
    return first_word(sql) in READ_PREFIXES


def classify_write(sql: str) -> str:
    word = first_word(sql)
    if word in ("insert",):
        return "create"
    if word in ("update", "merge"):
        return "update"
    if word in ("delete", "truncate"):
        return "delete"
    if word in ("create", "alter", "drop"):
        return "ddl"
    if word in ("grant", "revoke"):
        return "permission"
    if word in ("call", "exec"):
        return "procedure"
    return "unknown"


def risk_flags(sql: str) -> list[str]:
    normalized = normalize_sql(sql).lower()
    flags = []
    if normalized.startswith("update ") and " where " not in normalized:
        flags.append("UPDATE without WHERE")
    if normalized.startswith("delete ") and " where " not in normalized:
        flags.append("DELETE without WHERE")
    if normalized.startswith(("drop ", "truncate ", "alter ")):
        flags.append("DDL/destructive schema operation")
    if normalized.startswith(("call ", "exec ")):
        flags.append("Stored procedure/function may mutate data")
    return flags


def plan_write(url: str, sql: str) -> dict[str, Any]:
    return {
        "ok": True,
        "requires_confirmation": True,
        "redacted_url": redact_url(url),
        "sql": normalize_sql(sql),
        "operation_class": classify_write(sql),
        "risk_flags": risk_flags(sql),
        "execution_status": "not_executed",
        "required_next_step": "Ask the user to explicitly approve this exact write plan before execution.",
        "rollback_guidance": "Prepare a transaction, backup, or inverse statement appropriate to the target database before execution.",
    }


def run_query(url: str, sql: str, limit: int) -> dict[str, Any]:
    if not is_read(sql):
        return {"ok": False, "error": "not_read_only", "plan": plan_write(url, sql)}
    if url.startswith("sqlite:///"):
        db_path = url.removeprefix("sqlite:///")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(sql).fetchmany(limit)
            columns = rows[0].keys() if rows else []
            return {
                "ok": True,
                "engine": "sqlite3",
                "redacted_url": redact_url(url),
                "columns": list(columns),
                "row_count_returned": len(rows),
                "rows": [dict(row) for row in rows],
                "limited_to": limit,
            }
        finally:
            conn.close()
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        return {
            "ok": False,
            "missing_dependency": "sqlalchemy",
            "install": "Install SQLAlchemy and the target DB driver from SKILL/requirements.txt.",
        }
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchmany(limit)
        columns = list(result.keys())
    return {
        "ok": True,
        "redacted_url": redact_url(url),
        "columns": columns,
        "row_count_returned": len(rows),
        "rows": [dict(zip(columns, row)) for row in rows],
        "limited_to": limit,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard database CRUD operations.")
    sub = parser.add_subparsers(dest="command", required=True)

    query = sub.add_parser("query", help="Execute a read-only SQL query.")
    query.add_argument("--url", required=True)
    query.add_argument("--sql", required=True)
    query.add_argument("--limit", type=int, default=100)
    query.add_argument("--no-log", action="store_true")

    write = sub.add_parser("plan-write", help="Create a confirmation plan for write SQL.")
    write.add_argument("--url", required=True)
    write.add_argument("--sql", required=True)
    write.add_argument("--no-log", action="store_true")

    args = parser.parse_args()
    if args.command == "query":
        output = run_query(args.url, args.sql, args.limit)
        action = "db-query"
    else:
        output = plan_write(args.url, args.sql)
        action = "db-plan-write"
    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
    if append_action and not args.no_log:
        append_action("agent", action, f"{redact_url(args.url)}: ok={output.get('ok')}")
    return 0 if output.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
