# GitHub and Gitea Reference

Use this reference before GitHub or Gitea collaboration.

## Local Git

- Prefer local Git for status, branch, diff, and commit metadata.
- Never discard user changes unless the user explicitly asks.
- Avoid destructive commands such as hard reset, forced checkout, branch deletion, and force push unless explicitly approved.

## Remote API Reads

- GitHub base URL: `https://api.github.com`.
- Gitea base URL normally looks like `https://gitea.example.com/api/v1`.
- Read operations may fetch repository metadata, issues, pull requests, comments, branches, commits, and statuses.
- Tokens should come from environment variables such as `GITHUB_TOKEN` or `GITEA_TOKEN`.

## Remote API Writes

Generate a confirmation plan before writing:

- Platform and base URL.
- HTTP method and endpoint.
- Redacted headers.
- JSON body or form payload.
- Expected side effect.
- Rollback or follow-up action if available.

Write operations include issue creation, comments, labels, PR creation, merge, close/reopen, releases, branch protection changes, and repository settings.

## Common Commands

```bash
python SKILL/scripts/git_collab.py local-status --repo .
python SKILL/scripts/git_collab.py local-diff --repo . --stat
python SKILL/scripts/git_collab.py api-get --platform github --endpoint /repos/OWNER/REPO
python SKILL/scripts/git_collab.py plan-api-write --platform gitea --base-url https://gitea.example.com/api/v1 --method POST --endpoint /repos/OWNER/REPO/issues --body '{"title":"Example"}'
```
