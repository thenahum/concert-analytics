"""Bar chart builders."""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd
from plotnine import aes, coord_flip, geom_col, ggplot, labs, scale_fill_manual


def _add_fill_scale(plot, fill_values: Mapping | None):
    if fill_values is None:
        return plot
    return plot + scale_fill_manual(values=dict(fill_values))


def horizontal_bar(
    frame: pd.DataFrame,
    category: str,
    value: str,
    fill: str | None = None,
    fill_values: Mapping | None = None,
    bar_fill: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    show_legend: bool = True,
):
    """Build a horizontal bar chart.

    Use ``fill`` and ``fill_values`` when bars should be colored by a dataframe
    column. Use ``bar_fill`` for a single static bar color.
    """
    mapping = aes(x=category, y=value, fill=fill) if fill else aes(x=category, y=value)
    kwargs = {"show_legend": show_legend}
    if fill is None and bar_fill is not None:
        kwargs["fill"] = bar_fill

    plot = ggplot(frame, mapping) + geom_col(**kwargs) + coord_flip() + labs(x=x_label, y=y_label)
    return _add_fill_scale(plot, fill_values)


def segmented_bar(
    frame: pd.DataFrame,
    category: str,
    value: str,
    segment: str,
    fill_values: Mapping | None = None,
    horizontal: bool = True,
    position: str = "stack",
    x_label: str | None = None,
    y_label: str | None = None,
    show_legend: bool = True,
):
    """Build a segmented bar chart where each bar is split by ``segment``."""
    plot = (
        ggplot(frame, aes(x=category, y=value, fill=segment))
        + geom_col(position=position, show_legend=show_legend)
        + labs(x=x_label, y=y_label)
    )
    if horizontal:
        plot = plot + coord_flip()
    return _add_fill_scale(plot, fill_values)
