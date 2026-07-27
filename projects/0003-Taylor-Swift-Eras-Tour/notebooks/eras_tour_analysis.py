# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: .venv (3.13.2)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Taylor Swift Eras Tour Analysis
#
# Groundwork notebook for the first Project 0003 story: the Eras Tour as a
# calendar, geography, tour-scale, and album-representation object.

# %% [markdown]
# ## Setup

# %%
import pandas as pd
from plotnine import (
    aes,
    geom_col,
    geom_line,
    geom_point,
    ggplot,
    labs,
    scale_color_manual,
    scale_fill_manual,
    scale_size,
    scale_x_date,
    theme,
    element_text,
    element_blank
)

from loadin.postgres import run_query
from setkit import export, gaffer, notebook


PROJECT_NAME = "Taylor-Swift-Eras-Tour"
ctx = notebook.setup(project_name=PROJECT_NAME)
PROJECT_DIR = ctx.project_root / "projects" / "0003-Taylor-Swift-Eras-Tour"
FIGURES_DIR = PROJECT_DIR / "figures"
MASTER_TABLE = "analytics_project.project_003_eras_tour_master_setlist_data"

# %% [markdown]
# ## Load Master Data
#
# This reads the Project 003 dbt model. If this cell fails because the relation
# does not exist, build the model first with:
#
# ```bash
# inv dbt --command "run --select tag:project_003"
# ```

# %%
master_query = f"""
select
    *
from
    {MASTER_TABLE}
"""

df = run_query(master_query)
df["event_date"] = pd.to_datetime(df["event_date"])

df.shape

df.head(10)

# %%
summary = {
    "shows": df["event_id"].nunique(),
    "song_performances": len(df),
    "unique_songs": df["track_song_name"].nunique(),
    "unique_track_matches": df["track_id"].nunique(),
    "venues": df["venue_id"].nunique(),
    "countries": df["venue_country_code"].nunique(),
    "first_show": df["event_date"].min().date(),
    "last_show": df["event_date"].max().date(),
    "max_songs_in_show": int(df["event_total_songs"].max()),
}

summary

# %% [markdown]
# ## Part One: SCALE
#
# Vizualizations showing the full scale of the events

# %% [markdown]
# ### 001. Shows Per Month
#
# One row per month, with the total tracked shows in that month.

# %%
show_summary = (
    df.groupby(
        [
            "event_id",
            "event_date",
            "event_tour",
            "venue_name",
            "venue_city",
            "venue_state_code",
            "venue_country_code",
        ],
        dropna=False,
    )
    .agg(
        total_songs=("event_set_song_id", "count"),
        total_sets=("event_total_sets", "max"),
        encore_songs=("event_total_encore_songs", "max"),
    )
    .reset_index()
    .sort_values("event_date")
)

monthly_show_summary = (
    show_summary.assign(month_start=lambda frame: frame["event_date"].dt.to_period("M").dt.to_timestamp())
    .groupby("month_start", as_index=False)
    .agg(
        total_shows=("event_id", "nunique"),
        total_song_performances=("total_songs", "sum"),
    )
)

monthly_timeline_plot = (
    ggplot(monthly_show_summary, aes("month_start", "total_shows"))
    + geom_col(fill=gaffer.COLORS["setlistBlue"], width=24)
    + scale_x_date(date_breaks="2 month", date_labels="%b-%y")
    + labs(
        x=None,
        y="Tracked shows",
    )
    + gaffer.source_caption()
    + gaffer.theme(fig_width=16, fig_height=9, panel_grid="y")
    + theme(
        axis_text_x=element_text(size=12)
        , axis_title_x=element_blank()
    )
)

monthly_timeline_plot

# %%
export.chart(
    monthly_timeline_plot,
    project_name=PROJECT_NAME,
    chart_number="001",
    viz_name="Shows-Per-Month",
    out_dir=FIGURES_DIR,
    width=16,
    height=9,
)

# %% [markdown]
# ### 002. Venue Geography
#
# A first-pass map-like scatter using setlist.fm venue coordinates. This can
# become a proper world map later if the story needs geographic polish.

# %%
venue_geo = (
    df.dropna(subset=["venue_latitude", "venue_longitude"])
    .groupby(
        [
            "venue_id",
            "venue_name",
            "venue_city",
            "venue_state_code",
            "venue_country_code",
            "venue_latitude",
            "venue_longitude",
        ],
        dropna=False,
    )
    .agg(
        total_shows=("event_id", "nunique"),
        total_song_performances=("event_set_song_id", "count"),
    )
    .reset_index()
)

venue_geo.head()

# %%
venue_map_plot = (
    ggplot(
        venue_geo,
        aes(
            x="venue_longitude",
            y="venue_latitude",
            size="total_shows",
            color="venue_country_code",
        ),
    )
    + geom_point(alpha=0.78)
    + scale_size(range=(2, 12))
    + labs(
        x="Longitude",
        y="Latitude",
    )
    + gaffer.source_caption()
    + gaffer.theme(fig_width=16, fig_height=9, panel_grid="both")
    + theme(
        # axis_title_y=element_text(size=9)
    )
)

venue_map_plot

# %%
export.chart(
    venue_map_plot,
    project_name=PROJECT_NAME,
    chart_number="002",
    viz_name="Venue-Geography",
    out_dir=FIGURES_DIR,
    width=16,
    height=9,
)

# %% [markdown]
# ## 003. Taylor Tour Comparison
#
# This uses `mart_setlist_history` directly so the comparison can include prior
# Taylor Swift tours without changing Project 003's master model.

# %%
tour_comparison_query = """
select
    coalesce(event_tour, 'Unknown tour') as event_tour,
    count(distinct event_id) as total_shows,
    count(*) as total_song_performances,
    count(distinct song_name) as unique_songs,
    min(event_date) as first_show,
    max(event_date) as last_show
from
    analytics_mart.mart_setlist_history
where true
    and artist_name_hint = 'TaylorSwift'
    and event_tour is not null
group by
    1
having
    count(distinct event_id) >= 5
order by
    total_shows desc,
    total_song_performances desc
"""

tour_comparison = run_query(tour_comparison_query)
tour_comparison["first_show"] = pd.to_datetime(tour_comparison["first_show"])
tour_comparison["last_show"] = pd.to_datetime(tour_comparison["last_show"])
tour_comparison.head(12)

# %%
tour_colors = {
    "The Eras Tour": gaffer.COLORS["spotRed"],
    "Other Taylor tours": gaffer.COLORS["setlistBlue"],
}

tour_comparison = tour_comparison.assign(
    tour_group=lambda frame: frame["event_tour"].where(
        frame["event_tour"].str.contains("Eras Tour", case=False, na=False),
        "Other Taylor tours",
    )
)

tour_comparison_plot = (
    ggplot(
        tour_comparison,
        aes(
            x="total_shows",
            y="total_song_performances",
            color="tour_group",
            size="unique_songs",
        ),
    )
    + geom_point(alpha=0.82)
    + scale_color_manual(values=tour_colors)
    + scale_size(range=(3, 13))
    + labs(
        x="Tracked shows",
        y="Song performances",
        title="The Eras Tour Compared With Taylor Swift's Other Tours",
        subtitle="Tours with at least five tracked setlist.fm shows.",
    )
    + gaffer.source_caption()
    + gaffer.theme(fig_width=12, fig_height=9, panel_grid="both")
    + theme(
        plot_title=element_text(size=16, weight="bold", color=gaffer.COLORS["backstageBlack"]),
        plot_subtitle=element_text(size=10, color=gaffer.COLORS["gafferGrey"]),
    )
)

tour_comparison_plot

# %%
export.chart(
    tour_comparison_plot,
    project_name=PROJECT_NAME,
    chart_number="003",
    viz_name="Taylor-Tour-Comparison",
    out_dir=FIGURES_DIR,
    width=12,
    height=9,
)

# %% [markdown]
# ## 004. Album Representation
#
# Count song performances by selected Spotify album match. Covers and unmatched
# songs are kept visible so the chart reveals matching gaps.

# %%
album_order = [
    "Taylor Swift",
    "Fearless",
    "Speak Now",
    "Red",
    "1989",
    "reputation",
    "Lover",
    "folklore",
    "evermore",
    "Midnights",
    "THE TORTURED POETS DEPARTMENT",
    "Other / unmatched",
]

album_colors = {
    "Taylor Swift": "#6FAF75",
    "Fearless": "#D9B650",
    "Speak Now": "#8F6AAE",
    "Red": "#C8463A",
    "1989": "#4B9FD3",
    "reputation": "#4A4A4A",
    "Lover": "#E78AB5",
    "folklore": "#8F8F86",
    "evermore": "#A66A43",
    "Midnights": "#2D416C",
    "THE TORTURED POETS DEPARTMENT": "#C9B8A6",
    "Other / unmatched": gaffer.COLORS["gafferGrey"],
}


def album_family(album_name: str | None) -> str:
    if pd.isna(album_name) or not album_name:
        return "Other / unmatched"
    normalized = album_name.casefold()
    for album in album_order:
        if album != "Other / unmatched" and album.casefold() in normalized:
            return album
    return "Other / unmatched"


album_summary = (
    df.assign(album_family=lambda frame: frame["album_name"].map(album_family))
    .groupby("album_family", dropna=False)
    .agg(
        song_performances=("event_set_song_id", "count"),
        unique_songs=("song_name", "nunique"),
    )
    .reset_index()
)

album_summary["album_family"] = pd.Categorical(
    album_summary["album_family"],
    categories=[album for album in album_order if album in set(album_summary["album_family"])],
    ordered=True,
)
album_summary = album_summary.sort_values("album_family")

album_summary

# %%
album_plot = (
    ggplot(album_summary, aes("album_family", "song_performances", fill="album_family"))
    + geom_col(show_legend=False)
    + scale_fill_manual(values=album_colors)
    + labs(
        x=None,
        y="Song performances",
        title="Which Albums Got The Most Love?",
        subtitle="Counts include repeat performances across all tracked Eras Tour shows.",
    )
    + gaffer.source_caption(additional_sources=["Spotify"])
    + gaffer.theme(fig_width=12, fig_height=9, panel_grid="y")
    + theme(
        plot_title=element_text(size=16, weight="bold", color=gaffer.COLORS["backstageBlack"]),
        plot_subtitle=element_text(size=10, color=gaffer.COLORS["gafferGrey"]),
        axis_text_x=element_text(rotation=35, ha="right"),
    )
)

album_plot

# %%
export.chart(
    album_plot,
    project_name=PROJECT_NAME,
    chart_number="004",
    viz_name="Album-Representation",
    out_dir=FIGURES_DIR,
    width=12,
    height=9,
)
