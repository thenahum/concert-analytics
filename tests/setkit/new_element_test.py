from pathlib import Path

import pytest

import matplotlib

matplotlib.use("Agg")

from plotnine import aes, coord_flip, geom_col, ggplot, labs, scale_fill_manual

from loadin.postgres import run_query
from setkit import export, gaffer, transforms


PROJECT_002_MASTER_QUERY = """
select
    artist_display_name,
    coachella_analytics_period,
    event_id
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
    overview_df = transforms.show_counts_by_period(
        df,
        period_order=period_order,
    )

    plot = (
        ggplot(overview_df, aes(x="artist_display_name", y="num_shows", fill="coachella_analytics_period"))
        + geom_col(position="stack")
        + coord_flip()
        + scale_fill_manual(
            values={
                "Before Coachella": gaffer.COLORS["lightBlue"],
                "Coachella": gaffer.COLORS["stageGreen"],
                "After Coachella": gaffer.COLORS["lightAmpOrange"],
            }
        )
        + labs(x="Artist", y="Number of Shows")
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
