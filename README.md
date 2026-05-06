# Cross-Agent Workflow Skill

This repository contains a portable `cross-agent-workflow` skill for AI agents that need to work across business documents, databases, and Git collaboration platforms. The skill is designed to keep work reproducible between agents by pairing operating instructions with small Python helper scripts and persistent handoff records.

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

```


## What This Skill Covers

- Office and PDF inspection for `.docx`, `.pptx`, `.xlsx`, and `.pdf` files.
- Fuller document extraction, including PDF metadata, page text, tables, and layout-aware analysis when optional PDF dependencies are installed.
- Guarded database CRUD workflows that allow read-only queries and require a confirmation plan before any write operation.
- GitHub and Gitea collaboration workflows for local status, diffs, safe API reads, and planned API writes.
- Cross-agent continuity through `state/HANDOFF.md` and `state/ACTION_LOG.md`.

## Folder Layout

- `SKILL/SKILL.md` is the main skill manifest and operating guide.
- `SKILL/scripts/` contains reusable Python tools for documents, PDFs, databases, Git collaboration, and action logging.
- `SKILL/references/` contains deeper workflow notes for Office/PDF handling, database CRUD, Git platforms, and enabling the skill in other agents.
- `SKILL/state/` stores handoff and action-log files so work can continue without relying only on chat history.
- `SKILL/requirements.txt` lists optional dependencies for full document, PDF, database, and API support.

## Main Scripts

- `doc_inspect.py`: concise JSON or Markdown summaries of Office and PDF files.
- `doc_extract.py`: fuller text and table extraction from supported document formats.
- `pdf_skill.py`: advanced PDF extraction with automatic engine selection, layout-aware extraction, table detection, page analysis, and metadata support.
- `db_guard.py`: read-only SQL execution plus write-operation planning that highlights risky mutations.
- `git_collab.py`: local Git summaries, GitHub/Gitea API reads, and API write-plan generation.
- `log_action.py`: structured updates for the action log and handoff file.

## Basic Usage

```bash
python SKILL/scripts/doc_inspect.py "input.docx" --format markdown
python SKILL/scripts/doc_extract.py "report.pdf" --format json --max-chars 20000
python SKILL/scripts/pdf_skill.py "document.pdf" --format markdown --engine auto
python SKILL/scripts/db_guard.py query --url "sqlite:///sample.db" --sql "select * from users limit 5"
python SKILL/scripts/git_collab.py local-status --repo .
python SKILL/scripts/git_collab.py local-diff --repo . --stat
```

## Safety Model

Database write operations, including create, update, delete, truncate, drop, alter, grant, revoke, merge, and procedure execution, must be planned first and executed only after explicit user approval. GitHub and Gitea write operations, such as creating issues, commenting, labeling, merging, closing, reopening, deleting, releasing, or pushing, also require a confirmation plan before execution.

Modified Office files should be written as new output files unless the user explicitly asks to overwrite an existing file. Access tokens, passwords, and database credentials should not be stored in this skill directory.

## Dependencies

The scripts are Python-first and intended to fail with clear missing-dependency messages. Install the optional packages in `SKILL/requirements.txt` only when a task needs full Office, PDF, database, or API support:

```bash
pip install -r SKILL/requirements.txt
```

The current handoff notes indicate that scripts have been compiled and partially validated, but full document and API testing should be repeated after dependencies are installed in the active Python environment.
