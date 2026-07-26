"""Plotnine theme helpers for the Gaffer visual identity."""

from __future__ import annotations

from collections.abc import Iterable

from plotnine import (
    element_blank,
    element_line,
    element_rect,
    element_text,
    labs,
    theme as plotnine_theme,
)

from .colors import COLORS
from .fonts import FONTS


def source_caption(additional_sources: Iterable[str] | None = None):
    """Return the standard Concert Analytics source caption."""
    sources = ["setlist.fm"]
    if additional_sources:
        sources.extend(additional_sources)

    return labs(caption=f"Source: {', '.join(sources)} sourced via Concert Analytics")


def theme(fig_width: int | float = 9, fig_height: int | float = 16, panel_grid: str = "x"):
    """Return the standard Gaffer plotnine theme.

    Parameters
    ----------
    fig_width, fig_height:
        Plot dimensions in inches.
    panel_grid:
        Which major grid lines to show: ``"x"``, ``"y"``, ``"both"``, or ``"none"``.
    """
    if panel_grid not in {"x", "y", "both", "none"}:
        raise ValueError('panel_grid must be one of "x", "y", "both", or "none"')

    grid_line = element_line(
        color=COLORS["gafferGrey"],
        linetype="dashed",
        size=0.5,
    )

    panel_grid_y = grid_line if panel_grid in ("y", "both") else element_blank()
    panel_grid_x = grid_line if panel_grid in ("x", "both") else element_blank()

    return plotnine_theme(
        figure_size=(fig_width, fig_height),
        plot_background=element_rect(fill=COLORS["spotlightCream"], color=None),
        panel_background=element_rect(fill=COLORS["spotlightCream"], color=None),
        panel_border=element_blank(),
        plot_margin_top=0.03,
        plot_margin_bottom=0.025,
        plot_margin_right=0.03,
        plot_margin_left=0.03,
        plot_title=element_blank(),
        plot_subtitle=element_blank(),
        plot_caption=element_text(
            family=FONTS["axis"],
            size=12,
            color=COLORS["gafferGrey"],
            ha="right",
            margin={"t": 30},
        ),
        axis_title=element_text(
            family=FONTS["axis"],
            size=12,
            color=COLORS["gafferGrey"],
            weight="ultralight",
        ),
        axis_text=element_text(
            family=FONTS["axis"],
            size=12,
            color=COLORS["gafferGrey"],
        ),
        axis_title_y=element_blank(),
        axis_ticks=element_line(color=COLORS["spotlightCream"]),
        axis_ticks_minor=element_blank(),
        panel_grid_major_y=panel_grid_y,
        panel_grid_major_x=panel_grid_x,
        panel_grid_minor=element_blank(),
        legend_title=element_blank(),
        legend_background=element_blank(),
        legend_key=element_blank(),
        legend_key_width=10,
        legend_position="top",
        legend_margin=1,
        legend_direction="vertical",
    )


def facets():
    """Return the standard Gaffer facet styling preset."""
    return plotnine_theme(
        strip_text=element_text(
            size=12,
            family=FONTS["axis"],
            color=COLORS["backstageBlack"],
        ),
        strip_background=element_blank(),
        axis_title_x=element_blank(),
    )
