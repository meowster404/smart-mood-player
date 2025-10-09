# utils/spotify_utils.py
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

def get_spotify_client():
    """Authenticates with Spotify to get a client object."""
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("⚠️ Spotify Client ID or Secret not found in .env")
        return None

    try:
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = Spotify(auth_manager=auth_manager)
        return sp
    except Exception as e:
        print(f"⚠️ Failed to authenticate Spotify client: {e}")
        return None

def search_for_playlists(sp, query):
    """Searches for 20 playlists on Spotify based on a query."""
    if not sp:
        return []
    
    try:
        # Using the 'search' endpoint with type='playlist'
        results = sp.search(q=query, type='playlist', limit=20)
        if not results['playlists']['items']:
            return []
        
        playlists = []
        for item in results['playlists']['items']:
            playlists.append({
                "name": item["name"],
                "owner": item["owner"]["display_name"],
                "url": item["external_urls"]["spotify"],
            })
        return playlists
    except Exception as e:
        print(f"⚠️ Spotify search error: {e}")
        return []

def search_for_tracks(sp, query):
    """Searches for 20 tracks on Spotify based on a query."""
    if not sp:
        return []
    
    try:
        # Using the 'search' endpoint with type='track'
        results = sp.search(q=query, type='track', limit=20)
        if not results['tracks']['items']:
            return []
        
        tracks = []
        for item in results['tracks']['items']:
            tracks.append({
                "name": item["name"],
                "artist": item["artists"][0]["name"],
                "url": item["external_urls"]["spotify"],
                "uri": item["uri"],
            })
        return tracks
    except Exception as e:
        print(f"⚠️ Spotify search error: {e}")
        return []