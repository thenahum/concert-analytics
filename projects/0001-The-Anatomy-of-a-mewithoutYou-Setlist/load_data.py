import logging

from loadin.postgres import upsert_raw_table
from loadin.setlistfm import setlist_dataframe
from loadin.spotify import (
    album_tracks_dataframe,
    albums_dataframe,
    albums_metadata_dataframe,
    tracks_metadata_dataframe,
)


ARTIST_FETCH = {
    "mbid": "759b5ff1-91fe-4ec9-b9b7-75b7b2ceb283",
    "spotifyuri": "spotify:artist:3D4qYDvoPn5cQxtBm4oseo",
    "name_hint": "mewithoutyou",
}

FETCH_CONFIG = {
    "setlistfm_force_refresh": False,
    "spotify_force_refresh": False,
    "sample": False,
}

print(albums_dataframe(
            spotifyuri,
            name_hint=name_hint,
            force_refresh=fetch_config["spotify_force_refresh"],
        ))


def load_artist(artist: dict, fetch_config: dict):
    name_hint = artist["name_hint"]
    spotifyuri = artist["spotifyuri"]

    upsert_raw_table(
        "setlist_history",
        setlist_dataframe(
            artist["mbid"],
            name_hint=name_hint,
            force_refresh=fetch_config["setlistfm_force_refresh"],
            sample=fetch_config["sample"],
        ),
    )
    upsert_raw_table(
        "artist_albums",
        albums_dataframe(
            spotifyuri,
            name_hint=name_hint,
            force_refresh=fetch_config["spotify_force_refresh"],
        ),
    )
    upsert_raw_table(
        "artist_tracks",
        album_tracks_dataframe(
            spotifyuri,
            name_hint=name_hint,
            force_refresh=fetch_config["spotify_force_refresh"],
        ),
    )
    upsert_raw_table(
        "artist_albums_metadata",
        albums_metadata_dataframe(
            spotifyuri,
            name_hint=name_hint,
            force_refresh=fetch_config["spotify_force_refresh"],
        ),
    )
    upsert_raw_table(
        "artist_tracks_metadata",
        tracks_metadata_dataframe(
            spotifyuri,
            name_hint=name_hint,
            force_refresh=fetch_config["spotify_force_refresh"],
        ),
    )


def main():
    logging.basicConfig(level=logging.INFO)
    load_artist(ARTIST_FETCH, FETCH_CONFIG)


if __name__ == "__main__":
    main()
