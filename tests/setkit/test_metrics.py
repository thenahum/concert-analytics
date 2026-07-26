import math

import pandas as pd
import pytest

from setkit import metrics


def test_entropy_accepts_counts_and_returns_bits():
    assert metrics.entropy([1, 1, 1, 1]) == pytest.approx(2.0)
    assert metrics.entropy([4, 0, 0, 0]) == pytest.approx(0.0)


def test_effective_count_converts_entropy_to_count_like_value():
    assert metrics.effective_count([10, 10, 10, 10]) == pytest.approx(4.0)
    assert metrics.effective_count([3, 1]) == pytest.approx(1.754765, rel=1e-5)


def test_entropy_rejects_negative_values_and_invalid_base():
    with pytest.raises(ValueError):
        metrics.entropy([1, -1])
    with pytest.raises(ValueError):
        metrics.entropy([1, 1], base=1)


def test_distribution_summary_counts_category_balance_by_group():
    frame = pd.DataFrame(
        {
            "tour": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "song": ["x", "x", "y", "z", "x", "x", "x", "y"],
        }
    )

    result = metrics.distribution_summary(frame, category="song", group_by="tour").sort_values("tour")

    assert result.to_dict("records") == [
        {
            "tour": "A",
            "entropy": pytest.approx(1.5),
            "effective_count": pytest.approx(math.sqrt(8)),
            "total_weight": 4,
            "category_count": 3,
        },
        {
            "tour": "B",
            "entropy": pytest.approx(0.811278, rel=1e-5),
            "effective_count": pytest.approx(1.754765, rel=1e-5),
            "total_weight": 4,
            "category_count": 2,
        },
    ]


def test_distribution_summary_can_use_precomputed_weights():
    frame = pd.DataFrame(
        {
            "tour": ["A", "A", "A"],
            "song": ["x", "y", "z"],
            "song_probability_in_tour": [0.5, 0.25, 0.25],
        }
    )

    result = metrics.distribution_summary(
        frame,
        category="song",
        group_by="tour",
        weight_column="song_probability_in_tour",
        entropy_column="setlist_entropy",
        effective_count_column="effective_song_count",
    )

    assert result.loc[0, "setlist_entropy"] == pytest.approx(1.5)
    assert result.loc[0, "effective_song_count"] == pytest.approx(math.sqrt(8))
    assert result.loc[0, "total_weight"] == pytest.approx(1.0)
