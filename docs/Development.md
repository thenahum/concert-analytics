# Concert Analytics Development

This document records the current development workflow and cleanup direction. Commands that affect APIs, databases, SSH tunnels, or the home directory should be treated as stateful operations.

## Environment

The root `requirements.txt` is the preferred environment contract for this repository. This project is a monorepo-style analysis workspace, so one pinned environment is currently preferred over independent package lockfiles.

Expected local setup direction:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --no-build-isolation -r requirements.txt
```

`requirements.txt` includes editable installs for `loadin` and `setkit`, so the command should be run from the repository root.

`--no-build-isolation` keeps local editable package installation aligned with the pinned repository environment.

## Secrets

Use `.env.example` to see required variables. Do not commit or expose real values from `.env`.

Important variables include:

- `SETLIST_FM_API_KEY`
- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `PGHOST`
- `PGPORT`
- `PGUSER`
- `PGPASSWORD`
- `PGDATABASE`
- `DBT_DB`
- `DBT_SCHEMA`
- SSH tunnel settings for local development

Agents and scripts must not print credentials or connection strings.

## Data And Caches

`data/` is local-only. It is a staging/cache layer for API responses before data is loaded into PostgreSQL.

PostgreSQL is the durable source of truth.

Do not commit API cache payloads, notebook checkpoints, dbt `target/`, dbt logs, or local database-tool metadata.

## Database And dbt

The intended schema convention is:

- `raw`
- `analytics_staging`
- `analytics_mart`
- `analytics_project`

dbt should own warehouse bootstrap, including the raw schema and database functions required by dbt models.

Bootstrap is meant for rebuild and disaster-recovery setup, not for every routine dbt run.

dbt task shortcuts currently live in `tasks.py`.

Known task examples:

```bash
inv deps
inv bootstrap
inv run
inv build
inv test
inv dbt --command "run --select tag:project_002"
```

These tasks may start an SSH tunnel and may create or replace a symlink at `~/.dbt/profiles.yml`. Treat them as stateful.

`inv bootstrap` calls `dbt run-operation bootstrap_database`. It creates schemas and the `analytics_mart.similarity(...)` wrapper around Postgres `pg_trgm` similarity. Creating the `pg_trgm` extension may require elevated database privileges depending on the server.

## Packages

`loadin` should be the data tool:

- API fetches.
- Raw data caching.
- PostgreSQL loading and querying.

`loadin` modules should be import-safe: importing the package must not read `.env` or create API/database clients. Credentials should be loaded only inside explicit config/client functions, and tests should prefer fake config objects or fake clients.

`setkit` should be the storytelling tool:

- Themes.
- Charts.
- Pure metrics.
- Notebook helpers.

Database access should stay out of `setkit`.

## Projects

New project folders use the standard scaffold documented in `projects/README.md`: `source/`, `notebooks/`, `figures/`, and `exports/`. Newer projects should prefer a dbt project model for the master analysis dataset.

Project folders are the journalism workbench. They should be readable and reproducible enough for collaboration, but they do not need the same test depth as `loadin`, `setkit`, or dbt.

Recommended project hygiene:

- Use `loadin.*` imports for ingestion and database access.
- Keep project scripts in the project's `source/` folder and runnable as direct commands.
- Put execution in `main()` so imports and compile checks do not trigger APIs or database writes.
- Prefer Python compile checks for project scripts.
- Keep exploratory SQL in the ignored `sql_playground/`; promote the final master query to a dbt project model.
- Prefer paired `.ipynb` and Jupytext `py:percent` `.py` files for new collaborative notebook analysis once Jupytext is configured.
- Avoid rewriting notebooks or exports unless the task specifically calls for it.

`setkit` should be developed as reusable visualizations, metrics, and helpers emerge from ongoing project work. Favor clean platform APIs over compatibility shims for old notebook imports; if an older project needs to rerun, update the project code to the current API. Existing projects do not need to be retrofitted wholesale just to use `setkit`.

Keep `docs/SetkitCatalog.md` updated when adding or changing analyst-facing `setkit` functions.

Recommended `setkit` extraction workflow:

- Build the new reusable functionality in `setkit` first.
- Check that existing project code still works unless intentionally touched.
- Prefer focused Python tests over notebook edits for validating new package elements.
- When a refactor is needed, move a small representative project chunk into a test before or alongside the notebook/script change.
- It is acceptable to validate against live PostgreSQL data using read-only queries copied from existing notebooks or project scripts. The concert analytics warehouse contains public-source analysis data, and these established read queries are allowed for realism.
- Keep database access out of `setkit` itself. Live-data validation should live in project scripts or tests that call `loadin.postgres`, not inside the `setkit` package.
- Notebook refactors are optional adoption work, not required proof that a new `setkit` element is useful.

Current lower-priority backlog:

- Bring Project 0001 up to newer project conventions.
- Clean notebook imports after package setup is stable.
- Avoid editing Project 0002 notebooks in setup-focused branches unless necessary.

## Validation Status

Current validation is incomplete.

Missing or not yet standardized:

- Full Python test coverage.
- Ruff/format commands.
- Type checking.
- Notebook execution validation.
- CI.
- A clean end-to-end reproduction command.

Until these exist, agents should inspect before changing and should report which validations were actually run.

Current lightweight Python test command:

```bash
.venv/bin/python -m pytest tests/loadin
```

The current `.venv` may need to be refreshed from `requirements.txt` before this works.
