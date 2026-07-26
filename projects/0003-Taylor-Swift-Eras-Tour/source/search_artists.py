"""Find Spotify and setlist.fm artist identifiers for this project.

This module is import-safe. API clients and credentials are only loaded when
``main()`` runs or ``search_artists()`` is called explicitly.
"""

from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
import time
from typing import Any, Sequence

from loadin.setlistfm import search_artist as search_setlistfm_artist
from loadin.spotify import search_artist_uri as search_spotify_artist


DEFAULT_ARTIST_NAME = "Taylor Swift"
SETLISTFM_REQUEST_DELAY_SECONDS = 2


def search_all_setlistfm_artists(artist_name: str) -> dict[str, Any]:
    """Fetch every setlist.fm artist-search page for a raw name query."""
    first_page = search_setlistfm_artist(
        artist_name,
        page=1,
        sort="relevance",
    )
    artists = list(first_page.get("artist", []))
    total = int(first_page.get("total", len(artists)))
    items_per_page = int(first_page.get("itemsPerPage", len(artists) or 1))
    total_pages = (total + items_per_page - 1) // items_per_page

    for page in range(2, total_pages + 1):
        time.sleep(SETLISTFM_REQUEST_DELAY_SECONDS)
        response = search_setlistfm_artist(
            artist_name,
            page=page,
            sort="relevance",
        )
        artists.extend(response.get("artist", []))

    return {
        "artist": artists,
        "total": total,
        "itemsPerPage": items_per_page,
        "pagesFetched": total_pages,
    }


def search_artists(artist_name: str) -> dict[str, Any]:
    """Return raw artist search results from Spotify and setlist.fm."""
    return {
        "query": artist_name,
        "spotify": search_spotify_artist(artist_name),
        "setlistfm": search_all_setlistfm_artists(artist_name),
    }


def _spotify_candidates(results: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = []
    for artist in results.get("spotify", []):
        candidates.append(
            {
                "name": artist.get("name"),
                "id": artist.get("id"),
                "uri": artist.get("uri"),
            }
        )
    return candidates


def _setlistfm_candidates(results: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = []
    for artist in results.get("setlistfm", {}).get("artist", []):
        candidates.append(
            {
                "name": artist.get("name"),
                "mbid": artist.get("mbid"),
                "sort_name": artist.get("sortName"),
                "disambiguation": artist.get("disambiguation"),
            }
        )
    return candidates


def _normalized_name(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


def _name_rank(candidate_name: str | None, query: str) -> tuple[bool, int, float, str]:
    """Sort exact and minimally embellished artist names before fan-out names."""
    candidate = _normalized_name(candidate_name)
    length_difference = abs(len(candidate) - len(query))
    similarity = SequenceMatcher(None, query, candidate).ratio()
    return candidate != query, length_difference, -similarity, candidate


def summarize_results(results: dict[str, Any]) -> dict[str, Any]:
    """Return all fetched candidates ordered by closeness to the query."""
    query = _normalized_name(results["query"])
    setlistfm_response = results.get("setlistfm", {})
    setlistfm_candidates = sorted(
        _setlistfm_candidates(results),
        key=lambda artist: _name_rank(artist.get("name"), query),
    )

    return {
        "query": results["query"],
        "spotify": _spotify_candidates(results),
        "setlistfm": setlistfm_candidates,
        "setlistfm_pagination": {
            "pages_fetched": setlistfm_response.get("pagesFetched"),
            "items_per_page": setlistfm_response.get("itemsPerPage"),
            "total": setlistfm_response.get("total"),
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search Spotify and setlist.fm for an artist's IDs."
    )
    parser.add_argument(
        "artist_name",
        nargs="?",
        default=DEFAULT_ARTIST_NAME,
        help=f"Raw artist search string (default: {DEFAULT_ARTIST_NAME!r}).",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print complete API responses instead of the candidate summary.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    results = search_artists(args.artist_name)
    output = results if args.raw else summarize_results(results)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
