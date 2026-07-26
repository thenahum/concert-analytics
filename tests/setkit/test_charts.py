import matplotlib

matplotlib.use("Agg")

import pandas as pd

from setkit import charts, export, gaffer


def test_horizontal_bar_can_export_with_static_fill(tmp_path):
    frame = pd.DataFrame({"song": ["A", "B"], "times_played": [2, 1]})

    plot = (
        charts.horizontal_bar(
            frame,
            category="song",
            value="times_played",
            bar_fill=gaffer.COLORS["stageGreen"],
            x_label="Song",
            y_label="Times Played",
        )
        + gaffer.theme(fig_width=4, fig_height=3)
    )

    output_path = export.chart(
        plot,
        project_name="Test",
        chart_number="001",
        viz_name="Horizontal-Bar",
        width=4,
        height=3,
        out_dir=tmp_path,
    )

    assert output_path.exists()


def test_segmented_bar_can_export_with_fill_mapping(tmp_path):
    frame = pd.DataFrame(
        {
            "artist": ["A", "A", "B"],
            "period": ["Before", "After", "Before"],
            "num_shows": [2, 1, 3],
        }
    )

    plot = (
        charts.segmented_bar(
            frame,
            category="artist",
            value="num_shows",
            segment="period",
            fill_values={"Before": gaffer.COLORS["lightBlue"], "After": gaffer.COLORS["lightAmpOrange"]},
            x_label="Artist",
            y_label="Number of Shows",
        )
        + gaffer.theme(fig_width=4, fig_height=3)
    )

    output_path = export.chart(
        plot,
        project_name="Test",
        chart_number="002",
        viz_name="Segmented-Bar",
        width=4,
        height=3,
        out_dir=tmp_path,
    )

    assert output_path.exists()
