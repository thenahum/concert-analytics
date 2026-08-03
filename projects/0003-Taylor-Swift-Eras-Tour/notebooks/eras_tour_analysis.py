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
#     display_name: .venv
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
import geopandas as gpd
import pandas as pd
from geodatasets import get_path
from plotnine import (
    aes,
    coord_fixed,
    coord_flip,
    facet_grid,
    geom_col,
    geom_line,
    geom_map,
    geom_point,
    geom_rect,
    geom_text,
    geom_vline,
    ggplot,
    guide_legend,
    guides,
    labs,
    scale_color_manual,
    scale_fill_manual,
    scale_size,
    scale_x_date,
    scale_x_continuous,
    scale_y_continuous,
    theme,
    element_text,
    element_blank,
    theme_void,
)

from loadin.postgres import run_query
from setkit import export, gaffer, notebook


PROJECT_NAME = "Taylor-Swift-Eras-Tour"
ctx = notebook.setup(project_name=PROJECT_NAME)
REPO_ROOT = ctx.project_root
PROJECT_DIR = REPO_ROOT / "projects" / "0003-Taylor-Swift-Eras-Tour"
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
df["album_release_date"] = pd.to_datetime(df["album_release_date"])

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

album_release_annotations = (
    df.loc[
        df["album_release_date"].between(
            show_summary["event_date"].min(),
            show_summary["event_date"].max(),
        )
        & df["album_name"].notna()
        & df["album_name"].ne("THE TORTURED POETS DEPARTMENT: THE ANTHOLOGY")
        & df["album_type"].eq("album"),
        ["album_name", "album_release_date"],
    ]
    .assign(album_release_month=lambda frame: frame["album_release_date"].dt.to_period("M").dt.to_timestamp())
    .drop_duplicates()
    .sort_values(["album_release_month", "album_release_date", "album_name"])
    .groupby("album_release_month", as_index=False)
    .agg(album_label=("album_name", " / ".join))
    .assign(label_y=monthly_show_summary["total_shows"].max() + 1)
)

monthly_timeline_plot = (
    ggplot(monthly_show_summary, aes("month_start", "total_shows"))
    + geom_col(fill=gaffer.COLORS["stageGreen"], width=24)
    + geom_vline(
        data=album_release_annotations,
        mapping=aes(xintercept="album_release_month"),
        color=gaffer.COLORS["backstageBlack"],
        linetype="dotted",
        alpha=0.45,
        size=0.8,
    )
    + geom_text(
        data=album_release_annotations,
        mapping=aes("album_release_month", "label_y", label="album_label"),
        color=gaffer.COLORS["backstageBlack"],
        size=8,
        angle=90,
        ha="left",
        va="center",
        alpha=0.75,
        nudge_x=4,
        nudge_y=-2.6,
    )
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
world = gpd.read_file(get_path("naturalearth.land"))

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
country_palette = [
    gaffer.COLORS["stageGreen"],
    gaffer.COLORS["setlistBlue"],
    gaffer.COLORS["ampOrange"],
    gaffer.COLORS["floodPink"],
    gaffer.COLORS["encorePurple"],
    gaffer.COLORS["clockYellow"],
    gaffer.COLORS["lightBlue"],
]
venue_country_colors = {
    country_code: country_palette[index % len(country_palette)]
    for index, country_code in enumerate(sorted(venue_geo["venue_country_code"].dropna().unique()))
}

venue_map_plot = (
    ggplot()
    + geom_map(
        data=world,
        fill=gaffer.COLORS["spotlightCream"],
        color=gaffer.COLORS["gafferGrey"],
        size=0.25,
    )
    + geom_point(
        data=venue_geo,
        mapping=aes(
            x="venue_longitude",
            y="venue_latitude",
            size="total_shows",
            fill="venue_country_code",
        ),
        color=gaffer.COLORS["backstageBlack"],
        shape="o",
        stroke=0.7,
        alpha=0.7,
        show_legend=False,
    )
    + coord_fixed(ratio=1)
    + scale_fill_manual(values=venue_country_colors)
    + scale_size(range=(3, 12))
    + labs(
        x="Longitude",
        y="Latitude",
    )
    + gaffer.source_caption()
    + gaffer.theme(fig_width=16, fig_height=9, panel_grid="both")
    + theme(
        axis_title_y=element_blank()
        , axis_title_x=element_blank()
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

# %%
country_legend = pd.DataFrame(
    {
        "venue_country_code": sorted(venue_country_colors),
    }
).assign(
    x=lambda frame: frame.index % 7,
    y=lambda frame: 2 - (frame.index // 7),
)

show_size_legend = pd.DataFrame(
    {
        "total_shows": sorted({1, int(venue_geo["total_shows"].max())}),
    }
).assign(
    x=lambda frame: frame.index * 1.25 + 1.3,
    y=-0.8,
)

show_size_legend_title = pd.DataFrame(
    {
        "x": [0],
        "y": [-.8],
        "label": ["Shows at venue"],
    }
)

venue_map_legend_plot = (
    ggplot()
    + geom_point(
        data=country_legend,
        mapping=aes("x", "y", fill="venue_country_code"),
        color=gaffer.COLORS["gafferGrey"],
        shape="o",
        size=7,
        stroke=0.7,
        alpha=0.92,
        show_legend=False,
    )
    + geom_text(
        data=country_legend,
        mapping=aes("x", "y", label="venue_country_code"),
        nudge_x=0.2,
        ha="left",
        va="center",
        size=9,
        color=gaffer.COLORS["backstageBlack"],
    )
    + geom_text(
        data=show_size_legend_title,
        mapping=aes("x", "y", label="label"),
        ha="left",
        va="center",
        size=9,
        color=gaffer.COLORS["backstageBlack"],
    )
    + geom_point(
        data=show_size_legend,
        mapping=aes("x", "y", size="total_shows"),
        fill=gaffer.COLORS["stageGreen"],
        color=gaffer.COLORS["gafferGrey"],
        shape="o",
        stroke=0.7,
        alpha=0.92,
        show_legend=False,
    )
    + geom_text(
        data=show_size_legend,
        mapping=aes("x", "y", label="total_shows"),
        nudge_x=0.28,
        ha="left",
        va="center",
        size=9,
        color=gaffer.COLORS["backstageBlack"],
    )
    + scale_fill_manual(values=venue_country_colors)
    + scale_size(range=(3, 12))
    + theme_void()
    + theme(figure_size=(6, 4))
)

venue_map_legend_plot

# %%
export.chart(
    venue_map_legend_plot,
    project_name=PROJECT_NAME,
    chart_number="002",
    viz_name="Venue-Geography-Legend",
    out_dir=FIGURES_DIR,
    width=10,
    height=3.5,
)

# %% [markdown]
# ### 003. Taylor Tour Comparison
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
tour_metric_colors = {
    "Eras Tour · Shows": gaffer.COLORS["stageGreen"],
    "Eras Tour · Songs per show": gaffer.COLORS["ampOrange"],
    "Other tours · Shows": gaffer.COLORS["gafferGrey"],
    "Other tours · Songs per show": gaffer.COLORS["gafferGrey"],
}

tour_comparison = tour_comparison.assign(
    is_eras_tour=lambda frame: frame["event_tour"].str.contains(
        "Eras Tour", case=False, na=False
    ),
    average_songs_per_show=lambda frame: (
        frame["total_song_performances"] / frame["total_shows"]
    ),
)

tour_order = (
    tour_comparison.sort_values("total_shows", ascending=True)["event_tour"]
    .drop_duplicates()
    .tolist()
)

tour_comparison_bars = (
    tour_comparison[
        ["event_tour", "is_eras_tour", "total_shows", "average_songs_per_show"]
    ]
    .melt(
        id_vars=["event_tour", "is_eras_tour"],
        value_vars=["total_shows", "average_songs_per_show"],
        var_name="metric_key",
        value_name="value",
    )
    .assign(
        event_tour=lambda frame: pd.Categorical(
            frame["event_tour"], categories=tour_order, ordered=True
        ),
        tour_position=lambda frame: frame["event_tour"].cat.codes,
        metric=lambda frame: pd.Categorical(
            frame["metric_key"].map(
                {
                    "total_shows": "Total shows",
                    "average_songs_per_show": "Average songs per show",
                }
            ),
            categories=["Total shows", "Average songs per show"],
            ordered=True,
        ),
        plot_value=lambda frame: frame["value"],
        fill_group=lambda frame: (
            frame["is_eras_tour"].map({True: "Eras Tour", False: "Other tours"})
            + " · "
            + frame["metric_key"].map(
                {
                    "total_shows": "Shows",
                    "average_songs_per_show": "Songs per show",
                }
            )
        ),
    )
)

tour_comparison_plot = (
    ggplot(
        tour_comparison_bars,
        aes(
            xmin="plot_value",
            xmax=0,
            ymin="tour_position - 0.36",
            ymax="tour_position + 0.36",
            fill="fill_group",
        ),
    )
    + geom_rect(show_legend=False)
    + facet_grid(cols="metric", scales="free_x", space="free_x")
    + scale_fill_manual(values=tour_metric_colors)
    + scale_x_continuous(labels=lambda breaks: [f"{abs(value):g}" for value in breaks])
    + scale_y_continuous(breaks=range(len(tour_order)), labels=tour_order)
    + labs(
        x=None,
        y=None,
    )
    + gaffer.source_caption()
    + gaffer.theme(fig_width=12, fig_height=9, panel_grid="x")
    + gaffer.facets()
    + theme(
        axis_text_y=element_text(color=gaffer.COLORS["backstageBlack"]),
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
# ### 004. Album Representation
#
# Count song performances by selected Spotify album match. Covers and unmatched
# songs are kept visible so the chart reveals matching gaps.

# %%
album_order = [
    "THE TORTURED POETS DEPARTMENT",
    "Midnights",
    "evermore",
    "folklore",
    "Lover",
    "reputation",
    "1989",
    "Red",
    "Speak Now",
    "Fearless",
    "Taylor Swift",
    "Other / unmatched",
]

album_colors = {
    "Taylor Swift": gaffer.COLORS["stageGreen"],
    "Fearless": gaffer.COLORS["clockYellow"],
    "Speak Now": gaffer.COLORS["encorePurple"],
    "Red": gaffer.COLORS["spotRed"],
    "1989": gaffer.COLORS["setlistBlue"],
    "reputation": gaffer.COLORS["backstageBlack"],
    "Lover": gaffer.COLORS["floodPink"],
    "folklore": gaffer.COLORS["gafferGrey"],
    "evermore": gaffer.COLORS["ampOrange"],
    "Midnights": gaffer.COLORS["lightBlue"],
    "THE TORTURED POETS DEPARTMENT": gaffer.COLORS["lightAmpOrange"],
    "Other / unmatched": gaffer.COLORS["gafferGrey"],
}


album_summary = (
    df.groupby("album_family", dropna=False)
    .agg(
        song_performances=("event_set_song_id", "count"),
        unique_songs=("track_song_name", "nunique"),
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
album_metric_order = ["Performances", "Unique songs"]

album_chart_data = (
    album_summary.melt(
        id_vars="album_family",
        value_vars=["unique_songs", "song_performances"],
        var_name="metric_key",
        value_name="count",
    )
    .assign(
        metric=lambda frame: pd.Categorical(
            frame["metric_key"].map(
                {
                    "unique_songs": "Unique songs",
                    "song_performances": "Performances",
                }
            ),
            categories=album_metric_order,
            ordered=True,
        ),
        share=lambda frame: frame["count"]
        / frame.groupby("metric", observed=True)["count"].transform("sum"),
    )
)

album_totals = (
    album_chart_data.groupby("metric", observed=True, as_index=False)["count"]
    .sum()
    .assign(
        total_label=lambda frame: frame.apply(
            lambda row: (
                f"{int(row['count']):,} unique songs"
                if row["metric"] == "Unique songs"
                else f"{int(row['count']):,} performances"
            ),
            axis=1,
        )
    )
)

album_chart_data

# %%
album_plot = (
    ggplot(album_chart_data, aes("metric", "share", fill="album_family"))
    + geom_col(width=0.62)
    + geom_text(
        data=album_totals,
        mapping=aes(x="metric", y=1.02, label="total_label"),
        inherit_aes=False,
        ha="left",
        size=9,
        family=gaffer.FONTS["axis"],
        color=gaffer.COLORS["backstageBlack"],
    )
    + scale_fill_manual(values=album_colors)
    + scale_y_continuous(
        breaks=[0, 0.25, 0.5, 0.75, 1],
        labels=lambda breaks: [f"{value:.0%}" for value in breaks],
        limits=(0, 1.16),
        expand=(0, 0),
    )
    + coord_flip()
    + guides(fill=guide_legend(nrow=2))
    + labs(
        x=None,
        y="Share of total",
        fill=None,
    )
    + gaffer.source_caption(additional_sources=["Spotify API"])
    + gaffer.theme(fig_width=12, fig_height=6, panel_grid="x")
    + theme(
        axis_text_y=element_text(color=gaffer.COLORS["backstageBlack"]),
        legend_position="bottom",
        legend_direction="horizontal",
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
    height=6,
)
