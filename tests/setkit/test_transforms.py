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


def test_counts_by_counts_unique_values_with_optional_parent_group():
    frame = pd.DataFrame(
        {
            "artist_display_name": ["Artist A", "Artist A", "Artist A", "Artist B"],
            "coachella_analytics_period": ["Before Coachella", "Before Coachella", "Coachella", "Coachella"],
            "event_id": [1, 1, 2, 3],
        }
    )

    result = transforms.counts_by(
        frame,
        by="coachella_analytics_period",
        group_by="artist_display_name",
        value_column="event_id",
        count_column="num_shows",
        category_orders={"coachella_analytics_period": ["Before Coachella", "Coachella"]},
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


def test_counts_by_counts_rows_without_parent_group():
    frame = pd.DataFrame({"album_name": ["A", "A", "B"]})

    result = transforms.counts_by(frame, by="album_name", count_column="times_played")

    assert result.to_dict("records") == [
        {"album_name": "A", "times_played": 2},
        {"album_name": "B", "times_played": 1},
    ]


def test_counts_by_can_sort_counts():
    frame = pd.DataFrame({"artist": ["A", "A", "B"], "song": ["x", "y", "x"]})

    result = transforms.counts_by(frame, by="song", group_by="artist", sort=True)

    assert result.to_dict("records") == [
        {"artist": "A", "song": "x", "count": 1},
        {"artist": "A", "song": "y", "count": 1},
        {"artist": "B", "song": "x", "count": 1},
    ]
