import sys
import os

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, PROJECT_ROOT)

from spotify import search_artist_uri,albums_dataframe,album_tracks_dataframe,albums_metadata_dataframe,tracks_metadata_dataframe
from setlistfm import setlist_dataframe,search_artist
from postgres import load_dataframe,upsert_raw_table

import logging


logging.basicConfig(level=logging.INFO)  # DEBUG < INFO < WARNING < ERROR < CRITICAL


# print(search_artist("Turnstile"))
# print(search_artist_uri("Turnstile")) 

fetch_config = {
    'setlistfm_force_refresh': False
    ,'spotify_force_refresh': False
    ,'sample':True
}

tame_impala_fetch = {
    'mbid': "63aa26c3-d59b-4da4-84ac-716b54f1ef4d"
    ,'spotifyuri':"spotify:artist:5INjqkS1o8h1imAzPqGZBb"
    ,'name_hint':"TameImpala"
}

billie_Eilish_fetch = {
    'mbid': "f4abc0b5-3f7a-4eff-8f78-ac078dbce533"
    ,'spotifyuri':"spotify:artist:6qqNVTkY8uBg9cP3Jd7DAH"
    ,'name_hint':"BillieEilish"
}

Japanese_Breakfast_fetch = {
    'mbid': "8c529495-91f5-4e2f-b71b-adcb66878d04"
    ,'spotifyuri':"spotify:artist:7MoIc5s9KXolCBH1fy9kkw"
    ,'name_hint':"JapaneseBreakfast"
}

Turnstile_fetch = {
    'mbid': "7b748dac-f5ce-45a7-9b95-c1d8b5b013ed"
    ,'spotifyuri':"spotify:artist:2qnpHrOzdmOo1S4ox3j17x"
    ,'name_hint':"Turnstile"
}

project_artist_fetch = [
    tame_impala_fetch
    ,billie_Eilish_fetch
    ,Japanese_Breakfast_fetch
    ,Turnstile_fetch
]

for artist in project_artist_fetch:
    #Setlist History
    upsert_raw_table("setlist_history",setlist_dataframe(artist['mbid'],name_hint=artist['name_hint'],force_refresh=fetch_config['setlistfm_force_refresh'],sample=fetch_config['sample']))

    #load album data
    upsert_raw_table("artist_albums",albums_dataframe(artist['spotifyuri'],name_hint=artist['name_hint'],force_refresh=fetch_config['spotify_force_refresh']),)

    #load track data
    upsert_raw_table("artist_tracks",album_tracks_dataframe(artist['spotifyuri'],name_hint=artist['name_hint'],force_refresh=fetch_config['spotify_force_refresh']))

    #load album metadata
    upsert_raw_table("artist_albums_metadata",albums_metadata_dataframe(artist['spotifyuri'],name_hint=artist['name_hint'],force_refresh=fetch_config['spotify_force_refresh']))

    #load track metadata
    upsert_raw_table("artist_tracks_metadata",tracks_metadata_dataframe(artist['spotifyuri'],name_hint=artist['name_hint'],force_refresh=fetch_config['spotify_force_refresh']))
