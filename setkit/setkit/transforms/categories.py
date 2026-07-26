"""Categorical ordering transforms."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def as_ordered_category(frame: pd.DataFrame, column: str, order: Sequence[str]) -> pd.DataFrame:
    """Return a copy with a column converted to an ordered categorical."""
    result = frame.copy()
    result[column] = pd.Categorical(result[column], categories=list(order), ordered=True)
    return result
