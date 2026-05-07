# Cross-Agent Workflow Skill

```
最近很少寫程式，反而是一直在做文件然後寫分析報告、工作報告，有點乏了! 請御三家 AI Agent 幫我寫個skill template，以後就可以請他們幫我完成文書工作了!
下面是我的 prompt
I haven't been programming much lately; instead, I've been spending a lot of time creating documentation, writing analysis reports, and work reports. I'm getting a bit tired of it! Could the three major AI agents help me create a skill template so they can handle my paperwork for me in the future?
Below is my prompt.
request:
1. 我想建立一個跨 ai agent 的 skill，涵蓋範圍為，skill 工具請儘量以 python 生態系及python script完成，以達到泛用的目的
   目標1 協作 docx、pptx、xlsx 以及 read pdf
   目標2 database crud 協助，當然除了 query 以外其餘都要進一步確認
   目標3 gitea 與 github 的協作
請先協助規劃，在實作過程中必須請實作的 ai agent 記錄，使下一次實作的 ai agent 可以接手完成，而不依賴 ai agent session
2. 請寫一份文件，告知使用者要如何讓 codex cli、gemini cli、claude code 以及 github copilot 使用這些 skill, github copilot 如果 cli 與 vscode extension 使用方式不同的話也要一併說明
3. 我忘了 opencode! 請協助更新使用者使用文件
-------------------------------------------------
1. I want to create a cross-AI agent skill, covering the following scope. The skill tools should ideally be built using the Python ecosystem and Python scripts to achieve versatility.
   Goal 1: Collaborate on docx, pptx, xlsx, and read PDFs.
   Goal 2: Assist with database CRUD operations; all functions except querying need further confirmation.
   Goal 3: Collaborate with Gitea and GitHub.
Please assist with the planning. During implementation, the AI ​​agent must record the implementation so that subsequent AI agents can take over without relying on AI agent sessions.
2. Please write a document instructing users on how to use these skills with Codex CLI, Gemini CLI, Claude Code, and GitHub Copilot. If the usage differs between the GitHub Copilot CLI and the VS Code extension, please also explain.
3. I forgot OpenCode! Please help update the user documentation.
This file and `SKILL/SKILL.md` are the canonical docs. Other markdown files are optional deep references.
```

This repository provides a Python-first, portable skill set for AI agents that need to work on documents, databases, and Git collaboration tasks with clear safety guardrails.

This file and `SKILL/SKILL.md` are the canonical docs. Other markdown files are optional deep references.

## Scope

- Office/PDF processing: `.docx`, `.pptx`, `.xlsx`, `.pdf`
- Advanced extraction: layout-aware PDF, table detection, metadata
- Batch pipelines: mixed file types, structured output, error recovery
- Work-report artifacts: reusable Markdown templates, xlsx field specs, and pptx outlines
- Guarded database CRUD: read allowed, writes require explicit confirmation plan
- GitHub/Gitea collaboration: local status/diff, safe reads, planned writes
- Cross-agent continuity: persistent handoff and action logs

## Quick Start

```bash
pip install -r SKILL/requirements.txt
python SKILL/scripts/batch_extractor.py --check-deps
python SKILL/scripts/doc_inspect.py "sample.pdf" --format markdown
```

## Core Scripts

- `SKILL/scripts/doc_inspect.py`: fast structure inspection
- `SKILL/scripts/doc_extract.py`: full text/table extraction
- `SKILL/scripts/pdf_skill.py`: advanced PDF extraction (`auto`, `pdfplumber`, `pypdf`)
- `SKILL/scripts/batch_extractor.py`: batch processing for 10+ files
- `SKILL/scripts/db_guard.py`: database query + write-plan workflow
- `SKILL/scripts/git_collab.py`: local Git summaries + API read/write planning
- `SKILL/scripts/log_action.py`: append action and handoff records

## Common Commands

```bash
# Inspect one document
python SKILL/scripts/doc_inspect.py "report.pdf" --format markdown

# Extract one document
python SKILL/scripts/doc_extract.py "report.pdf" --format json --max-chars 50000

# Advanced PDF (layout-aware)
python SKILL/scripts/pdf_skill.py "form.pdf" --engine pdfplumber --format json

# Batch extraction
python SKILL/scripts/batch_extractor.py --files "*.pdf" "*.xlsx" --output extracted/ --format json

# DB read-only query
python SKILL/scripts/db_guard.py query --url "sqlite:///sample.db" --sql "select * from users limit 5"

# DB write planning (requires user confirmation before execution)
python SKILL/scripts/db_guard.py plan-write --url "sqlite:///sample.db" --sql "update users set active = 0 where id = 1"

# Git collaboration
python SKILL/scripts/git_collab.py local-status --repo .
python SKILL/scripts/git_collab.py local-diff --repo . --stat
```

## Safety Rules

- Never execute database write operations without explicit user confirmation.
- Never perform GitHub/Gitea write actions without a confirmation plan.
- Prefer writing modified Office files to new output files.
- Do not store tokens, passwords, or DB credentials in this repository.

## Minimal Reading Path for Agents

1. `SKILL/SKILL.md` (required operating guide)
2. `SKILL/state/HANDOFF.md` (current state)
3. `SKILL/state/ACTION_LOG.md` (recent actions)

Only if needed:

- `SKILL/references/extraction_guide.md`
- `SKILL/references/work_report_templates.md`
- `SKILL/references/database_crud.md`
- `SKILL/references/git_platforms.md`
- `SKILL/references/agent_enablement.md`

## Notes

- The repository includes two additional extraction-oriented skills:
  - `doc-extraction-advanced`
  - `batch-document-processor`
- Recommended output for automation is JSON.
- For scanned PDFs, run OCR before extraction (OCR is not built into these scripts).
