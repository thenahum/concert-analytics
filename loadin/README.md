# loadin

Concert Analytics ingestion and data-access package.

`loadin` wraps the repository's source-data utilities for Postgres, Spotify, and setlist.fm. Its job is to fetch source data, cache API responses, normalize source-shaped records, and load/query PostgreSQL.

Warehouse bootstrap and modeled transformations belong to dbt, not `loadin`.

## Features

Postgres helpers in `loadin.postgres`:

- `get_engine()` creates a SQLAlchemy engine from Postgres environment variables.
- `load_dataframe()` loads a DataFrame into `raw.<table>`.
- `upsert_raw_table()` replaces rows in `raw.<table>` by matching `name_hint`.
- `refresh_raw_table()` deletes and reloads a raw table.
- `fetch_table()` fetches modeled tables, defaulting to `analytics_mart`.
- `run_query()` runs ad hoc SQL and returns a DataFrame.

Spotify helpers in `loadin.spotify`:

- Search for artists.
- Fetch artist albums, album tracks, album metadata, and track metadata.
- Cache raw JSON responses locally.
- Convert common Spotify responses to DataFrames.

setlist.fm helpers in `loadin.setlistfm`:

- Search artists.
- Fetch paginated setlist history.
- Cache raw JSON responses locally.
- Convert setlist responses to song-performance DataFrames.

## Configuration And Secrets

Importing `loadin` does not read `.env`.

Configuration is loaded when a function needs credentials, such as `get_engine()`, `get_spotify_client()`, or `get_setlistfm_config()`. This keeps import smoke tests and unit tests from touching secrets.

Config helpers use redacted dataclasses:

- `loadin.postgres.PostgresConfig`
- `loadin.spotify.SpotifyConfig`
- `loadin.setlistfm.SetlistFmConfig`

Tests can pass explicit config objects or fake clients instead of reading `.env`.

## Cache Directory

Cache files are local-only staging data. PostgreSQL is the durable source of truth.

Cache resolution:

1. `CA_DATA_DIR` or `LOADIN_DATA_DIR`, if set.
2. `<repo_root>/data`, when running inside this repository.
3. A platform-specific user cache directory.

## Installation

From the repository root:

```bash
pip install -e ./loadin
```

The repository-level environment is currently pinned by `requirements.txt`.

## Database Bootstrap

`loadin` assumes the `raw` schema exists before loading data. Rebuild-oriented schema and function setup lives in dbt:

```bash
inv bootstrap
```

That task runs `dbt run-operation bootstrap_database`.
