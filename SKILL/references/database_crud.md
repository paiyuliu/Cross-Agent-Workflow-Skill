# Database CRUD Reference

Use this reference before any database work.

## Connection

Use SQLAlchemy URLs. Keep credentials outside the skill and prefer environment variables or secrets supplied by the user.

Examples:

```text
sqlite:///local.db
postgresql+psycopg://user:password@host:5432/dbname
mysql+pymysql://user:password@host:3306/dbname
mssql+pyodbc://user:password@dsn
```

## Read Operations

- Allow `SELECT`, `WITH`, `PRAGMA`, `EXPLAIN`, `SHOW`, and `DESCRIBE` as read-like operations.
- Limit result size unless the user explicitly asks for full output.
- Record SQL, target URL with credentials redacted, row count, and summary in `state/ACTION_LOG.md`.

## Write Operations

Generate a confirmation plan before executing any write operation:

- SQL statement with credentials redacted.
- Operation class: create, update, delete, ddl, permission, procedure, or unknown write.
- Target tables or objects if detectable.
- Risk flags, especially missing `WHERE` for `UPDATE` or `DELETE`.
- Estimated blast radius when possible.
- Suggested rollback or backup step.

Do not execute a write operation until the user explicitly confirms the exact plan.

## High-Risk Defaults

- Block `UPDATE` and `DELETE` without `WHERE` by default.
- Block `DROP`, `TRUNCATE`, and `ALTER` until the user confirms backup/rollback readiness.
- Treat stored procedure/function calls as writes unless clearly read-only.
- Do not log raw passwords, tokens, or full connection strings.
