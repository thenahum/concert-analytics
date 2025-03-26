import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()

# Create and cache a Spotipy client
_sp = None

def get_spotify_client():
    global _sp
    if _sp is None:
        _sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
            )
        )
    return _sp


def search_artist_uri(artist_name: str) -> str:
    """
    Search for an artist by name and return their Spotify URI.
    """
    sp = get_spotify_client()
    result = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
    items = result.get('artists', {}).get('items', [])
    if not items:
        raise ValueError(f"No artist found for '{artist_name}'")
    return items[0]['uri']



def get_artist_albums(artist_uri: str) -> list:
    """
    Get all albums for the artist URI. Returns raw album objects.
    """
    sp = get_spotify_client()
    albums = []
    limit = 50
    offset = 0
    while True:
        results = sp.artist_albums(artist_uri, album_type='album', limit=limit, offset=offset)
        items = results.get('items', [])
        if not items:
            break
        albums.extend(items)
        offset += limit
    return albums


def get_album_tracks(album_ids: list) -> list:
    """
    Given a list of album IDs, return all their tracks as raw track objects.
    """
    sp = get_spotify_client()
    tracks = []
    for album_id in album_ids:
        album_tracks = []
        limit = 50
        offset = 0
        while True:
            result = sp.album_tracks(album_id, limit=limit, offset=offset)
            items = result.get('items', [])
            if not items:
                break

            for track in items:
                track["album_id"] = album_id
                album_tracks.append(track)

            offset += limit
        tracks.extend(album_tracks)
    return tracks