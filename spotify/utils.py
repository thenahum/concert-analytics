from .client import get_artist_albums,get_album_tracks,get_tracks_metadata,get_albums_metadata

import os
import json
import hashlib
import pandas as pd
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def save_json(data, filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved to {path}")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)

def _build_cache_filename(func_name, spotifyuri, cache_mode="full", name_hint=None):
    """
    Build a filename based on function name, spotifyid, and whether it's sample/full.
    """
    safe_name = name_hint.replace(" ", "_").lower() if name_hint else "data"

    if isinstance(spotifyuri, list):
        # Create a short hash of the list of IDs for uniqueness
        hash_input = json.dumps(sorted(spotifyuri)).encode("utf-8")
        uri_hash = hashlib.md5(hash_input).hexdigest()[:10]
        safe_spotifyURI = f"list_{uri_hash}"
    elif isinstance(spotifyuri, str):
        safe_spotifyURI = spotifyuri.replace(":", "_").lower()
    else:
        safe_spotifyURI = "unknown"

    filename = f"spotify_{func_name}_{safe_name}_{safe_spotifyURI}_{cache_mode}.json"
    return filename

def cached_json(fetch_func, spotifyuri, *args, name_hint=None, force=False, cache_mode="full", **kwargs):
    """
    Auto-cache wrapper: load if cached, otherwise fetch and save.
    
    Parameters:
        fetch_func (callable): Function to call if not cached.
        *args, **kwargs: Passed to the fetch function.
        name_hint (str): Optional readable name to include in filename.
        force (bool): If True, always fetch fresh data.

    Returns:
        dict or list
    """
    filename = _build_cache_filename(fetch_func.__name__, spotifyuri, cache_mode, name_hint)
    path = os.path.join(DATA_DIR, filename)

    if not force and os.path.exists(path):
        logger.info(f"Using cached: {filename}")
        return load_json(filename)

    logger.info(f"Fetching fresh and caching as: {filename}")
    data = fetch_func(spotifyuri, *args, **kwargs)
    save_json(data, filename)
    return data

def get_artist_album_ids(spotifyuri, *args, name_hint=None, force=False):
    """
    Returns album IDs in a list from a artist URI, will use cached album data unless forced
    """

    album_data = cached_json(
        get_artist_albums
        ,spotifyuri
        ,name_hint=name_hint
        ,force=force
        )

    return [album["id"] for album in album_data]


def get_all_tracks_for_artist(spotifyuri, *args, name_hint=None, force=False):
    """
    Returns album IDs in a list from a artist URI, will use cached album data unless forced
    """

    album_ids = get_artist_album_ids(
        spotifyuri
        ,name_hint=name_hint
        ,force=force
        )

    data = cached_json(
        get_album_tracks
        ,album_ids
        ,name_hint=name_hint
        ,force=force
        )

    return data

def get_all_tracks_ids(spotifyuri, *args, name_hint=None, force=False):
    """
    Returns album IDs in a list from a artist URI, will use cached album data unless forced
    """

    tracks = get_all_tracks_for_artist(
        spotifyuri
        ,name_hint=name_hint
        ,force=force
    )

    return [track["id"] for track in tracks]

def get_album_metadata_for_artist(spotifyuri, *args, name_hint=None, force=False):
    """
    Returns album IDs in a list from a artist URI, will use cached album data unless forced
    """

    album_ids = get_artist_album_ids(
        spotifyuri
        ,name_hint=name_hint
        ,force=force
        )

    data = cached_json(
        get_albums_metadata
        ,album_ids
        ,name_hint=name_hint
        ,force=force
        )

    return data

def get_track_metadata_for_artist(spotifyuri, *args, name_hint=None, force=False):
    """
    Returns album IDs in a list from a artist URI, will use cached album data unless forced
    """

    album_ids = get_all_tracks_ids(
        spotifyuri
        ,name_hint=name_hint
        ,force=force
        )

    data = cached_json(
        get_tracks_metadata
        ,album_ids
        ,name_hint=name_hint
        ,force=force
        )

    return data



def albums_to_dataframe(albums):
    """
    Convert spotify web API data into a pandas DataFrame where each row is a song performance.

    Parameters:
        albums (list): List of albums objects from the API.

    Returns:
        pd.DataFrame: Flattened album-level data.
    """
    rows = []

    for al in albums:
        album_id = al.get("id")
        album_url = al.get("href")
        album_uri = al.get("uri")
        album_type = al.get("album_type")
        album_name = al.get("name")
        album_total_tracks = al.get("total_tracks")
        album_release_date = al.get("release_date")
        album_release_date_precision = al.get("release_date_precision")
        album_group = al.get("album_group")
        album_image_url = al.get("images", [{}])[0].get("url")

        rows.append({
            "album_id": album_id
            , "album_url": album_url
            , "album_uri": album_uri
            , "album_type": album_type
            , "album_name": album_name
            , "album_total_tracks": album_total_tracks
            , "album_release_date": album_release_date
            , "album_release_date_precision": album_release_date_precision
            , "album_group": album_group
            , "album_image_url": album_image_url
        })

    return pd.DataFrame(rows)

def albums_dataframe(spotifyuri, force_refresh=False, name_hint=None):
    """
    High-level function to load setlists, cache them, and return a clean pandas DataFrame.

    Parameters:
        mbid (str): MusicBrainz ID of the artist
        sample (bool): Whether to only fetch a small sample (default: True)
        force_refresh (bool): Whether to skip the cache and re-fetch (default: False)
        name_hint (str): Optional name for cache filename (e.g. 'Radiohead')
        sample_pages (int): How many pages to fetch when sample=True (default: 3)

    Returns:
        pd.DataFrame
    """

    album_data = cached_json(
        get_artist_albums
        ,spotifyuri
        ,name_hint=name_hint
        ,force=force_refresh
    )

    return albums_to_dataframe(album_data)


def album_tracks_to_dataframe(album_tracks):
    """
    Convert spotify web API data into a pandas DataFrame where each row is a song performance.

    Parameters:
        albums (list): List of albums objects from the API.

    Returns:
        pd.DataFrame: Flattened album-level data.
    """
    rows = []

    for tr in album_tracks:
        track_id = tr.get("id")
        track_url = tr.get("href")
        track_uri = tr.get("uri")
        album_id = tr.get("album_id")
        track_disk_number = tr.get("disc_number")
        track_duration_ms = tr.get("duration_ms")
        track_name = tr.get("name")
        track_number = tr.get("track_number")

        rows.append({
            "track_id": track_id
            , "track_url": track_url
            , "track_uri": track_uri
            , "album_id": album_id
            , "track_disk_number": track_disk_number
            , "track_duration_ms": track_duration_ms
            , "track_name": track_name
            , "track_number": track_number
        })

    return pd.DataFrame(rows)

def album_tracks_dataframe(spotifyuri, force_refresh=False, name_hint=None):
    """
    High-level function to load setlists, cache them, and return a clean pandas DataFrame.

    Parameters:
        mbid (str): MusicBrainz ID of the artist
        sample (bool): Whether to only fetch a small sample (default: True)
        force_refresh (bool): Whether to skip the cache and re-fetch (default: False)
        name_hint (str): Optional name for cache filename (e.g. 'Radiohead')
        sample_pages (int): How many pages to fetch when sample=True (default: 3)

    Returns:
        pd.DataFrame
    """

    album_tracks_data = get_all_tracks_for_artist(
        spotifyuri
        ,name_hint=name_hint
        ,force=force_refresh
    )

    return album_tracks_to_dataframe(album_tracks_data)



def albums_metadata_to_dataframe(albums):
    """
    Convert spotify web API data into a pandas DataFrame where each row is a song performance.

    Parameters:
        albums (list): List of albums objects from the API.

    Returns:
        pd.DataFrame: Flattened album-level data.
    """
    rows = []

    for al in albums:
        album_id = al.get("id")
        album_popularity = al.get("popularity")

        rows.append({
            "album_id": album_id
            , "album_popularity": album_popularity
        })

    return pd.DataFrame(rows)

def albums_metadata_dataframe(spotifyuri, force_refresh=False, name_hint=None):
    """
    High-level function to load setlists, cache them, and return a clean pandas DataFrame.

    Parameters:
        mbid (str): MusicBrainz ID of the artist
        sample (bool): Whether to only fetch a small sample (default: True)
        force_refresh (bool): Whether to skip the cache and re-fetch (default: False)
        name_hint (str): Optional name for cache filename (e.g. 'Radiohead')
        sample_pages (int): How many pages to fetch when sample=True (default: 3)

    Returns:
        pd.DataFrame
    """

    album_metadata = get_album_metadata_for_artist(
        spotifyuri
        ,name_hint=name_hint
        ,force=force_refresh
    )

    return albums_metadata_to_dataframe(album_metadata)


def tracks_metadata_to_dataframe(tracks):
    """
    Convert spotify web API data into a pandas DataFrame where each row is a song performance.

    Parameters:
        albums (list): List of albums objects from the API.

    Returns:
        pd.DataFrame: Flattened album-level data.
    """
    rows = []

    for tr in tracks:
        track_id = tr.get("id")
        track_popularity = tr.get("popularity")
        track_isrc = tr.get("external_ids",{}).get("isrc")

        rows.append({
            "track_id": track_id
            , "track_popularity": track_popularity
            ,"track_isrc": track_isrc
        })

    return pd.DataFrame(rows)

def tracks_metadata_dataframe(spotifyuri, force_refresh=False, name_hint=None):
    """
    High-level function to load setlists, cache them, and return a clean pandas DataFrame.

    Parameters:
        mbid (str): MusicBrainz ID of the artist
        sample (bool): Whether to only fetch a small sample (default: True)
        force_refresh (bool): Whether to skip the cache and re-fetch (default: False)
        name_hint (str): Optional name for cache filename (e.g. 'Radiohead')
        sample_pages (int): How many pages to fetch when sample=True (default: 3)

    Returns:
        pd.DataFrame
    """

    tracks_metadata = get_track_metadata_for_artist(
        spotifyuri
        ,name_hint=name_hint
        ,force=force_refresh
    )

    return tracks_metadata_to_dataframe(tracks_metadata)
