"""Gaffer color constants and palette previews."""

from __future__ import annotations

from collections.abc import Mapping

COLORS = {
    "lightAmpOrange": "#FB9E50",
    "floodPink": "#F986BA",
    "setlistBlue": "#3C7DC4",
    "spotRed": "#D64848",
    "ampOrange": "#F25C05",
    "lightBlue": "#A7ECF5",
    "encorePurple": "#5D4E8C",
    "stageGreen": "#33C27D",
    "clockYellow": "#F6D357",
    "spotlightCream": "#FAF3E0",
    "gafferGrey": "#777777",
    "backstageBlack": "#1C1C1C",
}

def preview_palette(color_dict: Mapping[str, str] | None = None):
    """Preview a palette in a compact matplotlib swatch chart."""
    import matplotlib.pyplot as plt

    colors = dict(color_dict or COLORS)
    fig, ax = plt.subplots(figsize=(8, 1))
    for i, (label, color) in enumerate(colors.items()):
        ax.bar(i, 1, color=color)
        ax.text(i, 1.05, label, rotation=45, ha="right", va="bottom", fontsize=8)
    ax.axis("off")
    return fig, ax
