# Database CRUD Reference

Use this reference before any database work.

## Connection

Use SQLAlchemy URLs. Keep credentials outside the skill and prefer environment variables or secrets supplied by the user.

### SQLite

```text
sqlite:///local.db
sqlite:////absolute/path/to/data.db
```

No driver installation required. SQLite is included with Python.

### PostgreSQL

```text
postgresql+psycopg://user:password@host:5432/dbname
```

Requires: `pip install psycopg[binary]` (psycopg3) or `pip install psycopg2-binary` (psycopg2).

### MySQL

```text
mysql+pymysql://user:password@host:3306/dbname
mysql+pymysql://user:password@host:3306/dbname?charset=utf8mb4
```

Requires: `pip install PyMySQL` (pure-Python, no system libraries needed).

Alternative: `mysqlclient` for a C-based connector (`mysql+mysqldb://...`), requires system `libmysqlclient`.

Install from optional requirements:

```bash
pip install PyMySQL
# or install all optional DB drivers:
pip install -r SKILL/requirements-db.txt
```

### MariaDB

**Option A – MySQL-compatible dialect (recommended, no system libraries)**

Use the same `mysql+pymysql://` URL format. PyMySQL is protocol-compatible with MariaDB:

```text
mysql+pymysql://user:password@host:3306/dbname
```

**Option B – Native MariaDB connector**

Requires the MariaDB Connector/Python package *and* `libmariadb` on the system:

```text
mariadb+mariadbconnector://user:password@host:3306/dbname
```

Install:

```bash
pip install mariadb
# Ensure libmariadb-dev (Linux) or MariaDB Connector/C (Windows/macOS) is installed first.
```

**Recommendation:** Use the `mysql+pymysql` dialect unless you need MariaDB-specific features (e.g., sequences). It is portable and has no system-level dependencies.

### Microsoft SQL Server

```text
mssql+pyodbc://user:password@host:1433/dbname?driver=ODBC+Driver+18+for+SQL+Server
mssql+pyodbc://user:password@dsn_name
mssql+pyodbc://@server/dbname?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes
```

**System requirement:** "Microsoft ODBC Driver for SQL Server" must be installed on the host OS. This is a system-level package — the Python `pyodbc` package alone is not sufficient.

- Windows: Download from https://aka.ms/downloadmsodbcsql
- Linux (Ubuntu/Debian): Follow https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
- macOS: Use Homebrew — `brew install microsoft/mssql-release/msodbcsql18`

After installing the ODBC driver:

```bash
pip install pyodbc
# or:
pip install -r SKILL/requirements-db.txt
```

Verify the ODBC driver name with:

```bash
python -c "import pyodbc; print(pyodbc.drivers())"
```

Use the exact driver name in the URL's `driver=` parameter (spaces replaced with `+`).

### Oracle Database

**Option A – Service name (most common)**

```text
oracle+oracledb://user:password@host:1521/?service_name=ORCLPDB1
```

**Option B – SID (legacy)**

```text
oracle+oracledb://user:password@host:1521/ORCL
```

**Option C – TNS alias (requires tnsnames.ora or wallet)**

```text
oracle+oracledb://:@/?service_name=myservice&dsn=my_tns_alias
```

**Option D – Easy Connect string embedded in DSN**

```text
oracle+oracledb://user:password@//host:1521/ORCLPDB1
```

`oracledb` defaults to thin mode, which does **not** require Oracle Instant Client or any system-level Oracle libraries. Thin mode supports Oracle Database 12.1 and later.

Install:

```bash
pip install oracledb
# or:
pip install -r SKILL/requirements-db.txt
```

Run diagnostics to confirm the driver is importable:

```bash
python SKILL/scripts/db_guard.py diagnose --url "oracle+oracledb://user:pass@host:1521/?service_name=ORCLPDB1"
```

## Installing Optional Drivers

The base `requirements.txt` includes only SQLAlchemy. Database-specific drivers are optional.

```bash
# Install all optional DB drivers at once:
pip install -r SKILL/requirements-db.txt

# Or install only what you need:
pip install PyMySQL          # MySQL and MariaDB (PyMySQL dialect)
pip install mariadb          # MariaDB native connector (requires libmariadb)
pip install pyodbc           # Microsoft SQL Server (requires ODBC driver on OS)
pip install oracledb         # Oracle Database (thin mode, no Oracle Client required)
```

Run the diagnose command to check driver availability before connecting:

```bash
python SKILL/scripts/db_guard.py diagnose --url "mssql+pyodbc://user:pass@host/db"
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

## Cross-Agent Usage Notes

This skill is designed to be used by multiple AI agents (Codex CLI, Gemini CLI, Claude Code, GitHub Copilot, opencode, and others). When running in an agent environment:

- Install optional DB drivers on-demand when the target database is known.
- Use `diagnose` to check driver availability without attempting a live connection.
- Always use environment variables or agent-provided secrets for credentials; never hard-code them.
- All output redacts credentials automatically; check `redacted_url` in the JSON response.
