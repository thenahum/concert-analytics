"""Reusable count transforms."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pandas as pd

from .categories import as_ordered_category


def _as_list(value: str | Sequence[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def counts_by(
    frame: pd.DataFrame,
    by: str | Sequence[str],
    group_by: str | Sequence[str] | None = None,
    value_column: str | None = None,
    count_column: str = "count",
    distinct: bool = True,
    category_orders: Mapping[str, Sequence[str]] | None = None,
    sort: bool = False,
    ascending: bool = False,
) -> pd.DataFrame:
    """Count rows or values by one or more dimensions.

    Parameters
    ----------
    by:
        Dimension column or columns to count by, such as song, album, or period.
    group_by:
        Optional parent grouping column or columns, such as artist.
    value_column:
        Optional value to count. When omitted, rows are counted.
    distinct:
        When ``value_column`` is provided, count distinct values by default.
    category_orders:
        Optional mapping of column name to explicit categorical order.
    sort:
        Whether to sort by the count column.
    """
    dimensions = _as_list(group_by) + _as_list(by)
    grouped = frame.groupby(dimensions)

    if value_column is None:
        result = grouped.size().reset_index(name=count_column)
    else:
        agg_func = "nunique" if distinct else "count"
        result = grouped.agg(**{count_column: (value_column, agg_func)}).reset_index()

    for column, order in (category_orders or {}).items():
        result = as_ordered_category(result, column, order)

    if sort:
        result = result.sort_values(count_column, ascending=ascending).reset_index(drop=True)

    return result
