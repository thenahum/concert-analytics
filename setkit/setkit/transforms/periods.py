"""Period and event-count transforms."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def as_ordered_category(frame: pd.DataFrame, column: str, order: Sequence[str]) -> pd.DataFrame:
    """Return a copy with a column converted to an ordered categorical."""
    result = frame.copy()
    result[column] = pd.Categorical(result[column], categories=list(order), ordered=True)
    return result


def show_counts_by_period(
    frame: pd.DataFrame,
    artist_column: str = "artist_display_name",
    period_column: str = "coachella_analytics_period",
    event_column: str = "event_id",
    count_column: str = "num_shows",
    period_order: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Count unique shows by artist and period."""
    result = (
        frame.groupby([artist_column, period_column])
        .agg(**{count_column: (event_column, "nunique")})
        .reset_index()
    )

    if period_order is not None:
        result = as_ordered_category(result, period_column, period_order)

    return result
