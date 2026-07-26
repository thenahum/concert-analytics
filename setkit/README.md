# setkit

Concert Analytics storytelling and analysis helper package.

`setkit` is intended for reusable visualization systems, chart builders, metrics, and notebook helpers that emerge from On the Setlist project work.

Database access belongs in `loadin`, not `setkit`.

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

## Transforms

Use `setkit.transforms` for reusable dataframe shaping before charts or metrics:

```python
from setkit import transforms

overview_df = transforms.show_counts_by_period(df, period_order=["After Coachella", "Coachella", "Before Coachella"])
```
