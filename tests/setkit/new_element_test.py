from pathlib import Path

import pytest

import matplotlib

matplotlib.use("Agg")

from loadin.postgres import run_query
from setkit import charts, export, gaffer, transforms


PROJECT_002_MASTER_QUERY = """
select
    artist_display_name,
    artist_name_hint,
    coachella_analytics_period,
    event_id,
    event_set_song_id,
    track_song_name
from
    analytics_project.project_002_coachella_master_setlist_data
"""

REVIEW_ARTIFACT_DIR = Path("tests/setkit/artifacts")


def _project_002_master_data():
    try:
        return run_query(PROJECT_002_MASTER_QUERY)
    except Exception as exc:
        pytest.skip(f"Live project database unavailable: {exc}")


def test_gaffer_and_export_work_together_on_project_002_overview_chart(tmp_path):
    df = _project_002_master_data()

    period_order = ["After Coachella", "Coachella", "Before Coachella"]
    overview_df = transforms.counts_by(
        df,
        by="coachella_analytics_period",
        group_by="artist_display_name",
        value_column="event_id",
        count_column="num_shows",
        category_orders={"coachella_analytics_period": period_order},
    )

    period_colors = {
        "Before Coachella": gaffer.COLORS["lightBlue"],
        "Coachella": gaffer.COLORS["stageGreen"],
        "After Coachella": gaffer.COLORS["lightAmpOrange"],
    }
    plot = (
        charts.segmented_bar(
            overview_df,
            category="artist_display_name",
            value="num_shows",
            segment="coachella_analytics_period",
            fill_values=period_colors,
            x_label="Artist",
            y_label="Number of Shows",
        )
        + gaffer.theme(fig_width=16, fig_height=9, panel_grid="y")
        + gaffer.source_caption()
    )

    output_path = export.chart(
        plot,
        project_name="Coachella-vs-Normal-Tour",
        chart_number="001",
        viz_name="Overview-of-Shows",
        width=16,
        height=9,
        out_dir=tmp_path / "viz",
    )

    assert not overview_df.empty
    assert output_path.exists()
    assert output_path.name == "Coachella-vs-Normal-Tour_001_Overview-of-Shows.svg"
    assert output_path.read_text().lstrip().startswith("<?xml")

    review_path = export.chart(
        plot,
        project_name="Coachella-vs-Normal-Tour",
        chart_number="001",
        viz_name="Overview-of-Shows",
        width=16,
        height=9,
        out_dir=REVIEW_ARTIFACT_DIR,
    )

    assert review_path.exists()


def test_charts_transforms_and_export_build_project_002_song_breakout(tmp_path):
    df = _project_002_master_data()

    period_order = ["After Coachella", "Coachella", "Before Coachella"]
    song_counts = transforms.counts_by(
        df,
        by="track_song_name",
        group_by=["artist_name_hint", "coachella_analytics_period"],
        value_column="event_set_song_id",
        count_column="frequency",
        category_orders={"coachella_analytics_period": period_order},
    )

    artist = (
        song_counts.groupby("artist_name_hint")["frequency"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )
    artist_song_counts = song_counts[song_counts["artist_name_hint"] == artist].reset_index(drop=True)

    artist_song_counts = transforms.truncate_labels(
        artist_song_counts,
        "track_song_name",
        max_length=14,
        output_column="track_song_label",
    )

    label_order = (
        artist_song_counts.groupby("track_song_label")["frequency"]
        .sum()
        .sort_values(ascending=True)
        .index
        .tolist()
    )
    artist_song_counts = transforms.as_ordered_category(artist_song_counts, "track_song_label", label_order)

    period_colors = {
        "Before Coachella": gaffer.COLORS["lightBlue"],
        "Coachella": gaffer.COLORS["stageGreen"],
        "After Coachella": gaffer.COLORS["lightAmpOrange"],
    }
    plot = (
        charts.segmented_bar(
            artist_song_counts,
            category="track_song_label",
            value="frequency",
            segment="coachella_analytics_period",
            fill_values=period_colors,
            x_label="Song Name",
            y_label="Song Frequency",
        )
        + gaffer.theme(fig_width=9, fig_height=12)
        + gaffer.source_caption()
    )

    output_path = export.chart(
        plot,
        project_name="Coachella-vs-Normal-Tour",
        chart_number="002",
        viz_name=f"{artist}-Song-Breakout",
        width=9,
        height=12,
        out_dir=tmp_path / "viz",
    )
    review_path = export.chart(
        plot,
        project_name="Coachella-vs-Normal-Tour",
        chart_number="002",
        viz_name=f"{artist}-Song-Breakout",
        width=9,
        height=12,
        out_dir=REVIEW_ARTIFACT_DIR,
    )

    assert not artist_song_counts.empty
    assert artist_song_counts["track_song_label"].astype(str).str.contains(r"\.\.\.").any()
    assert output_path.exists()
    assert review_path.exists()
