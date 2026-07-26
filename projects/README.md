# Project Workspace

Each numbered folder under `projects/` is the workbench for one On the Setlist story. New projects use a four-digit sequence followed by a descriptive slug, such as `0003-Taylor-Swift-Eras-Tour`.

## Standard Scaffold

```text
projects/NNNN-Project-Name/
├── README.md
├── source/
├── notebooks/
├── figures/
└── exports/
```

- `source/` contains project-specific Python entrypoints for API discovery and reproducible ingestion. Scripts should use `loadin`, keep side effects inside `main()`, and require an explicit invocation before contacting APIs or changing PostgreSQL.
- `notebooks/` contains exploratory analysis and visualization work. Prefer a paired `.ipynb` and Jupytext `py:percent` `.py` file with the same stem. The notebook preserves rich output and the exploratory record; the text representation is the primary collaboration and code-review surface.
- `figures/` contains generated publication visuals.
- `exports/` contains derived datasets or other files published as article references. These are outputs, not authoritative analysis inputs.

Exploratory SQL belongs in the ignored repository-level `sql_playground/`. Once the master dataset is understood, its durable query belongs in a project model under `concert_analytics_dbt/models/project/`.

Raw API responses and caches belong in the ignored repository-level `data/`. PostgreSQL remains the durable source of truth.

## Notebook Collaboration

For a paired notebook such as `analysis.ipynb` and `analysis.py`:

1. Sync the pair before starting work.
2. Use the `.py` file for agent edits, code review, and focused compile checks.
3. Use Jupyter for interactive execution, visual inspection, and narrative refinement.
4. Sync again after notebook work so code and Markdown changes reach both files.
5. Commit the `.ipynb` when its saved outputs are part of the analytical record.

Jupytext is the recommended pairing tool, but it is not yet included in the repository dependencies. Until it is configured, do not assume notebook and text files synchronize automatically.
