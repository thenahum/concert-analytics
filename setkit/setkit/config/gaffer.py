from plotnine import ggplot, aes, geom_col, labs, theme, element_text, element_rect, scale_x_datetime, element_blank,element_line

#Colors
gaffer_colors = {
    "lightAmpOrange": "#FB9E50"
    , "floodPink": "#F986BA"
    , "setlistBlue": "#3C7DC4"
    , "spotRed": "#D64848"
    , "ampOrange": "#F25C05"
    , "lightBlue":"#A7ECF5"
    , "encorePurple": "#5D4E8C"
    , "stageGreen": "#33C27D"
    , "clockYellow": "#F6D357"
    , "spotlightCream": "#FAF3E0"
    , "gafferGrey": "#777777"
    , "backstageBlack":"#1C1C1C"
}

base_family_axis="Courier New"
base_family_title="Helvetica"

def default_labels(additional_sources=[]):
    sources = 'setflist.fm'
    if len(additional_sources) > 0:
        for source in additional_sources:
            sources += f', {source}'

    default_labels = labs(
            caption = f"Source: {sources} sourced via Concert Analytics"
        )

    return default_labels

def gaffer_theme(fig_width=9,fig_height=16,panel_grid='x'):
    #panel_grid can be x, y, or both
    #Basic Fonts

    # Define the grid line element once
    grid_line = element_line(
        color=gaffer_colors["gafferGrey"],
        linetype="dashed",
        size=0.5
    )

    # Determine which grid lines to show
    panel_grid_y = grid_line if panel_grid in ("y", "both") else element_blank()
    panel_grid_x = grid_line if panel_grid in ("x", "both") else element_blank()

    gaffer_theme = theme(
        # aspect_ratio = 9 / 16
        # , 
        figure_size=(fig_width,fig_height)
        
        # Backgrounds
        , plot_background=element_rect(fill=gaffer_colors["spotlightCream"], color=None)
        , panel_background=element_rect(fill=gaffer_colors["spotlightCream"], color=None)
        , panel_border=element_blank()

        #Margins
        , plot_margin_top= .03
        , plot_margin_bottom=.025
        , plot_margin_right= 0.03
        , plot_margin_left=0.03

        # Titles & subtitles
        , plot_title=element_blank()
        , plot_subtitle=element_blank()
        
        , plot_caption=element_text(
            family=base_family_axis
            , size=12
            , color=gaffer_colors["gafferGrey"]
            , ha='right'
            , margin={'t': 30}  # spacing above caption
        )

        # Axis
        , axis_title=element_text(
            family=base_family_axis
            , size=12
            , color=gaffer_colors["gafferGrey"]
            , weight='ultralight'
            # ,margin={'t': 5, 'r': 5}  # tweak based on axis
        )
        
        , axis_text=element_text(
            family=base_family_axis
            , size=12
            , color=gaffer_colors["gafferGrey"]
            # ,margin={'l':5, 't':20}
        )

        , axis_title_y=element_blank()
        
        , axis_ticks=element_line(
            color=gaffer_colors["spotlightCream"]
        )
        , axis_ticks_minor=element_blank()

        , panel_grid_major_y = panel_grid_y
        , panel_grid_major_x = panel_grid_x
        , panel_grid_minor=element_blank()

        # Legend
        , legend_title=element_blank()
        , legend_background=element_blank()
        , legend_key=element_blank()
        , legend_key_width=10
        , legend_position="top"
        , legend_margin=1
        , legend_direction="vertical"
        # ,legend_margin=margins(t=5, b=5)
        # ,legend_box_margin=margins(t=10)
    )

    return gaffer_theme

def gaffer_facets():
    """
    Facet styling preset for On The Setlist · Gaffer.
    """
    return theme(
        # facet title
        strip_text=element_text(
            size=12
            , family="Courier New"
            , color=gaffer_colors["backstageBlack"]
        )
        , strip_background=element_blank()
        , axis_title_x=element_blank() 
    )