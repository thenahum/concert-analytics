import logging

from loadin.postgres import upsert_raw_table
from loadin.setlistfm import search_artist, setlist_dataframe
from loadin.spotify import (
    album_tracks_dataframe,
    albums_dataframe,
    albums_metadata_dataframe,
    search_artist_uri,
    tracks_metadata_dataframe,
)


# print(search_artist("Turnstile"))
# print(search_artist_uri("Turnstile")) 

FETCH_CONFIG = {
    "setlistfm_force_refresh": False,
    "spotify_force_refresh": False,
    "sample": False,
}

TAME_IMPALA_FETCH = {
    "mbid": "63aa26c3-d59b-4da4-84ac-716b54f1ef4d",
    "spotifyuri": "spotify:artist:5INjqkS1o8h1imAzPqGZBb",
    "name_hint": "TameImpala",
}

BILLIE_EILISH_FETCH = {
    "mbid": "f4abc0b5-3f7a-4eff-8f78-ac078dbce533",
    "spotifyuri": "spotify:artist:6qqNVTkY8uBg9cP3Jd7DAH",
    "name_hint": "BillieEilish",
}

JAPANESE_BREAKFAST_FETCH = {
    "mbid": "8c529495-91f5-4e2f-b71b-adcb66878d04",
    "spotifyuri": "spotify:artist:7MoIc5s9KXolCBH1fy9kkw",
    "name_hint": "JapaneseBreakfast",
}

TURNSTILE_FETCH = {
    "mbid": "7b748dac-f5ce-45a7-9b95-c1d8b5b013ed",
    "spotifyuri": "spotify:artist:2qnpHrOzdmOo1S4ox3j17x",
    "name_hint": "Turnstile",
}

PROJECT_ARTIST_FETCHES = [
    TAME_IMPALA_FETCH,
    BILLIE_EILISH_FETCH,
    JAPANESE_BREAKFAST_FETCH,
    TURNSTILE_FETCH,
]


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
    for artist in PROJECT_ARTIST_FETCHES:
        load_artist(artist, FETCH_CONFIG)


if __name__ == "__main__":
    main()
