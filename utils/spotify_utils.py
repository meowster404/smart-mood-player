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
    """
    Searches for 20 playlists on Spotify based on a query,
    with robust error handling.
    """
    if not sp:
        return []
    
    try:
        results = sp.search(q=query, type='playlist', limit=20)
        
        # --- Robustness Fix based on your suggestions ---
        # 1. Check if 'results' is not None and contains the 'playlists' key.
        # This handles authentication errors or bad API responses.
        if not results or 'playlists' not in results:
            print("⚠️ Spotify search returned no results or an invalid format. Check API credentials.")
            return []

        # 2. Check if the 'items' list exists and is not empty.
        # This handles cases where a search yields no results.
        playlist_items = results['playlists'].get('items')
        if not playlist_items:
            print(f"No playlists found for query: '{query}'")
            return []
        
        # 3. Process the items now that we know they exist.
        playlists = []
        for item in playlist_items:
            # Ensure each item has the expected structure before accessing keys
            if item and 'name' in item and 'owner' in item and 'external_urls' in item:
                playlists.append({
                    "name": item.get("name", "Unknown Playlist"),
                    "owner": item.get("owner", {}).get("display_name", "Unknown Owner"),
                    "url": item.get("external_urls", {}).get("spotify"),
                })
        return playlists
        
    except Exception as e:
        print(f"⚠️ An unexpected Spotify search error occurred: {e}")
        return []