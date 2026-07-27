# Concert Analytics Architecture

This document describes the repository as it exists today and the intended direction for cleanup. It is a living reference for humans and agents working on Concert Analytics.

## Purpose

Concert Analytics supports the "On the Setlist" data journalism workflow:

- Fetch concert and music metadata from APIs such as setlist.fm and Spotify.
- Cache API responses locally before loading them.
- Load source-shaped data into PostgreSQL.
- Transform raw tables into modeled datasets with dbt.
- Explore modeled data in Python and notebooks.
- Export reproducible datasets and figures for published analysis.

This repository is a monorepo-style data workspace rather than a centralized enterprise data platform. Project folders, packages, dbt models, notebooks, and exports intentionally live together.

## Current Repository Map

```text
.
├── loadin/                  # Ingestion and database access package
├── setkit/                  # Storytelling, charting, and analysis helpers
├── concert_analytics_dbt/   # dbt warehouse project
├── projects/                # Article/project-specific analysis work
├── data/                    # Local-only API cache/staging files
├── sql_playground/          # Ad hoc SQL exploration
├── docs/                    # Architecture and development notes
├── tasks.py                 # Invoke task shortcuts
└── requirements.txt         # Pinned repository environment
```

## Ownership Boundaries

### `loadin`

`loadin` owns data access and ingestion.

It should contain:

- API clients for setlist.fm and Spotify.
- Source response caching.
- Source-specific normalization directly tied to API responses.
- PostgreSQL connection helpers.
- Raw-table loading and upsert helpers.

It should not contain warehouse modeling logic, cross-source analytics metrics, article-specific calculations, or reusable charting code.

### dbt

`concert_analytics_dbt` owns warehouse transformation and bootstrap logic.

The modeled database convention is `analytics_<layer>`, including:

- `analytics_staging`
- `analytics_mart`
- `analytics_project`

The raw ingestion schema remains `raw`. It should be created by dbt bootstrap or dbt-adjacent bootstrap logic, not by `loadin`.

dbt should also own database prerequisites required by models, such as the `analytics_mart.similarity(...)` function currently referenced by the mart layer.

Shared mart models should stay focused on broadly reusable source and warehouse semantics. Keep deterministic, artist-agnostic rules here when they apply across catalogs, such as preferring an album track over an identically named single in `mart_all_tracks_versions`. Artist-specific catalog quirks, narrative choices, or rights-era policies should be handled in project master models instead of generalized into mart models unless they reveal a structural change needed for all setlist.fm or Spotify data.

### `setkit`

`setkit` owns storytelling support.

It should contain:

- Plotnine themes and visual style constants.
- Reusable chart builders.
- Reusable analysis helpers and pure metrics.
- Notebook convenience utilities.

Database access should stay in `loadin`. `setkit` should not duplicate Postgres connection logic.

See `docs/SetkitCatalog.md` for the current analyst-facing function catalog.

### `projects`

Project folders are the article workbench. A project can include:

- A `load_data.py` ingestion script.
- A notebook for exploration and visualization.
- SQL exploration files.
- A dbt project model for the master dataset when appropriate.
- CSV exports and figures used for publication.

Project 0002 follows the newer dbt master dataset pattern. Project 0001 predates that pattern and may remain notebook-documented until later cleanup.

Project master models are the right layer for story-specific merge policy between setlist.fm and Spotify. For example, Taylor Swift's Taylor's Version recordings should be evaluated in the Taylor project master model, where the project can decide how to rank re-recordings, originals, vault tracks, and popularity ties without changing shared mart behavior for every artist.

## Data Authority

PostgreSQL is the durable source of truth for data. The repository `data/` directory is local-only cache/staging material and should not be committed except for `.gitkeep`.

## Current Known Gaps

- Project and notebook imports still mix old top-level modules with new `loadin.*` imports.
- `setkit` is only partially implemented.
- Legacy schema bootstrap has been removed from `loadin`; dbt now has an explicit bootstrap macro.
- `analytics_mart.similarity(...)` is now represented in dbt bootstrap, but it still requires validation against a real database.
- Python tests, lint configuration, CI, and notebook validation are not yet established.
- Documentation is being introduced before the cleanup is complete; treat this file as direction plus current state, not proof that every convention is enforced.
