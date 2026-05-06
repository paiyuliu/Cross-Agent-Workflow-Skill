---
name: cross-agent-workflow
description: Cross-agent collaboration workflow for Office documents, PDF reading, guarded database CRUD, and GitHub/Gitea collaboration. Use when an AI agent needs to inspect or modify docx, pptx, xlsx, or pdf files; query or plan database CRUD with explicit confirmation for non-query operations; collaborate with GitHub or Gitea issues, pull requests, comments, branches, diffs, or repository metadata; or leave handoff records so another AI agent can continue without relying on session memory.
---

# Cross-Agent Workflow

Use this skill as a portable operating guide for agents working with business documents, databases, and Git platforms. Prefer the bundled Python scripts before writing one-off code.

## Required Handoff Discipline

- Read `state/HANDOFF.md` before starting work.
- Append every meaningful action to `state/ACTION_LOG.md` using `scripts/log_action.py`.
- Update `state/HANDOFF.md` before ending work with current status, completed work, blockers, and exact next steps.
- Never rely on chat/session memory as the only record of implementation state.

## Safety Rules

- Treat database reads as allowed when credentials and scope are already provided.
- Treat database create, update, delete, truncate, drop, alter, grant, revoke, merge, and procedure execution as write operations.
- For database write operations, generate a confirmation plan first and wait for explicit user approval before execution.
- For GitHub/Gitea write operations, generate a confirmation plan first for comments, issue creation, labels, PR creation, merge, close, reopen, delete, release, or push.
- Prefer writing modified Office files as new output files unless the user explicitly asks to overwrite.
- Do not store access tokens, passwords, or database credentials in this skill.

## Document Workflow

- Use `scripts/doc_inspect.py` for a concise JSON or Markdown summary of `.docx`, `.pptx`, `.xlsx`, and `.pdf` files.
- Use `scripts/doc_extract.py` when the agent needs fuller extracted text or tables.
- Use `scripts/pdf_skill.py` for advanced PDF operations: layout-aware extraction, table detection, page analysis, and metadata.
- Load `references/office_pdf.md` before adding document-editing logic or troubleshooting dependencies.

Example:

```bash
python SKILL/scripts/doc_inspect.py "input.docx" --format markdown
python SKILL/scripts/doc_extract.py "report.pdf" --format json --max-chars 20000
python SKILL/scripts/pdf_skill.py "document.pdf" --format markdown --engine auto
python SKILL/scripts/pdf_skill.py "document.pdf" --format json --engine pdfplumber
```

## Database Workflow

- Load `references/database_crud.md` before touching a database.
- Use `scripts/db_guard.py query` for read-only SQL.
- Use `scripts/db_guard.py plan-write` for any non-query SQL; do not execute the resulting plan until the user confirms.
- Use SQLAlchemy URLs for portability, for example `sqlite:///local.db`, `postgresql+psycopg://...`, `mysql+pymysql://...`, or `mssql+pyodbc://...`.

Example:

```bash
python SKILL/scripts/db_guard.py query --url "sqlite:///sample.db" --sql "select * from users limit 5"
python SKILL/scripts/db_guard.py plan-write --url "sqlite:///sample.db" --sql "update users set active = 0 where last_login < '2025-01-01'"
```

## GitHub and Gitea Workflow

- Load `references/git_platforms.md` before using remote APIs.
- Use local Git commands for repo state, branches, diffs, and commits.
- Use `scripts/git_collab.py local-status` and `scripts/git_collab.py local-diff` for reproducible summaries.
- Use `scripts/git_collab.py api-get` for safe reads from GitHub/Gitea REST APIs.
- Use `scripts/git_collab.py plan-api-write` to prepare write operations for confirmation.

Example:

```bash
python SKILL/scripts/git_collab.py local-status --repo .
python SKILL/scripts/git_collab.py local-diff --repo . --stat
python SKILL/scripts/git_collab.py plan-api-write --platform github --method POST --endpoint /repos/OWNER/REPO/issues --body '{"title":"Example"}'
```

## Dependency Model

- Scripts should fail with clear missing-dependency messages instead of stack traces.
- Install optional dependencies from `requirements.txt` only when the task needs full Office/PDF/DB/API support.
- Keep new scripts Python-first and portable across agents.

## Agent Enablement

- Read `references/agent_enablement.md` when installing or explaining this skill for Codex CLI, Gemini CLI, Claude Code, GitHub Copilot CLI, GitHub Copilot in VS Code, or opencode.
