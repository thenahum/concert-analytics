# setkit Catalog

`setkit` is the storytelling helper package for On the Setlist. It is for reusable chart style, chart builders, dataframe transforms, export paths, metrics, and notebook setup helpers that make analysis notebooks easier to write and rerun.

Database access belongs in `loadin`, not `setkit`.

## Quick Import

```python
from setkit import charts, export, gaffer, metrics, notebook, transforms
```

Design rules:

- Build clean package APIs first, then adopt them in notebooks when a project is intentionally touched.
- Do not carry stale compatibility wrappers only to keep old project imports alive.
- Use focused Python tests for package behavior; use notebooks for analysis and human review.
- Live element tests may query public-source warehouse data through `loadin.postgres`, but `setkit` itself should remain database-free.

## Contents

- [Gaffer](#gaffer)
- [Charts](#charts)
  - [`charts.horizontal_bar`](#horizontal-bar)
  - [`charts.segmented_bar`](#segmented-bar)
- [Transforms](#transforms)
  - [`transforms.counts_by`](#counts-by)
  - [`transforms.as_ordered_category`](#ordered-category)
  - [`transforms.truncate_labels`](#truncate-labels)
- [Export](#export)
- [Metrics](#metrics)
  - [`metrics.entropy`](#entropy)
  - [`metrics.effective_count`](#effective-count)
  - [`metrics.distribution_summary`](#distribution-summary)
- [Notebook](#notebook)
- [Current Live Element Tests](#current-live-element-tests)

## Gaffer

Gaffer is the default On the Setlist visual identity.

For the full visual philosophy, color palette, and font guidance, see
[Gaffer Theme](GafferTheme.md).

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

What you need prepared:

| Helper | Required input | Notes |
| --- | --- | --- |
| `gaffer.COLORS` | Nothing | Dictionary of named brand colors. |
| `gaffer.FONTS` | Nothing | Dictionary of preferred font family names. |
| `gaffer.theme(...)` | Nothing | Returns a Plotnine theme object to add to a chart. |
| `gaffer.facets()` | Nothing | Returns facet styling for Plotnine charts. |
| `gaffer.source_caption(additional_sources=...)` | Optional list of source names | Always includes `setlist.fm`; pass extra sources like `["Spotify Web API"]`. |
| `gaffer.preview_palette()` | Nothing | Returns a small palette preview chart. |

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

<a id="horizontal-bar"></a>

### `charts.horizontal_bar`

Use for regular horizontal bar charts.

What you need prepared:

| Argument | Required? | Expected shape |
| --- | --- | --- |
| `frame` | Yes | A pandas dataframe with one row per bar. |
| `category` | Yes | Name of the column containing bar labels. |
| `value` | Yes | Name of the numeric column containing bar lengths. |
| `fill` | No | Name of a categorical color column, if bars are colored by data. |
| `fill_values` | No | Mapping from values in `fill` to color strings. |
| `bar_fill` | No | Single color string when all bars use the same color. |

Returns a Plotnine chart. It does not sort, count, save, or apply `gaffer.theme`;
prepare those separately with `transforms` and `export`.

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

<a id="segmented-bar"></a>

### `charts.segmented_bar`

Use for stacked or segmented bars, such as show counts split by period or song frequencies split by analysis period.

What you need prepared:

| Argument | Required? | Expected shape |
| --- | --- | --- |
| `frame` | Yes | A pandas dataframe with one row per category and segment combination. |
| `category` | Yes | Name of the column containing bar labels. |
| `value` | Yes | Name of the numeric column containing segment sizes. |
| `segment` | Yes | Name of the categorical column used to split each bar. |
| `fill_values` | No | Mapping from values in `segment` to color strings. |

Returns a Plotnine chart. If each category has multiple segments, prepare the
data so each segment has its own row, usually with `transforms.counts_by`.

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

<a id="counts-by"></a>

### `transforms.counts_by`

Use for count tables by one or more dimensions. This covers patterns like counts by song, counts by album, counts by period, and counts by song within each artist.

What you need prepared:

| Argument | Required? | Expected shape |
| --- | --- | --- |
| `frame` | Yes | A pandas dataframe with the dimensions you want to count. |
| `by` | Yes | Column name, or list of column names, for the counted dimension. |
| `group_by` | No | Parent grouping column name, or list of names, such as artist, tour, or period. |
| `value_column` | No | Column to count within each group. When omitted, rows are counted. |
| `distinct` | No | When `value_column` is provided, distinct values are counted by default. |
| `category_orders` | No | Mapping of column name to desired categorical order. |

Returns a dataframe with the grouping columns plus `count_column`. It does not
change the input dataframe.

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

<a id="ordered-category"></a>

### `transforms.as_ordered_category`

Use when chart order matters.

What you need prepared:

| Argument | Required? | Expected shape |
| --- | --- | --- |
| `frame` | Yes | A pandas dataframe containing the column to order. |
| `column` | Yes | Column name to convert into an ordered pandas categorical. |
| `order` | Yes | Ordered list of expected display values. |

Returns a copy of the dataframe with `column` converted to an ordered category.
Values not included in `order` become missing categorical values.

```python
overview_df = transforms.as_ordered_category(
    overview_df,
    "coachella_analytics_period",
    ["After Coachella", "Coachella", "Before Coachella"],
)
```

<a id="truncate-labels"></a>

### `transforms.truncate_labels`

Use for chart axis labels that get too long.

What you need prepared:

| Argument | Required? | Expected shape |
| --- | --- | --- |
| `frame` | Yes | A pandas dataframe containing the text column. |
| `column` | Yes | Column name containing labels to shorten. |
| `max_length` | No | Maximum output label length, including the ellipsis. Must be greater than 3. |
| `output_column` | No | Destination column. When omitted, the original column name is reused in the returned copy. |

Returns a copy of the dataframe. Missing values stay missing.

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

What you need prepared:

| Argument | Required? | Expected shape |
| --- | --- | --- |
| `plot` | Yes | A Plotnine chart object, usually after adding theme/caption layers. |
| `project_name` | Yes | Short project slug used as the filename prefix. |
| `chart_number` | Yes | Chart sequence string, such as `"001"`. |
| `viz_name` | Yes | Short chart slug used in the filename. |
| `width`, `height` | No | Export dimensions in inches. |
| `out_dir` | No | Output directory. Defaults to `viz`. |
| `format` | No | File extension/format, currently usually `svg`. |

Returns a `Path` to the written file and creates the output directory if needed.

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

Metrics are pure analysis functions for reusable calculations that are more
analytical than dataframe reshaping and more ad hoc than warehouse modeling.

Use them when:

- A calculation is reused across projects.
- The result is analytical rather than just dataframe reshaping for one chart.
- The calculation should not live permanently in a project-specific master analysis table.
- You want notebook-side data science helpers that operate on any dataframe.

Do not use them for stable warehouse metrics that should be available to every
project model. Those belong in dbt models, macros, or database functions.

<a id="entropy"></a>

### `metrics.entropy`

Use for Shannon entropy on counts, weights, or probabilities. This is useful for
measuring how concentrated or varied a song, album, era, or period distribution
is.

What you need prepared:

| Argument | Required? | Expected shape |
| --- | --- | --- |
| `values` | Yes | A sequence, pandas Series, or numpy array of non-negative counts, weights, or probabilities. |
| `base` | No | Log base. Defaults to `2`, so results are measured in bits. |

Input values do not need to be pre-normalized. Missing values are ignored. Empty
or all-zero inputs return `0.0`.

```python
setlist_entropy = metrics.entropy(song_tour_prob_df["song_probability_in_tour"])
```

<a id="effective-count"></a>

### `metrics.effective_count`

Use to convert entropy into a count-like value. For example, an effective song
count of 10 means the distribution is as varied as 10 evenly represented songs.

What you need prepared:

| Argument | Required? | Expected shape |
| --- | --- | --- |
| `values` | Yes | Same as `metrics.entropy`: non-negative counts, weights, or probabilities. |
| `base` | No | Must match the entropy base. Defaults to `2`. |

Input values do not need to be pre-normalized. The result is a float, because
real-world distributions are rarely exactly equivalent to a whole number of
even categories.

```python
effective_song_count = metrics.effective_count(
    song_tour_prob_df["song_probability_in_tour"]
)
```

<a id="distribution-summary"></a>

### `metrics.distribution_summary`

Use for grouped concentration summaries, such as tour-level setlist variety or
show-level album/era balance.

What you need prepared:

| Argument | Required? | Expected shape |
| --- | --- | --- |
| `frame` | Yes | A pandas dataframe with one row per observed item or precomputed category weight. |
| `category` | Yes | Column containing the category whose balance you want to measure, such as song, album, era, or period. |
| `group_by` | No | Column name, or list of names, defining each distribution to summarize. |
| `weight_column` | No | Numeric column containing counts, weights, or probabilities. When omitted, rows are counted. |
| `entropy_column` | No | Output column name for entropy. |
| `effective_count_column` | No | Output column name for effective count. |
| `total_weight_column` | No | Output column name for the summed row count or summed weight. |
| `category_count_column` | No | Output column name for the number of observed categories. |
| `base` | No | Log base used by entropy and effective count. Defaults to `2`. |

Returns one row per group, or one row total when `group_by` is omitted. Output
includes entropy, effective count, total weight, and category count.

```python
tour_variety = metrics.distribution_summary(
    song_tour_prob_df,
    category="song_name",
    group_by=["event_tour_id", "event_tour"],
    weight_column="song_probability_in_tour",
    entropy_column="setlist_entropy",
    effective_count_column="effective_song_count",
)
```

Possible next metrics from the current project review:

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
- You want a small context object with the repository root and `project_name`.

What you need prepared:

| Helper | Required input | Notes |
| --- | --- | --- |
| `notebook.find_project_root(start=...)` | A path inside the repo, or nothing to use the current working directory | Looks upward for repository markers like `.agents` or `.git`. |
| `notebook.add_project_root(...)` | Optional root or start path | Adds the repo root to `sys.path` once. |
| `notebook.configure_logging(...)` | Optional log level | Calls Python logging setup. |
| `notebook.configure_pandas(...)` | Optional display limits | Sets pandas display options. |
| `notebook.setup(project_name=...)` | Optional project name | Runs the common setup steps and returns a context object. |

These helpers do not import database utilities or read secrets.

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
