# utils/spotify_utils.py

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_spotify_client():
    """Authenticate with Spotify using environment variables."""
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"
    ))

def get_spotify_recommendations(sp, mood):
    """Search Spotify for mood-based songs."""
    print(f"🎧 Searching for {mood} mood songs on Spotify...")
    query = f"{mood} music"
    results = sp.search(q=query, type="track", limit=5)
    
    tracks = []
    for item in results["tracks"]["items"]:
        tracks.append({
            "title": item["name"],
            "artist": item["artists"][0]["name"],
            "url": item["external_urls"]["spotify"]
        })
    return tracks
