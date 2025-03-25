from .client import get_all_setlists

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

def _build_cache_filename(func_name, mbid, cache_mode="sample", name_hint=None):
    """
    Build a filename based on function name, mbid, and whether it's sample/full.
    """
    safe_name = name_hint.replace(" ", "_").lower() if name_hint else "data"
    filename = f"setlistfm_{func_name}_{safe_name}_{mbid}_{cache_mode}.json"
    return filename

def cached_json(fetch_func, mbid, *args, name_hint=None, force=False, cache_mode="sample", **kwargs):
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
    filename = _build_cache_filename(fetch_func.__name__, mbid, cache_mode, name_hint)
    path = os.path.join(DATA_DIR, filename)

    if not force and os.path.exists(path):
        logger.info(f"Using cached: {filename}")
        return load_json(filename)

    logger.info(f"Fetching fresh and caching as: {filename}")
    data = fetch_func(mbid, *args, **kwargs)
    save_json(data, filename)
    return data

def setlists_to_dataframe(setlists):
    """
    Convert setlist.fm data into a pandas DataFrame where each row is a song performance.

    Parameters:
        setlists (list): List of setlist objects from the API.

    Returns:
        pd.DataFrame: Flattened song-level data.
    """
    rows = []

    for sl in setlists:
        event_date = sl.get("eventDate")
        event_id = sl.get("id")
        venue = sl.get("venue", {}).get("name")
        venue_city = sl.get("venue", {}).get("city", {}).get("name")
        venue_stateCode = sl.get("venue", {}).get("city", {}).get("stateCode")
        venue_lat = sl.get("venue", {}).get("city", {}).get("coords",{}).get("lat")
        venue_lon = sl.get("venue", {}).get("city", {}).get("coords",{}).get("long")
        venue_countryCode = sl.get("venue", {}).get("city", {}).get("country", {}).get("code")
        event_info = sl.get("info")
        event_url = sl.get("url")

        sets = sl.get("sets", {}).get("set", [])
        tour = sl.get("tour",{}).get("name")


        for set_index, set_entry in enumerate(sets):
            encore_index = set_entry.get("encore", 0)
            songs = set_entry.get("song", [])
            encore_flag = bool(set_entry.get("encore"))

            for song_index, song in enumerate(songs):
                if not bool(song.get("tape")):
                    song_name = song.get("name")
                    song_coverFlag = bool(song.get("cover"))
                    song_coverArtistName = song.get("cover",{}).get("name")
                    song_coverArtistMbid = song.get("cover",{}).get("mbid")
                    song_info = song.get("info")
                    song_withFlag = bool(song.get("with"))
                    song_withArtistName = song.get("with",{}).get("name")
                    song_withArtistMbid = song.get("with",{}).get("mbid")

                    rows.append({
                        "event_date": event_date
                        , "event_id": event_id
                        , "event_info": event_info
                        , "event_url": event_url
                        , "venue": venue
                        , "venue_city": venue_city
                        , "venue_state_code": venue_stateCode
                        , "venue_lat": venue_lat
                        , "venue_lon": venue_lon
                        , "venue_country_code": venue_countryCode
                        , "set_index": set_index
                        , "encore_flag": encore_flag
                        , "encore_index": encore_index
                        , "song_index": song_index
                        , "song": song_name
                        , "song_info": song_info
                        , "song_cover_flag": song_coverFlag
                        , "song_cover_artist_name": song_coverArtistName
                        , "song_cover_artist_mbid": song_coverArtistMbid
                        , "song_with_flag": song_withFlag
                        , "song_with_artist_name": song_withArtistName
                        , "song_with_artist_mbid": song_withArtistMbid
                    })

    return pd.DataFrame(rows)

def setlist_dataframe(mbid, sample=True, force_refresh=False, name_hint=None, sample_pages=3):
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
    max_pages = sample_pages if sample else None
    cache_mode = "sample" if sample else "full"

    setlists = cached_json(
        get_all_setlists,
        mbid,
        max_pages=max_pages,
        name_hint=name_hint,
        force=force_refresh,
        cache_mode=cache_mode
    )

    return setlists_to_dataframe(setlists)