# Taylor Swift Eras Tour

An On the Setlist project exploring Taylor Swift's Eras Tour through reproducible, data-driven analysis.

## Project Questions

The specific story and methodology are still to be defined. Likely areas of exploration include:

- How the setlist changed across tour legs, cities, and dates.
- How surprise songs were distributed and repeated.
- How each album or "era" was represented over time.
- How show length, song order, mashups, and special guests varied.
- How the tour compares with Taylor Swift's earlier tours or other large tours.

## Structure

- `source/`: project-specific API discovery and reproducible ingestion scripts.
- `notebooks/`: paired notebook and text-based analysis for exploration and visualization.
- `figures/`: generated charts and graphics.
- `exports/`: publication-ready datasets and other outputs.

API cache files and raw payloads belong in the repository-level ignored `data/` directory, not here. PostgreSQL remains the durable source of truth. Reusable database access belongs in `loadin`, warehouse transformations in dbt, and reusable analysis or visualization helpers in `setkit`.

Exploratory SQL belongs in the ignored repository-level `sql_playground/`. The final master dataset should become a Project 0003 model under `concert_analytics_dbt/models/project/` once its shape is understood.

For collaborative notebook work, prefer a paired `.ipynb` and Jupytext `py:percent` `.py` file with the same stem. The notebook preserves the interactive record and rendered output; the text file is the primary surface for agent edits and code review. Jupytext still needs to be added to the repository tooling before synchronization is automatic.

## Status

Artist discovery and interactive source ingestion are implemented. The dbt master model and notebook analysis are still to be developed.

## Artist Discovery

Search both APIs for Taylor Swift and print the candidate identifiers:

```bash
.venv/bin/python projects/0003-Taylor-Swift-Eras-Tour/source/search_artists.py
```

Pass another raw artist search string as the positional argument. Add `--raw` to inspect the complete responses returned by the current `loadin` search helpers:

```bash
.venv/bin/python projects/0003-Taylor-Swift-Eras-Tour/source/search_artists.py "Taylor Swift" --raw
```

The normal summary fetches every setlist.fm result page and orders artists by closeness to the search string: exact names first, then names with the least added material. Pagination metadata is included in the output. Requests after the first page are spaced by two seconds. `--raw` preserves the API's relevance ordering in the combined response.

Running either command contacts Spotify and setlist.fm and requires credentials for both services. Importing the module does not load credentials or make API requests.

## Source Ingestion

Run the interactive ingestion entrypoint:

```bash
.venv/bin/python projects/0003-Taylor-Swift-Eras-Tour/source/load_data.py
```

The script asks whether to preview the resulting dataframes or upsert them into PostgreSQL, whether to use a three-page setlist.fm sample or the complete setlist history, and whether to prefer existing API cache files or force a refresh.

Sample mode applies only to setlist.fm; Spotify album and track ingestion remains complete because the current Spotify helpers do not have a sample mode. Sample and full setlist responses use separate cache files.

The cache-preferred option still contacts an API when its corresponding cache file does not exist. A refresh contacts both APIs and replaces the relevant cache files. Only the explicit `load` choice opens a PostgreSQL connection and upserts the five established raw tables for `TaylorSwift`.
