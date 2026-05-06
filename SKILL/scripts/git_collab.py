#!/usr/bin/env python3
"""Local Git helpers and safe GitHub/Gitea API planning."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    from log_action import append_action
except Exception:  # pragma: no cover
    append_action = None


DEFAULT_BASE = {
    "github": "https://api.github.com",
    "gitea": "",
}


def run_git(repo: str, args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", "-C", repo, *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {"ok": proc.returncode == 0, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def token_for(platform: str) -> str | None:
    if platform == "github":
        return os.environ.get("GITHUB_TOKEN")
    if platform == "gitea":
        return os.environ.get("GITEA_TOKEN")
    return None


def api_get(platform: str, base_url: str, endpoint: str) -> dict[str, Any]:
    base = base_url or DEFAULT_BASE.get(platform, "")
    if not base:
        return {"ok": False, "error": "missing_base_url", "hint": "Provide --base-url for Gitea."}
    url = base.rstrip("/") + "/" + endpoint.lstrip("/")
    headers = {"Accept": "application/json"}
    token = token_for(platform)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = body
            return {"ok": True, "url": url, "status": response.status, "body": parsed}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "url": url, "status": exc.code, "error": exc.read().decode("utf-8", errors="replace")}
    except urllib.error.URLError as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def plan_api_write(platform: str, base_url: str, method: str, endpoint: str, body: str | None) -> dict[str, Any]:
    base = base_url or DEFAULT_BASE.get(platform, "")
    parsed_body = None
    if body:
        try:
            parsed_body = json.loads(body)
        except json.JSONDecodeError as exc:
            return {"ok": False, "error": "invalid_json_body", "details": str(exc)}
    return {
        "ok": True,
        "requires_confirmation": True,
        "platform": platform,
        "base_url": base,
        "method": method.upper(),
        "endpoint": endpoint,
        "body": parsed_body,
        "headers": {"Accept": "application/json", "Authorization": "Bearer ***" if token_for(platform) else None},
        "execution_status": "not_executed",
        "required_next_step": "Ask the user to explicitly approve this exact API write plan before execution.",
    }


def print_json(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub/Gitea collaboration helper.")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("local-status")
    status.add_argument("--repo", default=".")
    status.add_argument("--no-log", action="store_true")

    diff = sub.add_parser("local-diff")
    diff.add_argument("--repo", default=".")
    diff.add_argument("--stat", action="store_true")
    diff.add_argument("--no-log", action="store_true")

    get = sub.add_parser("api-get")
    get.add_argument("--platform", choices=["github", "gitea"], required=True)
    get.add_argument("--base-url", default="")
    get.add_argument("--endpoint", required=True)
    get.add_argument("--no-log", action="store_true")

    write = sub.add_parser("plan-api-write")
    write.add_argument("--platform", choices=["github", "gitea"], required=True)
    write.add_argument("--base-url", default="")
    write.add_argument("--method", required=True)
    write.add_argument("--endpoint", required=True)
    write.add_argument("--body")
    write.add_argument("--no-log", action="store_true")

    args = parser.parse_args()
    if args.command == "local-status":
        output = run_git(args.repo, ["status", "--short", "--branch"])
        action = "git-local-status"
    elif args.command == "local-diff":
        output = run_git(args.repo, ["diff", "--stat"] if args.stat else ["diff"])
        action = "git-local-diff"
    elif args.command == "api-get":
        output = api_get(args.platform, args.base_url, args.endpoint)
        action = "git-api-get"
    else:
        output = plan_api_write(args.platform, args.base_url, args.method, args.endpoint, args.body)
        action = "git-plan-api-write"

    print_json(output)
    if append_action and not args.no_log:
        append_action("agent", action, f"ok={output.get('ok')}")
    return 0 if output.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
