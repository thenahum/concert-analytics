---
name: create-project-scaffold
description: Create the next numbered On the Setlist concert-analysis project folder and its standard source, notebook, figure, and export work areas. Use when starting, scaffolding, or initializing a new story project in the Concert Analytics repository, or when bringing an empty new project folder into the current project convention.
---

# Create Project Scaffold

Create a small, reproducible project workbench without starting ingestion, changing PostgreSQL, calling APIs, or inventing a dbt model.

## Workflow

1. Read the repository `AGENTS.md` and `projects/README.md`. Treat them as authoritative if this skill differs from current repository guidance.
2. Inspect immediate child directories under `projects/`. Extract existing four-digit numeric prefixes and choose one greater than the highest prefix. Do not fill historical gaps unless the user explicitly requests a number.
3. Convert the user-provided project title to a readable hyphenated slug. Preserve intentional artist-name capitalization when practical. Form `NNNN-Project-Name` with the zero-padded project number.
4. Check whether the target path exists. If it exists or the title could map to multiple existing projects, stop and ask before overwriting or merging.
5. Create only this structure:

   ```text
   projects/NNNN-Project-Name/
   ├── README.md
   ├── source/
   │   └── .gitkeep
   ├── notebooks/
   │   └── .gitkeep
   ├── figures/
   │   └── .gitkeep
   └── exports/
       └── .gitkeep
   ```

6. Write a concise project README containing:
   - The human-readable project title and one-sentence purpose.
   - A `Research Questions` section that marks questions as provisional unless the user supplied them.
   - A `Structure` section describing the four folders.
   - A `Workflow` section recording the path from API discovery and ingestion, through exploratory SQL, the dbt master model, and notebook analysis.
   - A `Status` section stating that only the scaffold exists.
7. Verify the new tree and run `git diff --check`. Report the created path and validation results.

## Repository Boundaries

- Put project-specific Spotify and setlist.fm discovery or ingestion entrypoints in `source/`. Use `loadin` rather than duplicating reusable clients or PostgreSQL helpers.
- Keep imports safe and side effects inside `main()`. Do not contact APIs, load data, or mutate PostgreSQL while scaffolding.
- Keep raw API payloads and caches out of the project folder; they belong in the ignored repository-level `data/` area.
- Keep exploratory SQL in the ignored repository-level `sql_playground/`. Do not create a project `sql/` folder by default.
- Put the durable master query in `concert_analytics_dbt/models/project/` only after exploration establishes its shape. Do not create a placeholder dbt model during scaffolding.
- Keep project-specific analysis in `notebooks/`; promote reusable pure metrics, charts, transforms, or notebook helpers to `setkit` only when a concrete need emerges.
- Treat `figures/` and `exports/` as generated outputs. Do not create fake artifacts.

## Notebook Convention

Recommend matching `analysis.ipynb` and `analysis.py` files using Jupytext `py:percent` pairing once Jupytext is configured. The notebook preserves narrative and rendered output; the text representation is the primary agent-editing and code-review surface.

Do not create empty notebook pairs during initial scaffolding. Do not claim synchronization is automatic unless repository configuration and dependencies confirm it.

## Existing Project Updates

When asked to bring an existing project into the convention, inspect it before editing. Preserve its substantive files, avoid rewriting notebooks or generated exports without explicit approval, and report any legacy content that does not map cleanly.
