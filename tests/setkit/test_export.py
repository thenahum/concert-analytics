from pathlib import Path

from setkit import export


class FakePlot:
    def __init__(self):
        self.save_kwargs = None

    def save(self, **kwargs):
        self.save_kwargs = kwargs


def test_chart_path_uses_project_convention():
    path = export.chart_path(
        project_name="Coachella-vs-Normal-Tour",
        chart_number="002",
        viz_name="Overview-Of-Songs",
    )

    assert path == Path("viz/Coachella-vs-Normal-Tour_002_Overview-Of-Songs.svg")


def test_chart_saves_plot_and_returns_path(tmp_path):
    plot = FakePlot()

    path = export.chart(
        plot,
        project_name="Project",
        chart_number="001",
        viz_name="Chart",
        width=9,
        height=12,
        out_dir=tmp_path / "viz",
    )

    assert path == tmp_path / "viz" / "Project_001_Chart.svg"
    assert path.parent.exists()
    assert plot.save_kwargs == {
        "filename": path,
        "format": "svg",
        "width": 9,
        "height": 12,
        "dpi": 300,
    }
