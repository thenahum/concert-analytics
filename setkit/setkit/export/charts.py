"""Chart export helpers."""

from __future__ import annotations

from pathlib import Path


def chart_path(
    project_name: str,
    chart_number: str = "000",
    viz_name: str = "unnamed",
    out_dir: str | Path = "viz",
    extension: str = "svg",
) -> Path:
    """Build the standard project chart export path."""
    extension = extension.lstrip(".")
    filename = f"{project_name}_{chart_number}_{viz_name}.{extension}"
    return Path(out_dir) / filename


def chart(
    plot,
    project_name: str,
    chart_number: str = "000",
    viz_name: str = "unnamed",
    width: int | float = 16,
    height: int | float = 9,
    out_dir: str | Path = "viz",
    format: str = "svg",
    dpi: int = 300,
) -> Path:
    """Save a plotnine chart using the standard project naming convention."""
    filename = chart_path(
        project_name=project_name,
        chart_number=chart_number,
        viz_name=viz_name,
        out_dir=out_dir,
        extension=format,
    )
    filename.parent.mkdir(parents=True, exist_ok=True)
    plot.save(
        filename=filename,
        format=format,
        width=width,
        height=height,
        dpi=dpi,
    )
    return filename
