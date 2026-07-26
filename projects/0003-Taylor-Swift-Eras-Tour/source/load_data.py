"""Fetch, preview, and optionally load Taylor Swift source data.

The module is import-safe. APIs, caches, and PostgreSQL are only touched after
``main()`` runs or the relevant functions are called explicitly.
"""

from __future__ import annotations

import logging
from typing import Callable, Mapping

import pandas as pd

from loadin.postgres import upsert_raw_table
from loadin.setlistfm import setlist_dataframe
from loadin.spotify import (
    album_tracks_dataframe,
    albums_dataframe,
    albums_metadata_dataframe,
    tracks_metadata_dataframe,
)


ARTIST_NAME = "Taylor Swift"
NAME_HINT = "TaylorSwift"
SETLISTFM_MBID = "20244d07-534f-4eff-b4d4-930878889970"
SPOTIFY_URI = "spotify:artist:06HL4z0CvFAxyc27GXpf02"
PREVIEW_ROWS = 10

Dataframes = dict[str, pd.DataFrame]


def prompt_choice(prompt: str, choices: Mapping[str, str]) -> str:
    """Prompt until the user selects one of the displayed choices."""
    rendered_choices = "/".join(choices)
    while True:
        answer = input(f"{prompt} [{rendered_choices}]: ").strip().casefold()
        if answer in choices:
            return choices[answer]
        print(f"Please choose one of: {rendered_choices}")


def fetch_dataframes(force_refresh: bool) -> Dataframes:
    """Build every raw dataframe, preferring caches unless refresh is forced."""
    return {
        "setlist_history": setlist_dataframe(
            SETLISTFM_MBID,
            name_hint=NAME_HINT,
            sample=False,
            force_refresh=force_refresh,
        ),
        "artist_albums": albums_dataframe(
            SPOTIFY_URI,
            name_hint=NAME_HINT,
            force_refresh=force_refresh,
        ),
        "artist_tracks": album_tracks_dataframe(
            SPOTIFY_URI,
            name_hint=NAME_HINT,
            force_refresh=force_refresh,
        ),
        "artist_albums_metadata": albums_metadata_dataframe(
            SPOTIFY_URI,
            name_hint=NAME_HINT,
            force_refresh=force_refresh,
        ),
        "artist_tracks_metadata": tracks_metadata_dataframe(
            SPOTIFY_URI,
            name_hint=NAME_HINT,
            force_refresh=force_refresh,
        ),
    }


def preview_dataframes(dataframes: Mapping[str, pd.DataFrame]) -> None:
    """Print dataframe shapes and representative rows without touching PostgreSQL."""
    for table_name, dataframe in dataframes.items():
        print(f"\nraw.{table_name}: {len(dataframe):,} rows x {len(dataframe.columns)} columns")
        if dataframe.empty:
            print("(empty dataframe)")
            continue
        print(dataframe.head(PREVIEW_ROWS).to_string(index=False))


def load_dataframes(
    dataframes: Mapping[str, pd.DataFrame],
    upsert: Callable[[str, pd.DataFrame], None] = upsert_raw_table,
) -> None:
    """Upsert every dataframe into its corresponding raw table."""
    for table_name, dataframe in dataframes.items():
        upsert(table_name, dataframe)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    action = prompt_choice(
        "Preview dataframes or load them into PostgreSQL?",
        {"preview": "preview", "load": "load"},
    )
    cache_mode = prompt_choice(
        "Use cached files when available or fetch a full refresh from the APIs?",
        {"cached": "cached", "refresh": "refresh"},
    )

    force_refresh = cache_mode == "refresh"
    print(
        f"\nPreparing {ARTIST_NAME} data "
        f"({'full API refresh' if force_refresh else 'cache preferred'})..."
    )
    dataframes = fetch_dataframes(force_refresh=force_refresh)

    if action == "preview":
        preview_dataframes(dataframes)
        print("\nPreview complete. PostgreSQL was not touched.")
        return

    load_dataframes(dataframes)
    print("\nLoad complete.")


if __name__ == "__main__":
    main()
