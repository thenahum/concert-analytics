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

Taylor-specific Spotify catalog choices belong in that Project 0003 master model, not in shared mart models. In particular, Taylor's Version matching should be treated as project merge policy: first identify candidate Spotify tracks for each setlist.fm song, then decide whether a Taylor's Version recording should outrank the original or a higher-popularity candidate.

For collaborative notebook work, use the paired `notebooks/eras_tour_analysis.ipynb` and Jupytext `py:percent` `notebooks/eras_tour_analysis.py` files. The notebook preserves the interactive record and rendered output; the text file is the primary surface for agent edits and code review. Jupytext is included in the repository tooling, but synchronization still needs to be run explicitly unless the local editor is configured to do it automatically. From the repository root, run `inv notebook-sync` to sync this default Project 003 pair.

## Status

Artist discovery, interactive source ingestion, the Project 003 dbt master model, and the paired analysis notebook are implemented. The first pass of scale-oriented visualizations exists, but the notebook now needs chart-by-chart refinement before publication.

Next work:

- Refine the analysis notebook one visualization at a time, starting with the Part One scale charts.
- Continue polishing chart code without embedded titles/subtitles; those are handled downstream in Canva.
- Revisit the venue geography visualization and investigate whether Plotnine can underlay a real world map beneath the venue points, or whether this chart needs a different mapping utility while preserving the repo's visual workflow.
- Keep using `inv notebook-sync` between notebook and `.py` edits, with lightweight Python validation unless notebook execution is explicitly needed.

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
