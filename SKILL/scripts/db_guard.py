#!/usr/bin/env python3
"""Guard database reads and produce confirmation plans for writes.

Subcommands
-----------
query       Execute a read-only SQL statement and return rows as JSON.
plan-write  Produce a confirmation plan for a write statement (no execution).
diagnose    Check whether the required driver for a given SQLAlchemy URL is
            importable and print installation guidance if it is not.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from typing import Any

try:
    from log_action import append_action
except Exception:  # pragma: no cover
    append_action = None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

READ_PREFIXES = ("select", "with", "pragma", "explain", "show", "describe")
WRITE_PREFIXES = (
    "insert", "update", "delete", "merge", "create", "alter", "drop",
    "truncate", "grant", "revoke", "call", "exec",
)

# Maps SQLAlchemy dialect prefix → (pip package name, import name, extra note)
_DRIVER_MAP: dict[str, tuple[str, str, str]] = {
    "mysql+pymysql":            ("PyMySQL",  "pymysql",    ""),
    "mysql+mysqldb":            ("mysqlclient", "MySQLdb", "Requires libmysqlclient on the system."),
    "mariadb+mariadbconnector": ("mariadb",  "mariadb",    "Requires libmariadb on the system."),
    "mssql+pyodbc":             ("pyodbc",   "pyodbc",     "Also requires 'Microsoft ODBC Driver for SQL Server' installed on the OS."),
    "mssql+pymssql":            ("pymssql",  "pymssql",    ""),
    "oracle+oracledb":          ("oracledb", "oracledb",   "Thin mode: no Oracle Instant Client required."),
    "oracle+cx_oracle":         ("cx_Oracle", "cx_Oracle", "Requires Oracle Instant Client on the system."),
    "postgresql+psycopg":       ("psycopg[binary]", "psycopg", ""),
    "postgresql+psycopg2":      ("psycopg2-binary", "psycopg2", ""),
    "postgresql+pg8000":        ("pg8000",   "pg8000",     ""),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def redact_url(url: str) -> str:
    """Replace the password portion of a SQLAlchemy URL with '***'."""
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
    flags: list[str] = []
    if normalized.startswith("update ") and " where " not in normalized:
        flags.append("UPDATE without WHERE")
    if normalized.startswith("delete ") and " where " not in normalized:
        flags.append("DELETE without WHERE")
    if normalized.startswith(("drop ", "truncate ", "alter ")):
        flags.append("DDL/destructive schema operation")
    if normalized.startswith(("call ", "exec ")):
        flags.append("Stored procedure/function may mutate data")
    return flags


def _dialect_prefix(url: str) -> str:
    """Return the dialect+driver prefix from a SQLAlchemy URL (lowercased)."""
    match = re.match(r"^([a-zA-Z0-9_+]+)://", url)
    return match.group(1).lower() if match else ""


def _driver_info(url: str) -> tuple[str, str, str] | None:
    """Return (pip_package, import_name, note) for the URL dialect, or None."""
    prefix = _dialect_prefix(url)
    return _DRIVER_MAP.get(prefix)


def _check_import(module_name: str) -> bool:
    """Return True if the Python module can be imported."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Core commands
# ---------------------------------------------------------------------------

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
        "rollback_guidance": (
            "Prepare a transaction, backup, or inverse statement appropriate to the "
            "target database before execution."
        ),
    }


def run_query(url: str, sql: str, limit: int) -> dict[str, Any]:
    if not is_read(sql):
        return {"ok": False, "error": "not_read_only", "plan": plan_write(url, sql)}

    # Reject high-risk patterns even for reads (safety in depth)
    flags = risk_flags(sql)
    if flags:
        return {
            "ok": False,
            "error": "blocked_by_risk_flags",
            "risk_flags": flags,
            "redacted_url": redact_url(url),
        }

    # SQLite: use stdlib so no SQLAlchemy dialect needed
    if url.startswith("sqlite:///"):
        import sqlite3
        db_path = url.removeprefix("sqlite:///")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(sql).fetchmany(limit)
            columns = list(rows[0].keys()) if rows else []
            return {
                "ok": True,
                "engine": "sqlite3",
                "redacted_url": redact_url(url),
                "columns": columns,
                "row_count_returned": len(rows),
                "rows": [dict(row) for row in rows],
                "limited_to": limit,
            }
        finally:
            conn.close()

    # All other databases: use SQLAlchemy + dialect driver
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        return {
            "ok": False,
            "missing_dependency": "sqlalchemy",
            "install": "pip install SQLAlchemy",
            "hint": "Install SKILL/requirements.txt to get SQLAlchemy.",
        }

    # Check dialect-specific driver *before* attempting connection
    driver_info = _driver_info(url)
    if driver_info:
        pip_pkg, import_name, note = driver_info
        if not _check_import(import_name):
            result: dict[str, Any] = {
                "ok": False,
                "missing_dependency": pip_pkg,
                "install": f"pip install {pip_pkg}",
                "hint": (
                    f"Install the optional DB driver for this dialect, then retry. "
                    f"Run: pip install -r SKILL/requirements-db.txt"
                ),
            }
            if note:
                result["note"] = note
            return result

    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            result_proxy = conn.execute(text(sql))
            rows = result_proxy.fetchmany(limit)
            columns = list(result_proxy.keys())
        return {
            "ok": True,
            "redacted_url": redact_url(url),
            "columns": columns,
            "row_count_returned": len(rows),
            "rows": [dict(zip(columns, row)) for row in rows],
            "limited_to": limit,
        }
    except Exception as exc:  # noqa: BLE001 – catch all DB/driver errors for safe JSON output
        from sqlalchemy.exc import OperationalError, DatabaseError, SQLAlchemyError
        error_type = (
            "operational_error" if isinstance(exc, OperationalError)
            else "database_error" if isinstance(exc, DatabaseError)
            else "sqlalchemy_error" if isinstance(exc, SQLAlchemyError)
            else "connection_error"
        )
        # Redact the URL from the error message in case the driver echoes it
        msg = redact_url(str(exc))
        return {
            "ok": False,
            "error": error_type,
            "redacted_url": redact_url(url),
            "detail": msg,
        }


def diagnose(url: str) -> dict[str, Any]:
    """Check driver availability for the given SQLAlchemy URL."""
    prefix = _dialect_prefix(url)
    result: dict[str, Any] = {
        "url_dialect": prefix,
        "redacted_url": redact_url(url),
    }

    if not prefix:
        result["ok"] = False
        result["error"] = "Could not parse dialect from URL."
        return result

    # SQLite needs no extra driver
    if prefix == "sqlite":
        result["ok"] = True
        result["driver_required"] = None
        result["status"] = "SQLite is included with Python. No additional driver needed."
        return result

    # PostgreSQL default dialect (no explicit driver specified)
    if prefix == "postgresql":
        result["ok"] = True
        result["driver_required"] = "psycopg2-binary or psycopg[binary]"
        result["status"] = (
            "SQLAlchemy will try psycopg2 by default. "
            "Install with: pip install psycopg2-binary"
        )
        return result

    driver_info = _driver_info(url)
    if driver_info is None:
        result["ok"] = True
        result["driver_required"] = "unknown"
        result["status"] = (
            f"Dialect '{prefix}' is not in the built-in driver map. "
            "Check SQLAlchemy docs for the correct driver package."
        )
        return result

    pip_pkg, import_name, note = driver_info
    available = _check_import(import_name)
    result["driver_required"] = pip_pkg
    result["import_name"] = import_name
    result["available"] = available

    if available:
        result["ok"] = True
        result["status"] = f"Driver '{pip_pkg}' is importable. Ready to connect."
    else:
        result["ok"] = False
        result["status"] = f"Missing dependency: {pip_pkg}"
        result["install"] = f"pip install {pip_pkg}"
        result["install_all"] = "pip install -r SKILL/requirements-db.txt"

    if note:
        result["note"] = note

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard database CRUD operations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- query ---------------------------------------------------------------
    query_p = sub.add_parser("query", help="Execute a read-only SQL query.")
    query_p.add_argument("--url", required=True, help="SQLAlchemy database URL.")
    query_p.add_argument("--sql", required=True, help="SQL SELECT (or SHOW/PRAGMA/etc.).")
    query_p.add_argument("--limit", type=int, default=100, help="Max rows to return (default 100).")
    query_p.add_argument("--no-log", action="store_true", help="Skip action log.")

    # -- plan-write ----------------------------------------------------------
    write_p = sub.add_parser("plan-write", help="Create a confirmation plan for write SQL.")
    write_p.add_argument("--url", required=True, help="SQLAlchemy database URL.")
    write_p.add_argument("--sql", required=True, help="SQL write statement to plan.")
    write_p.add_argument("--no-log", action="store_true", help="Skip action log.")

    # -- diagnose ------------------------------------------------------------
    diag_p = sub.add_parser(
        "diagnose",
        help="Check whether the required driver for the given URL is installed.",
    )
    diag_p.add_argument("--url", required=True, help="SQLAlchemy database URL to inspect.")
    diag_p.add_argument("--no-log", action="store_true", help="Skip action log.")

    args = parser.parse_args()

    if args.command == "query":
        output = run_query(args.url, args.sql, args.limit)
        action = "db-query"
    elif args.command == "plan-write":
        output = plan_write(args.url, args.sql)
        action = "db-plan-write"
    else:  # diagnose
        output = diagnose(args.url)
        action = "db-diagnose"

    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))

    if append_action and not args.no_log:
        append_action("agent", action, f"{redact_url(args.url)}: ok={output.get('ok')}")

    return 0 if output.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())

