import sys
import os

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, PROJECT_ROOT)

from spotify import albums_dataframe,album_tracks_dataframe,albums_metadata_dataframe,tracks_metadata_dataframe
from setlistfm import setlist_dataframe
from postgres import load_dataframe,upsert_raw_table

import logging


logging.basicConfig(level=logging.INFO)  # DEBUG < INFO < WARNING < ERROR < CRITICAL

mbid = "759b5ff1-91fe-4ec9-b9b7-75b7b2ceb283"
spotifyuri="spotify:artist:3D4qYDvoPn5cQxtBm4oseo"
name_hint="mewithoutyou"
setlistfm_force_refresh = False
spotify_force_refresh = False
sample = False

#load setlist data
upsert_raw_table("setlist_history",setlist_dataframe(mbid,name_hint=name_hint,force_refresh=setlistfm_force_refresh,sample=False))

#load album data
upsert_raw_table("artist_albums",albums_dataframe(spotifyuri,name_hint=name_hint,force_refresh=spotify_force_refresh),)

#load track data
upsert_raw_table("artist_tracks",album_tracks_dataframe(spotifyuri,name_hint=name_hint,force_refresh=spotify_force_refresh))

#load album metadata
upsert_raw_table("artist_albums_metadata",albums_metadata_dataframe(spotifyuri,name_hint=name_hint,force_refresh=spotify_force_refresh))

#load track metadata
upsert_raw_table("artist_tracks_metadata",tracks_metadata_dataframe(spotifyuri,name_hint=name_hint,force_refresh=spotify_force_refresh))
