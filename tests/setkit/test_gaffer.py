from setkit import gaffer


def test_gaffer_public_api_imports():
    assert gaffer.COLORS["stageGreen"] == "#33C27D"
    assert gaffer.FONTS["axis"] == "Courier New"


def test_gaffer_theme_builds_plotnine_theme():
    assert gaffer.theme(panel_grid="both") is not None
    assert gaffer.facets() is not None


def test_source_caption_builds_label_layer():
    assert gaffer.source_caption(["Spotify Web API"]) is not None
