# setkit Catalog

`setkit` is the storytelling helper package for On the Setlist. It is for reusable chart style, chart builders, dataframe transforms, export paths, metrics, and notebook setup helpers that make analysis notebooks easier to write and rerun.

Database access belongs in `loadin`, not `setkit`.

## Quick Import

```python
from setkit import charts, export, gaffer, notebook, transforms
```

Design rules:

- Build clean package APIs first, then adopt them in notebooks when a project is intentionally touched.
- Do not carry stale compatibility wrappers only to keep old project imports alive.
- Use focused Python tests for package behavior; use notebooks for analysis and human review.
- Live element tests may query public-source warehouse data through `loadin.postgres`, but `setkit` itself should remain database-free.

## Gaffer

Gaffer is the default On the Setlist visual identity.

Use it when:

- You want the standard On the Setlist colors.
- You want the standard Plotnine theme.
- You need the standard Concert Analytics source caption.
- You want to preview a color palette.

Available helpers:

```python
gaffer.COLORS
gaffer.FONTS
gaffer.theme(fig_width=16, fig_height=9, panel_grid="y")
gaffer.facets()
gaffer.source_caption(["Spotify Web API"])
gaffer.preview_palette()
```

Example:

```python
plot = (
    plot
    + gaffer.theme(fig_width=16, fig_height=9, panel_grid="y")
    + gaffer.source_caption(["Spotify Web API"])
)
```

## Charts

Chart builders return Plotnine chart objects. They do not save files and do not apply Gaffer automatically.

Use them when:

- You are making a common chart shape.
- You want a consistent dataframe-to-chart contract.
- You still want to add custom Plotnine layers after the base chart is built.

### `charts.horizontal_bar`

Use for regular horizontal bar charts.

```python
plot = charts.horizontal_bar(
    frame=song_counts,
    category="track_song_label",
    value="times_played",
    bar_fill=gaffer.COLORS["stageGreen"],
    x_label="Song",
    y_label="Times Played",
)
```

### `charts.segmented_bar`

Use for stacked or segmented bars, such as show counts split by period or song frequencies split by analysis period.

```python
plot = charts.segmented_bar(
    frame=overview_df,
    category="artist_display_name",
    value="num_shows",
    segment="coachella_analytics_period",
    fill_values={
        "Before Coachella": gaffer.COLORS["lightBlue"],
        "Coachella": gaffer.COLORS["stageGreen"],
        "After Coachella": gaffer.COLORS["lightAmpOrange"],
    },
    x_label="Artist",
    y_label="Number of Shows",
)
```

## Transforms

Transforms shape dataframes before charts or metrics.

Use them when:

- You are repeatedly grouping and counting records.
- You need ordered categories for chart display.
- You need readable chart labels without mutating the original dataframe.

### `transforms.counts_by`

Use for count tables by one or more dimensions. This covers patterns like counts by song, counts by album, counts by period, and counts by song within each artist.

```python
song_counts = transforms.counts_by(
    df,
    by="track_song_name",
    group_by=["artist_name_hint", "coachella_analytics_period"],
    value_column="event_set_song_id",
    count_column="frequency",
)
```

For a single-dimension count:

```python
album_counts = transforms.counts_by(
    df,
    by="album_name",
    count_column="times_played",
)
```

### `transforms.as_ordered_category`

Use when chart order matters.

```python
overview_df = transforms.as_ordered_category(
    overview_df,
    "coachella_analytics_period",
    ["After Coachella", "Coachella", "Before Coachella"],
)
```

### `transforms.truncate_labels`

Use for chart axis labels that get too long.

```python
song_counts = transforms.truncate_labels(
    song_counts,
    "track_song_name",
    max_length=25,
    output_column="track_song_label",
)
```

## Export

Export helpers save project artifacts with standard naming.

Use them when:

- You want chart filenames to follow the project convention.
- You want the output directory created automatically.
- You want tests or scripts to receive the saved `Path`.

```python
path = export.chart(
    plot,
    project_name="Coachella-vs-Normal-Tour",
    chart_number="002",
    viz_name="BillieEilish-Song-Breakout",
    width=9,
    height=12,
)
```

This writes:

```text
viz/Coachella-vs-Normal-Tour_002_BillieEilish-Song-Breakout.svg
```

## Metrics

Metrics are the next planned `setkit` area.

Use them when:

- A calculation is reused across projects.
- The result is analytical rather than just dataframe reshaping for one chart.
- The calculation should not live permanently in a project-specific master analysis table.

Candidate metrics from the current project review:

- Setlist entropy or effective setlist size.
- Era, album, or period representation by show or tour.
- Song-level concentration and repeat-rate summaries.
- Before/after deltas for project-defined periods.

Metric functions should be pure: accept dataframes, series, or scalar values and return values or dataframes. They should not query PostgreSQL or import project notebooks.

## Notebook

Notebook helpers handle lightweight setup only.

Use them when:

- You want to add the repository root to `sys.path`.
- You want standard logging setup.
- You want pandas display options configured.
- You want a small context object with `project_root` and `project_name`.

```python
ctx = notebook.setup(project_name="Coachella-vs-Normal-Tour")
```

Keep database imports explicit:

```python
from loadin.postgres import fetch_table, run_query
```

## Current Live Element Tests

The current live-data element test is:

```text
tests/setkit/new_element_test.py
```

It uses Project 002 data to build review SVGs in:

```text
tests/setkit/artifacts/
```

These SVGs are intentionally ignored by git and are meant for human visual review.
