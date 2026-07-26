"""Label transforms."""

from __future__ import annotations

import pandas as pd


def truncate_labels(
    frame: pd.DataFrame,
    column: str,
    max_length: int = 25,
    ellipsis: str = "...",
    output_column: str | None = None,
) -> pd.DataFrame:
    """Return a copy with long string labels shortened for chart axes."""
    if max_length <= len(ellipsis):
        raise ValueError("max_length must be greater than the ellipsis length")

    result = frame.copy()
    target_column = output_column or column

    def truncate(value):
        if pd.isna(value):
            return value
        label = str(value)
        if len(label) <= max_length:
            return label
        return label[: max_length - len(ellipsis)] + ellipsis

    result[target_column] = result[column].map(truncate)
    return result
