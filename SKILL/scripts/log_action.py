#!/usr/bin/env python3
"""Append portable Markdown action logs for cross-agent handoff."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = SKILL_ROOT / "state"
ACTION_LOG = STATE_DIR / "ACTION_LOG.md"
HANDOFF = STATE_DIR / "HANDOFF.md"


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def append_action(actor: str, action: str, details: str, log_path: Path = ACTION_LOG) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("# Action Log\n", encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n## {utc_now()}\n\n")
        fh.write(f"- actor: {actor}\n")
        fh.write(f"- action: {action}\n")
        fh.write(f"- details: {details}\n")


def update_handoff(status: str, next_steps: str, path: Path = HANDOFF) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    content = (
        "# Handoff\n\n"
        "## Current Status\n\n"
        f"{status.strip()}\n\n"
        "## Next Steps\n\n"
        f"{next_steps.strip()}\n"
    )
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Append cross-agent action logs.")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Append one action log entry.")
    add.add_argument("--actor", default="agent")
    add.add_argument("--action", required=True)
    add.add_argument("--details", required=True)

    handoff = sub.add_parser("handoff", help="Replace the handoff summary.")
    handoff.add_argument("--actor", default="agent")
    handoff.add_argument("--status", required=True)
    handoff.add_argument("--next-steps", required=True)

    args = parser.parse_args()
    if args.command == "add":
        append_action(args.actor, args.action, args.details)
    elif args.command == "handoff":
        update_handoff(args.status, args.next_steps)
        append_action(args.actor, "update-handoff", args.status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
