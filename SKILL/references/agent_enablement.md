# Enabling This Skill in Codex CLI, Gemini CLI, Claude Code, GitHub Copilot, and opencode

This document explains how to make the `cross-agent-workflow` skill available to common AI coding agents. The skill directory is the folder that contains `SKILL.md`, `scripts/`, `references/`, `state/`, and `requirements.txt`.

Use this document when onboarding a user, setting up a new machine, or making this skill available in another repository.

Sources checked: 2026-05-06.

## Skill Directory Rule

Install the whole directory, not only `SKILL.md`.

Expected layout:

```text
cross-agent-workflow/
├── SKILL.md
├── requirements.txt
├── references/
├── scripts/
└── state/
```

If the current folder is named `SKILL`, copy or rename it to `cross-agent-workflow` when installing into tools that expect one directory per skill.

Do not use symlinks unless the target agent is known to follow them. Copying the directory is the safest cross-platform option.

## Shared Preparation

1. Review the skill before installing it, especially `scripts/`.
2. Install Python dependencies only when needed:

```bash
python -m pip install -r cross-agent-workflow/requirements.txt
```

3. Keep credentials outside the skill. Use environment variables for tokens and database connection strings.
4. After installation, test with a read-only task first:

```bash
python cross-agent-workflow/scripts/db_guard.py plan-write --url sqlite:///sample.db --sql "update users set active = 0"
```

The expected behavior is a confirmation plan, not execution.

## OpenAI Codex CLI

Codex supports agent skills as instruction/resource folders. The OpenAI skills catalog describes skills as folders of instructions, scripts, and resources, and notes that Codex should be restarted after installing a skill.

Recommended install options:

### Personal Skill

Use this when the skill should be available across projects:

```bash
mkdir -p ~/.codex/skills
cp -R ./SKILL ~/.codex/skills/cross-agent-workflow
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force $HOME\.codex\skills
Copy-Item -Recurse -Force .\SKILL $HOME\.codex\skills\cross-agent-workflow
```

Restart Codex CLI after installing.

Invoke by asking for the workflow naturally, or explicitly:

```text
Use $cross-agent-workflow to inspect this workbook and record the handoff.
```

### Project Skill

If the Codex version in use supports shared Agent Skills locations, place the skill in the repository:

```bash
mkdir -p .agents/skills
cp -R ./SKILL .agents/skills/cross-agent-workflow
```

If Codex does not detect the project skill, fall back to the personal `~/.codex/skills` location.

## Gemini CLI

Gemini CLI does not use `SKILL.md` as a native skill entrypoint in the same way Claude Code and Copilot do. Use one of these compatibility patterns.

### Option A: Gemini Extension

Use this when you want the whole skill directory installed as reusable context.

1. Create or copy the skill into a Gemini extension directory:

```bash
mkdir -p ~/.gemini/extensions/cross-agent-workflow
cp -R ./SKILL/* ~/.gemini/extensions/cross-agent-workflow/
```

2. Add `gemini-extension.json` beside `SKILL.md`:

```json
{
  "name": "cross-agent-workflow",
  "version": "1.0.0",
  "contextFileName": "SKILL.md"
}
```

3. Restart Gemini CLI. Extensions are loaded on startup.

4. Ask Gemini to use the skill:

```text
Use the cross-agent-workflow extension. Read SKILL.md first, then inspect this xlsx file and update state/HANDOFF.md.
```

For local development of the extension, use:

```bash
gemini extensions link path/to/cross-agent-workflow
```

### Option B: Project GEMINI.md Wrapper

Use this when the skill stays in the repository as `./SKILL`.

Create or update `GEMINI.md` in the repository root:

```markdown
# Gemini Project Instructions

When the user asks for Office/PDF work, guarded database CRUD, GitHub/Gitea collaboration, or cross-agent handoff, read `SKILL/SKILL.md` first and follow it as the operating guide.

Use `SKILL/scripts/` before writing ad hoc code.
Record work in `SKILL/state/ACTION_LOG.md` and update `SKILL/state/HANDOFF.md` before ending.
For database writes or remote Git platform writes, produce a confirmation plan and wait for explicit approval.
```

In Gemini CLI, run:

```text
/memory refresh
/memory show
```

Use `/memory show` to confirm the wrapper instructions are loaded.

### Option C: Gemini Custom Command

Use this when users want an explicit command.

Create `.gemini/commands/cross-agent-workflow.toml`:

```toml
description = "Use the cross-agent workflow skill for Office/PDF, DB CRUD, GitHub/Gitea, and handoff logging."
prompt = """
Read SKILL/SKILL.md and follow the cross-agent-workflow skill.
Use bundled scripts under SKILL/scripts before writing ad hoc code.
Record meaningful work in SKILL/state/ACTION_LOG.md and update SKILL/state/HANDOFF.md before ending.
For database writes or remote Git platform writes, produce a confirmation plan and wait for explicit user approval.

User task:
{{args}}
"""
```

Then run:

```text
/commands reload
/cross-agent-workflow inspect the workbook in this repository
```

## Claude Code

Claude Code supports skills directly. A skill is a directory with a `SKILL.md` file and optional supporting files.

### Personal Skill

Use this for all projects:

```bash
mkdir -p ~/.claude/skills
cp -R ./SKILL ~/.claude/skills/cross-agent-workflow
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force $HOME\.claude\skills
Copy-Item -Recurse -Force .\SKILL $HOME\.claude\skills\cross-agent-workflow
```

### Project Skill

Use this for one repository:

```bash
mkdir -p .claude/skills
cp -R ./SKILL .claude/skills/cross-agent-workflow
```

Claude Code watches existing skill directories for changes. If `.claude/skills` did not exist when the session started, restart Claude Code.

Invoke explicitly:

```text
/cross-agent-workflow inspect this pdf and update the handoff
```

Or ask naturally:

```text
Inspect this docx, summarize the tables, and leave a handoff record.
```

## GitHub Copilot CLI

Copilot CLI supports Agent Skills directly. Project skills can live in `.github/skills`, `.claude/skills`, or `.agents/skills`. Personal skills can live in `~/.copilot/skills` or `~/.agents/skills`.

### Project Skill

Recommended for repository-shared use:

```bash
mkdir -p .github/skills
cp -R ./SKILL .github/skills/cross-agent-workflow
```

Alternative shared locations:

```bash
mkdir -p .agents/skills
cp -R ./SKILL .agents/skills/cross-agent-workflow
```

### Personal Skill

Use this for all local projects:

```bash
mkdir -p ~/.copilot/skills
cp -R ./SKILL ~/.copilot/skills/cross-agent-workflow
```

Start or reload Copilot CLI:

```text
/skills reload
/skills list
/skills info cross-agent-workflow
```

Invoke explicitly:

```text
Use the /cross-agent-workflow skill to inspect this xlsx and record a handoff.
```

Copilot can also choose the skill automatically from its `description`.

## GitHub Copilot in VS Code Extension

Copilot in VS Code is not identical to Copilot CLI.

Current GitHub documentation states that Agent Skills work with Copilot cloud agent, Copilot CLI, and agent mode in Visual Studio Code. In practice, VS Code also has always-on custom instruction mechanisms that differ from CLI skill commands.

Use one of these patterns:

### Option A: Agent Skills in VS Code Agent Mode

Install the skill in a project skill location:

```bash
mkdir -p .github/skills
cp -R ./SKILL .github/skills/cross-agent-workflow
```

Then use Copilot Chat in agent mode and ask:

```text
Use the /cross-agent-workflow skill to inspect this PDF and update the handoff.
```

If the VS Code extension does not expose skill commands in your version, use Option B.

### Option B: Repository Custom Instructions

Create `.github/copilot-instructions.md`:

```markdown
# Copilot Repository Instructions

When the user asks for Office/PDF work, guarded database CRUD, GitHub/Gitea collaboration, or cross-agent handoff, read `SKILL/SKILL.md` first and follow it.

Use `SKILL/scripts/` before writing ad hoc code.
Record meaningful work in `SKILL/state/ACTION_LOG.md`.
Update `SKILL/state/HANDOFF.md` before ending.
For database writes or remote Git platform writes, produce a confirmation plan and wait for explicit user approval.
```

VS Code automatically applies `.github/copilot-instructions.md` to chat requests in the workspace.

### Option C: AGENTS.md for Multi-Agent Workspaces

Create `AGENTS.md` in the repository root:

```markdown
# Agent Instructions

This repository contains a cross-agent skill at `SKILL/`.

For Office/PDF work, guarded database CRUD, GitHub/Gitea collaboration, or handoff logging:

1. Read `SKILL/SKILL.md`.
2. Prefer scripts in `SKILL/scripts/`.
3. Log work in `SKILL/state/ACTION_LOG.md`.
4. Update `SKILL/state/HANDOFF.md` before ending.
5. Do not execute database writes or remote Git platform writes without explicit user confirmation.
```

VS Code supports `AGENTS.md` as always-on instructions when the relevant setting is enabled. This is the best fallback when multiple AI tools share one repository.

## Copilot CLI vs VS Code Extension Differences

Use this rule of thumb:

```text
Copilot CLI: install Agent Skills as folders and manage them with /skills commands.
Copilot VS Code extension: use Agent Skills in agent mode when supported; otherwise use repository instructions or AGENTS.md.
```

Important differences:

- Copilot CLI has explicit skill commands: `/skills reload`, `/skills list`, `/skills info`, and direct `/skill-name` invocation.
- Copilot CLI loads skills from CLI-specific personal locations such as `~/.copilot/skills`.
- VS Code custom instructions are usually always-on context, not on-demand skill loading.
- VS Code can use `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md`, and `CLAUDE.md` as instruction sources.
- VS Code Agent Skills support depends on agent mode and extension/version capabilities; if uncertain, use `.github/copilot-instructions.md` or `AGENTS.md` as the reliable fallback.

## opencode

opencode supports Agent Skills directly. Skills are loaded on demand through opencode's native `skill` tool. Each skill must be one directory whose name matches the `name` field in `SKILL.md`.

### Project Skill

Recommended opencode-native project location:

```bash
mkdir -p .opencode/skills
cp -R ./SKILL .opencode/skills/cross-agent-workflow
```

Cross-agent project locations also work:

```bash
mkdir -p .agents/skills
cp -R ./SKILL .agents/skills/cross-agent-workflow
```

Claude-compatible project location also works:

```bash
mkdir -p .claude/skills
cp -R ./SKILL .claude/skills/cross-agent-workflow
```

### Global Skill

Recommended opencode-native global location:

```bash
mkdir -p ~/.config/opencode/skills
cp -R ./SKILL ~/.config/opencode/skills/cross-agent-workflow
```

Cross-agent global location:

```bash
mkdir -p ~/.agents/skills
cp -R ./SKILL ~/.agents/skills/cross-agent-workflow
```

Claude-compatible global location:

```bash
mkdir -p ~/.claude/skills
cp -R ./SKILL ~/.claude/skills/cross-agent-workflow
```

On Windows PowerShell, use the same target under `$HOME`:

```powershell
New-Item -ItemType Directory -Force $HOME\.config\opencode\skills
Copy-Item -Recurse -Force .\SKILL $HOME\.config\opencode\skills\cross-agent-workflow
```

### Permissions

If opencode does not load the skill, check `opencode.json`. Skills can be allowed, denied, or set to ask.

Project `opencode.json` example:

```json
{
  "permission": {
    "skill": {
      "cross-agent-workflow": "allow",
      "*": "ask"
    }
  }
}
```

Use `ask` if users should approve skill loading each time:

```json
{
  "permission": {
    "skill": {
      "cross-agent-workflow": "ask"
    }
  }
}
```

Do not disable the `skill` tool for agents that need this workflow.

### Usage

Ask naturally:

```text
Use the cross-agent workflow skill to inspect this xlsx and update the handoff.
```

Or explicitly tell opencode to load the skill:

```text
Load the cross-agent-workflow skill, then use its scripts for a guarded database write plan.
```

### AGENTS.md Fallback

opencode also supports `AGENTS.md` for project rules. If skill discovery is unavailable or disabled, create `AGENTS.md` in the repo root:

```markdown
# Agent Instructions

This repository contains a cross-agent skill at `SKILL/`.

For Office/PDF work, guarded database CRUD, GitHub/Gitea collaboration, or handoff logging:

1. Read `SKILL/SKILL.md`.
2. Prefer scripts in `SKILL/scripts/`.
3. Log work in `SKILL/state/ACTION_LOG.md`.
4. Update `SKILL/state/HANDOFF.md` before ending.
5. Do not execute database writes or remote Git platform writes without explicit user confirmation.
```

opencode also supports global instructions at `~/.config/opencode/AGENTS.md`.

## Verification Checklist

- The installed directory contains `SKILL.md`.
- The directory name is `cross-agent-workflow`.
- The agent can see `scripts/`, `references/`, and `state/`.
- The agent can run `python --version`.
- The agent can run one no-side-effect command from `scripts/`.
- The agent records a test entry in `state/ACTION_LOG.md`.
- Database writes and Git platform writes produce confirmation plans only.

## Official References

- OpenAI Codex CLI getting started: https://help.openai.com/en/articles/11096431-openai-codex-ligetting-started
- OpenAI skills catalog: https://github.com/openai/skills
- Gemini CLI custom commands: https://google-gemini.github.io/gemini-cli/docs/cli/custom-commands.html
- Gemini CLI extensions: https://google-gemini.github.io/gemini-cli/docs/extensions/
- Gemini CLI memory commands: https://google-gemini.github.io/gemini-cli/docs/cli/commands.html
- Claude Code skills: https://code.claude.com/docs/en/slash-commands
- GitHub Copilot CLI skills: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills
- GitHub Copilot agent skills overview: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- VS Code custom instructions: https://code.visualstudio.com/docs/copilot/customization/custom-instructions
- opencode Agent Skills: https://opencode.ai/docs/skills/
- opencode Rules / AGENTS.md: https://opencode.ai/docs/rules/
