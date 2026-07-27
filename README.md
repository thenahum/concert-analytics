# Concert Analytics

Concert Analytics is the data workspace for **On the Setlist**, a reproducible data journalism project for analyzing concert performances with setlist.fm, Spotify, PostgreSQL, dbt, Python, and notebooks.

This repo is both:

- A reusable data/analytics toolkit for concert analysis.
- A working newsroom-style project space for individual stories, charts, notebooks, and exports.

## Repository Map

```text
.
├── loadin/                  # Ingestion and Postgres access package
├── setkit/                  # Storytelling, charting, and analytics helpers
├── concert_analytics_dbt/   # dbt warehouse project and bootstrap macros
├── projects/                # Article/project-specific analysis work
├── data/                    # Local-only API cache/staging files
├── sql_playground/          # Ad hoc SQL exploration
├── docs/                    # Architecture and development notes
├── tasks.py                 # Invoke task shortcuts
└── requirements.txt         # Pinned repo environment plus local packages
```

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --no-build-isolation -r requirements.txt
```

`requirements.txt` installs the pinned Python environment and editable local packages:

- `loadin`
- `setkit`

Run setup from the repository root so the editable package paths resolve correctly.

`--no-build-isolation` keeps pip from trying to resolve build dependencies separately while installing the local editable packages. The required build tooling is already pinned in `requirements.txt`.

## Configuration

Copy `.env.example` to `.env` and fill in local values for:

- setlist.fm API access
- Spotify API access
- PostgreSQL connection settings
- dbt connection settings
- optional SSH tunnel settings

Do not commit `.env` or print secret values.

## Core Workflow

Typical project flow:

1. Fetch/cache source data with `loadin`.
2. Load source-shaped tables into PostgreSQL `raw`.
3. Run dbt bootstrap after a rebuild if schemas/functions need to be recreated.
4. Run dbt models to build staging, mart, and project datasets.
5. Analyze modeled data in notebooks or Python.
6. Export project datasets and figures for publication.

Useful commands:

```bash
inv deps
inv bootstrap
inv run
inv build
inv test
inv dbt --command "run --select tag:project_002"
inv notebook-sync
inv close
```

These tasks can be stateful. Some may start SSH tunnels, touch `~/.dbt/profiles.yml`, or connect to PostgreSQL.

## Package Boundaries

`loadin` is the data tool:

- API clients.
- API response caching.
- Source-specific normalization.
- PostgreSQL query/load/upsert helpers.

`concert_analytics_dbt` is the warehouse tool:

- Rebuild bootstrap.
- `raw`, `analytics_staging`, `analytics_mart`, and `analytics_project` schemas.
- dbt staging, mart, and project models.
- database functions required by dbt models.

`setkit` is the storytelling tool:

- `gaffer`: On the Setlist visual identity, colors, fonts, and Plotnine theme helpers
- `charts`: reusable chart builders with explicit dataframe contracts
- `transforms`: reusable dataframe shaping before charts or metrics
- `export`: standard chart artifact paths and save helpers
- `notebook`: lightweight notebook setup helpers
- `metrics`: reusable pure analysis metrics, such as entropy and effective category counts, as they are promoted from project work

`projects/` is the journalism workbench. Project files should be clear and reproducible enough to collaborate on, but they do not need production-level test coverage.

See the [setkit function catalog](docs/SetkitCatalog.md) for the current analyst-facing API and examples.

## Validation

Current lightweight library test command:

```bash
.venv/bin/python -m pytest tests/loadin
```

Current focused `setkit` test command:

```bash
.venv/bin/python -m pytest tests/setkit/test_gaffer.py tests/setkit/test_export.py tests/setkit/test_transforms.py tests/setkit/test_charts.py tests/setkit/test_notebook.py
```

Current live-data `setkit` element test:

```bash
.venv/bin/python -m pytest -rs tests/setkit/new_element_test.py
```

The live element test uses read-only PostgreSQL queries from existing project analysis and writes ignored review SVGs to `tests/setkit/artifacts/`.

Project scripts usually only need compile checks unless a task calls for deeper validation:

```bash
.venv/bin/python -m py_compile projects/0001-The-Anatomy-of-a-mewithoutYou-Setlist/load_data.py
.venv/bin/python -m py_compile projects/0002-Coachella-vs-Regular-Tour/load_data.py
```

## More Documentation

- [Architecture](docs/Architecture.md)
- [Development](docs/Development.md)
- [setkit catalog](docs/SetkitCatalog.md)
- [Gaffer theme](docs/GafferTheme.md)
- [Next session handoff](docs/NextSessionHandoff.md)
- [Agent guidance](AGENTS.md)
