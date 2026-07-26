# setkit

Concert Analytics storytelling and analysis helper package.

`setkit` is intended for reusable visualization systems, chart builders, metrics, and notebook helpers that emerge from On the Setlist project work.

Database access belongs in `loadin`, not `setkit`.

Current public subpackages:

- `setkit.gaffer`: On the Setlist visual identity.
- `setkit.charts`: reusable Plotnine chart builders.
- `setkit.transforms`: dataframe shaping helpers.
- `setkit.export`: chart artifact save paths.
- `setkit.notebook`: lightweight setup for analysis notebooks.
- `setkit.metrics`: pure reusable analysis metrics.

See `docs/SetkitCatalog.md` for the analyst-facing catalog and examples.

## Gaffer

Gaffer is the default On the Setlist visual identity. Import the namespace and
use its clean public API:

```python
from setkit import gaffer

plot = plot + gaffer.theme(fig_width=16, fig_height=9) + gaffer.source_caption()
```

## Export

Use `setkit.export` for standard project artifact paths:

```python
from setkit import export

export.chart(plot, project_name="Coachella-vs-Normal-Tour", chart_number="001", viz_name="Overview")
```

## Charts

Use `setkit.charts` for reusable plot shapes:

```python
from setkit import charts

plot = charts.segmented_bar(
    overview_df,
    category="artist_display_name",
    value="num_shows",
    segment="coachella_analytics_period",
)
```

## Transforms

Use `setkit.transforms` for reusable dataframe shaping before charts or metrics:

```python
from setkit import transforms

overview_df = transforms.counts_by(
    df,
    by="coachella_analytics_period",
    group_by="artist_display_name",
    value_column="event_id",
    count_column="num_shows",
)
```

## Notebook

Use `setkit.notebook` for lightweight notebook setup:

```python
from setkit import notebook

ctx = notebook.setup(project_name="Coachella-vs-Normal-Tour")
```

Database helpers should still be imported explicitly from `loadin`.

## Metrics

Use `setkit.metrics` for reusable notebook-side calculations that are more analytical than dataframe shaping:

```python
from setkit import metrics

tour_variety = metrics.distribution_summary(
    song_tour_prob_df,
    category="song_name",
    group_by="event_tour_id",
    weight_column="song_probability_in_tour",
    entropy_column="setlist_entropy",
    effective_count_column="effective_song_count",
)
```

Metrics stay pure: pass in dataframes, series, or scalar values; return values or dataframes; avoid database calls or project-specific assumptions.
