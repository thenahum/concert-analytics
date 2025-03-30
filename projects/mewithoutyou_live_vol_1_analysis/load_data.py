import sys
import os

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, PROJECT_ROOT)

from spotify import albums_dataframe,album_tracks_dataframe,albums_metadata_dataframe,tracks_metadata_dataframe
from setlistfm import setlist_dataframe
from postgres import load_dataframe

import logging


logging.basicConfig(level=logging.INFO)  # DEBUG < INFO < WARNING < ERROR < CRITICAL

mbid = "759b5ff1-91fe-4ec9-b9b7-75b7b2ceb283"
spotifyuri="spotify:artist:3D4qYDvoPn5cQxtBm4oseo"
name_hint="mewithoutyou"
force_refresh = False
sample = False

#load setlist data
load_dataframe(setlist_dataframe(mbid,name_hint=name_hint,force_refresh=force_refresh,sample=False),table_name='setlist_history')

#load album data
load_dataframe(albums_dataframe(spotifyuri,name_hint=name_hint,force_refresh=force_refresh),table_name='artist_albums')

#load track data
load_dataframe(album_tracks_dataframe(spotifyuri,name_hint=name_hint,force_refresh=force_refresh),table_name='artist_tracks')

#load album metadata
load_dataframe(albums_metadata_dataframe(spotifyuri,name_hint=name_hint,force_refresh=force_refresh),table_name='artist_albums_metadata')

#load track metadata
load_dataframe(tracks_metadata_dataframe(spotifyuri,name_hint=name_hint,force_refresh=force_refresh),table_name='artist_tracks_metadata')
