"""Distribution and concentration metrics."""

from __future__ import annotations

from collections.abc import Sequence
import math

import numpy as np
import pandas as pd


def _as_list(value: str | Sequence[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _probabilities(values: Sequence[float] | pd.Series | np.ndarray) -> np.ndarray:
    series = pd.Series(values, dtype="float64").dropna()
    if series.empty:
        return np.array([], dtype="float64")
    if (series < 0).any():
        raise ValueError("entropy values must be non-negative")

    total = float(series.sum())
    if total == 0:
        return np.array([], dtype="float64")

    return (series / total).to_numpy(dtype="float64")


def entropy(values: Sequence[float] | pd.Series | np.ndarray, base: float = 2) -> float:
    """Calculate Shannon entropy for counts, weights, or probabilities.

    Values are normalized before entropy is calculated, so callers can pass raw
    counts, play probabilities, or weighted shares.
    """
    if base <= 0 or base == 1:
        raise ValueError("base must be positive and not equal to 1")

    probabilities = _probabilities(values)
    if probabilities.size == 0:
        return 0.0
    probabilities = probabilities[probabilities > 0]

    return float(-np.sum(probabilities * np.log(probabilities)) / math.log(base))


def effective_count(values: Sequence[float] | pd.Series | np.ndarray, base: float = 2) -> float:
    """Return the effective number of equally represented categories.

    This is entropy converted back into a count-like value. For example, a tour
    with an effective song count of 10 is as varied as 10 evenly represented
    songs, even if the real song catalog is larger.
    """
    return float(base ** entropy(values, base=base))


def distribution_summary(
    frame: pd.DataFrame,
    category: str,
    group_by: str | Sequence[str] | None = None,
    weight_column: str | None = None,
    entropy_column: str = "entropy",
    effective_count_column: str = "effective_count",
    total_weight_column: str = "total_weight",
    category_count_column: str = "category_count",
    base: float = 2,
) -> pd.DataFrame:
    """Summarize category concentration within each optional group.

    Use this for questions such as "how varied was each tour's setlist?" or
    "how balanced was album/era representation in each show?".
    """
    group_columns = _as_list(group_by)
    dimensions = group_columns + [category]

    if weight_column is None:
        category_weights = frame.groupby(dimensions, dropna=False).size().reset_index(name="_weight")
    else:
        category_weights = (
            frame.groupby(dimensions, dropna=False)[weight_column]
            .sum()
            .reset_index(name="_weight")
        )

    if not group_columns:
        values = category_weights["_weight"]
        return pd.DataFrame(
            [
                {
                    entropy_column: entropy(values, base=base),
                    effective_count_column: effective_count(values, base=base),
                    total_weight_column: values.sum(),
                    category_count_column: category_weights[category].nunique(dropna=False),
                }
            ]
        )

    rows = []
    for group_key, group in category_weights.groupby(group_columns, dropna=False):
        key_values = group_key if isinstance(group_key, tuple) else (group_key,)
        values = group["_weight"]
        row = dict(zip(group_columns, key_values, strict=True))
        row.update(
            {
                entropy_column: entropy(values, base=base),
                effective_count_column: effective_count(values, base=base),
                total_weight_column: values.sum(),
                category_count_column: group[category].nunique(dropna=False),
            }
        )
        rows.append(row)

    return pd.DataFrame(rows)
