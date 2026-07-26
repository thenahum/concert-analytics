# AGENTS.md

Guidance for agents working in this repository.

## Project Purpose

Concert Analytics is the data workspace for "On the Setlist": reproducible, data-driven concert analysis using setlist.fm, Spotify, PostgreSQL, dbt, Python, notebooks, and publication-ready exports.

The repository is a data journalism playground and monorepo-style workspace. Prefer clear, practical conventions over enterprise complexity.

## Repository Map

- `loadin/`: Python package for ingestion and data access.
- `setkit/`: Python package for analysis, storytelling, and visualization helpers.
- `concert_analytics_dbt/`: dbt project for warehouse bootstrap and transformations.
- `projects/`: article/project-specific scripts, notebooks, SQL, datasets, and figures.
- `data/`: local-only API cache and staging files.
- `sql_playground/`: ad hoc SQL exploration.
- `docs/`: architecture and development documentation.
- `tasks.py`: Invoke shortcuts for recurring environment/dbt/tunnel commands.

## Ownership Boundaries

`loadin` owns:

- setlist.fm and Spotify clients.
- API response caching.
- Source-specific data wrangling.
- PostgreSQL connection, query, load, and upsert helpers.

dbt owns:

- Warehouse bootstrap.
- `raw`, `analytics_staging`, `analytics_mart`, and `analytics_project` schemas.
- Staging, mart, and project models.
- Database functions required by dbt models, including the similarity function.

`setkit` owns:

- Plot themes and palettes.
- Reusable charts.
- Pure metrics.
- Notebook/storytelling helpers.

Project folders own:

- Article-specific ingestion choices.
- Exploration notebooks.
- SQL sandboxes.
- Project-specific exports and figures.

Keep database access out of `setkit`. Keep warehouse modeling out of `loadin`.

## Quality Model

Treat `loadin/`, `setkit/`, and `concert_analytics_dbt/` as production-ish library layers. They need stable APIs, import safety, meaningful tests or dbt checks, explicit validation commands, and careful agent loops.

Treat `projects/`, notebooks, and project SQL as the journalism workbench. In project folders, the agent's role is closer to staff data engineer and analytics collaborator: make the work faster, clearer, and reproducible enough without over-engineering exploratory analysis. Compile/parse checks and clear entrypoints are usually enough unless the maintainer asks for stronger validation.

`setkit` should evolve from reusable chart, metric, and notebook ideas discovered during ongoing project work. Do not rewrite old projects just to force `setkit` usage.

## Secrets And Privacy

Respect `.codexignore` and `.gitignore`.

Never read, print, summarize, or expose:

- `.env`
- credential files
- `sql_playground/.dbeaver/`
- local cache payloads unless explicitly required and safe
- API keys, passwords, tokens, SSH credentials, or connection strings

Use `.env.example` and code references to infer configuration.

If a secret-bearing file appears outside ignored paths, flag the path without repeating secret values.

## Data Rules

`data/` is local-only. PostgreSQL is the durable source of truth.

Do not commit API cache payloads. Do not treat local JSON cache files as authoritative source data.

Before changing cache behavior, check `loadin/loadin/paths.py` and existing project assumptions.

## `loadin` Validation Safety

`loadin` should stay import-safe. Importing `loadin` must not read `.env`, open database connections, create API clients, or contact external services.

Use source parsing and import smoke tests for ordinary validation. Treat calls to `get_engine()`, `get_spotify_client()`, setlist.fm fetch functions, or raw loaders as secret/database/API-touching actions unless fake config or fake clients are passed.

## Database Safety

Database tasks are stateful. Do not run ingestion, migrations, bootstrap, or destructive SQL casually.

Before running commands that may change the database, make clear what they will touch.

Do not drop schemas, truncate tables, delete rows, or kill tunnels unless the user explicitly asks or approves.

## Development Commands

Preferred setup direction:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ./loadin
pip install -e ./setkit
```

Known task shortcuts:

```bash
inv deps
inv bootstrap
inv run
inv build
inv test
inv dbt --command "run --select tag:project_002"
inv close
```

These commands are not yet fully validated as agent-safe. `tasks.py` can start SSH tunnels and can alter `~/.dbt/profiles.yml`.

Current lightweight Python test command:

```bash
.venv/bin/python -m pytest tests/loadin
```

## Current Gaps

Do not assume these are solved:

- Python tests are not established.
- Linting and formatting commands are not standardized.
- CI is not present.
- Notebook validation is not standardized.
- Project notebooks still use some legacy imports.
- Project 0002 may need to remain stable in setup-focused branches.
- dbt bootstrap for raw schema and similarity function has not yet been validated against a live database.

## Working Rules

- Inspect before changing.
- Keep edits small and scoped.
- Prefer existing patterns unless they conflict with documented boundaries.
- Use `rg` for searching.
- Do not read ignored secret/cache locations.
- Do not modify notebooks, generated files, or project exports unless the task specifically calls for it.
- For project scripts, prefer lightweight compile/import safety over production-style tests.
- Report which validations were run and which could not be run.

## Definition Of Done

A change is done when:

- It follows the ownership boundaries above.
- Imports still make sense from the monorepo environment.
- Relevant docs are updated when behavior or workflow changes.
- Safe validation has been run, or missing validation is explicitly reported.
- No secrets or local cache payloads are exposed.

## Escalation Points

Ask the maintainer before:

- Changing database bootstrap or schema names.
- Running ingestion against live APIs.
- Running commands that mutate PostgreSQL.
- Rewriting notebooks or project exports.
- Changing pinned dependencies broadly.
- Modifying SSH tunnel behavior.
- Removing legacy files or generated artifacts.
