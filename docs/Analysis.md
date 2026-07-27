# Analysis Workflow

Concert Analytics story work usually happens in one project notebook backed by
durable warehouse models and small project-specific source scripts. The notebook
is the analytical record, not the ingestion layer or the warehouse model.

## Story Notebooks

- Use one primary notebook per story project, named for the project or story
  rather than for a single chart or article installment.
- Pair the notebook with a Jupytext `py:percent` file using the same stem, such
  as `eras_tour_analysis.ipynb` and `eras_tour_analysis.py`.
- Treat the `.ipynb` as the human reading and rendered-output surface.
- Treat the `.py` file as the collaboration, code review, search, and lightweight
  validation surface.
- Use `setkit.notebook.setup()` in the setup cell instead of hand-rolled
  `sys.path`, logging, or pandas display configuration.
- Use top-level Markdown headers inside the notebook to organize work by story
  piece, such as groundwork, deeper follow-ups, appendix checks, and discarded
  explorations.
- Keep useful analytical context in the notebook even when a chart is not ready
  for publication. Prefer moving obsolete or misleading work under a clearly
  labeled archive/scratch section over deleting context too early.

## Data Sources

- Prefer a project dbt model under `concert_analytics_dbt/models/project/` as
  the notebook's master dataset once the analysis shape is known.
- Use `loadin.postgres.run_query` or `fetch_table` from notebook cells for
  read-only warehouse access.
- Keep project-specific source discovery and ingestion scripts in `source/`.
  They should remain import-safe and should only contact APIs or PostgreSQL from
  explicit entrypoints.
- Keep exploratory SQL in the ignored repository-level `sql_playground/`.
- Do not read local API cache payloads as authoritative analysis inputs; use
  PostgreSQL or source scripts that make their cache/API behavior explicit.

## Project-Specific Modeling

- Keep reusable source and warehouse semantics in staging/mart models.
- Keep narrative-specific matching, manual track-link exceptions, special event
  windows, and artist-specific catalog policy in project models.
- Prefer tiny explicit override CTEs for project-only exceptions. Include stable
  identifiers such as `event_set_song_id` and `track_id` when possible.
- When a project exception reveals a general modeling issue, promote only the
  general rule to the shared mart layer and leave the story-specific choice in
  the project model.

## Visualization Work

- Start with readable first-pass charts that validate the data shape before
  spending time on final styling.
- Keep chart titles and subtitles out of generated chart code by default. The
  maintainer usually adds and refines those in Canva to tune wording, sizing,
  and layout for publication.
- Save generated figures under the project `figures/` directory.
- Save derived publication datasets or reference exports under `exports/`.
- Treat figures and exports as outputs, not canonical inputs.
- Promote reusable chart helpers, metrics, themes, or notebook setup utilities
  to `setkit` only when a concrete repeated need emerges.

## Code Style

- Prefer leading commas for multiline comma-separated code in any language when
  editing analysis files, SQL, and notebooks.
- Do not mechanically rewrite old code only to change comma placement. Apply the
  leading-comma style to new code and to nearby code that is already being
  edited.

## Validation

- Before notebook edits, sync the Jupytext pair.
- After editing the `.py` representation, run a Python compile check when
  possible.
- Run `inv notebook-sync` after changing either side of the default Project 003
  pair. For another notebook pair, run
  `inv notebook-sync --path=projects/NNNN-Project-Name/notebooks/analysis.ipynb`.
- During collaborative chart and cell iteration, agents should usually validate
  only the paired `.py` file and Jupytext sync. The maintainer validates the
  rendered notebook unless notebook execution or visual output review is
  explicitly requested.
- For dbt-backed notebook work, run safe dbt checks first: parse, list, and
  compile for the affected model.
- Run live dbt builds or notebook execution when the result depends on refreshed
  warehouse state or rendered outputs.
- Report which validations ran and which were skipped.
