---
name: cross-agent-workflow
description: Cross-agent collaboration workflow for Office/PDF documents, guarded database CRUD, and GitHub/Gitea collaboration. Use when an AI agent needs portable Python-first tooling plus persistent handoff records.
---

---
name: doc-extraction-advanced
description: Advanced extraction for PDF, Excel, Word, and PowerPoint with layout-aware PDF handling and table detection. Provides three levels: inspect, extract, and batch.
---

---
name: batch-document-processor
description: Batch processing for document extraction pipelines. Use for 10+ files, mixed file types, parallel execution, error recovery, and structured outputs.
---

# Cross-Agent Workflow

Use this file as the primary operating guide. Keep instructions short, safe, and reproducible across agents.

## Canonical Docs

- Primary: `SKILL/SKILL.md` and `README.md`
- State: `state/HANDOFF.md` and `state/ACTION_LOG.md`
- Optional deep references in `references/` only when needed

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

## Skills in This Repository

- `cross-agent-workflow` (foundation)
- `doc-extraction-advanced` (single-file advanced extraction)
- `batch-document-processor` (10+ files and pipelines)

## Document Workflow (3 Levels)

### Level 1: Inspect (fast)

- Use `scripts/doc_inspect.py` for concise structure summaries.

```bash
python SKILL/scripts/doc_inspect.py "input.docx" --format markdown
python SKILL/scripts/doc_inspect.py "report.pdf" --format json
```

### Level 2: Extract (full content)

- Use `scripts/doc_extract.py` when the agent needs fuller extracted text or tables.
- Use `scripts/pdf_skill.py` for advanced PDF operations: layout-aware extraction, table detection, page analysis, and metadata.

```bash
python SKILL/scripts/doc_extract.py "report.pdf" --format json --max-chars 20000
python SKILL/scripts/pdf_skill.py "document.pdf" --format markdown --engine auto
python SKILL/scripts/pdf_skill.py "document.pdf" --format json --engine pdfplumber
```

PDF engine guidance:

- `pdfplumber`: best for forms/tables/layout
- `pypdf`: faster simple text extraction
- `auto`: preferred default

### Level 3: Batch (pipeline mode)

- Use `scripts/batch_extractor.py` for mixed file sets and consistent output.

```bash
python SKILL/scripts/batch_extractor.py --files "*.pdf" "*.xlsx" --output extracted/ --format json
python SKILL/scripts/batch_extractor.py --check-deps
```

## Database Workflow

- Load `references/database_crud.md` before touching a database.
- Use `scripts/db_guard.py query` for read-only SQL.
- Use `scripts/db_guard.py plan-write` for any non-query SQL; do not execute the resulting plan until the user confirms.
- Use `scripts/db_guard.py diagnose` to check driver availability and get install guidance before connecting.
- Use SQLAlchemy URLs for portability across all supported databases:
  - SQLite: `sqlite:///local.db`
  - PostgreSQL: `postgresql+psycopg://user:pass@host:5432/dbname`
  - MySQL: `mysql+pymysql://user:pass@host:3306/dbname`
  - MariaDB: `mysql+pymysql://user:pass@host:3306/dbname` (or `mariadb+mariadbconnector://...`)
  - Microsoft SQL Server: `mssql+pyodbc://user:pass@host:1433/dbname?driver=ODBC+Driver+18+for+SQL+Server`
  - Oracle: `oracle+oracledb://user:pass@host:1521/?service_name=ORCLPDB1`
- Install database-specific drivers from `requirements-db.txt` when needed (see below).

Example:

```bash
python SKILL/scripts/db_guard.py query --url "sqlite:///sample.db" --sql "select * from users limit 5"
python SKILL/scripts/db_guard.py plan-write --url "sqlite:///sample.db" --sql "update users set active = 0 where last_login < '2025-01-01'"
python SKILL/scripts/db_guard.py diagnose --url "oracle+oracledb://user:pass@host:1521/?service_name=ORCLPDB1"
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

## Output and Performance Notes

- Prefer JSON output for downstream automation.
- For scanned/image PDFs, OCR is required before extraction.
- Batch defaults to parallel workers and continues on per-file failures.

## Dependency Model

- Scripts should fail with clear missing-dependency messages instead of stack traces.
- Install base dependencies from `requirements.txt` for full Office/PDF/DB/API support.
- Install optional database drivers from `requirements-db.txt` on-demand when the task requires a specific database:
  - `pip install -r SKILL/requirements-db.txt` — all optional DB drivers
  - `pip install PyMySQL` — MySQL or MariaDB (PyMySQL dialect, pure-Python)
  - `pip install mariadb` — MariaDB native connector (requires libmariadb on the system)
  - `pip install pyodbc` — Microsoft SQL Server (requires ODBC driver on OS)
  - `pip install oracledb` — Oracle Database (thin mode, no Oracle Client required)
- Use `scripts/db_guard.py diagnose --url ...` to check which driver is needed before installing.
- Keep new scripts Python-first and portable across agents.

## Minimal Reference Path

Read references only when required by task type:

- Document/PDF details: `references/office_pdf.md`, `references/extraction_guide.md`
- Database details: `references/database_crud.md`
- Git platform APIs: `references/git_platforms.md`
- Agent setup docs: `references/agent_enablement.md`

## Agent Enablement

- Read `references/agent_enablement.md` when installing or explaining this skill for Codex CLI, Gemini CLI, Claude Code, GitHub Copilot CLI, GitHub Copilot in VS Code, or opencode.
