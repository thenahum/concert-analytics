import pandas as pd
import pytest

from setkit import transforms


def test_truncate_labels_shortens_long_values_without_mutating_input():
    frame = pd.DataFrame({"song": ["short", "abcdefghijklmnopqrstuvwxyz", None]})

    result = transforms.truncate_labels(frame, "song", max_length=10)

    assert result["song"].tolist() == ["short", "abcdefg...", None]
    assert frame["song"].tolist() == ["short", "abcdefghijklmnopqrstuvwxyz", None]


def test_truncate_labels_can_write_to_output_column():
    frame = pd.DataFrame({"song": ["abcdefghijklmnopqrstuvwxyz"]})

    result = transforms.truncate_labels(frame, "song", max_length=8, output_column="song_label")

    assert result["song"].iloc[0] == "abcdefghijklmnopqrstuvwxyz"
    assert result["song_label"].iloc[0] == "abcde..."


def test_truncate_labels_rejects_too_short_max_length():
    with pytest.raises(ValueError):
        transforms.truncate_labels(pd.DataFrame({"song": ["abc"]}), "song", max_length=3)


def test_as_ordered_category_sets_requested_order():
    frame = pd.DataFrame({"period": ["Coachella", "Before Coachella"]})

    result = transforms.as_ordered_category(frame, "period", ["Before Coachella", "Coachella"])

    assert result["period"].cat.ordered
    assert list(result["period"].cat.categories) == ["Before Coachella", "Coachella"]


def test_show_counts_by_period_counts_unique_events():
    frame = pd.DataFrame(
        {
            "artist_display_name": ["Artist A", "Artist A", "Artist A", "Artist B"],
            "coachella_analytics_period": ["Before Coachella", "Before Coachella", "Coachella", "Coachella"],
            "event_id": [1, 1, 2, 3],
        }
    )

    result = transforms.show_counts_by_period(
        frame,
        period_order=["Before Coachella", "Coachella"],
    )

    assert result.to_dict("records") == [
        {
            "artist_display_name": "Artist A",
            "coachella_analytics_period": "Before Coachella",
            "num_shows": 1,
        },
        {
            "artist_display_name": "Artist A",
            "coachella_analytics_period": "Coachella",
            "num_shows": 1,
        },
        {
            "artist_display_name": "Artist B",
            "coachella_analytics_period": "Coachella",
            "num_shows": 1,
        },
    ]
    assert result["coachella_analytics_period"].cat.ordered
