# utils/spotify_utils.py
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_spotify_client():
    """Authenticate using the Client Credentials Flow (no browser needed)."""
    print("Attempting to authenticate with Spotify using Client Credentials...")
    try:
        auth_manager = SpotifyClientCredentials(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        print("✅ Spotify authentication successful!")
        return sp
    except Exception as e:
        print(f"\n❌ SPOTIFY AUTHENTICATION FAILED ❌")
        print("Could not connect. Please ensure SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET are correct in your .env file.")
        print(f"Error details: {e}\n")
        return None

def get_spotify_recommendations(sp, mood):
    """Search Spotify for mood-based songs."""
    if not sp:
        print("Spotify client is not available. Skipping search.")
        return []

    print(f"🎧 Searching for '{mood}' mood songs on Spotify...")
    query = f"genre:{mood}"

    try:
        results = sp.search(q=query, type="track", limit=20)
        tracks = []
        if not results["tracks"]["items"]:
            print("⚠️ Spotify returned 0 tracks for this query.")
            return []

        for item in results["tracks"]["items"]:
            tracks.append({
                "title": item["name"],
                "artist": item["artists"][0]["name"],
                "url": item["external_urls"]["spotify"],
                "preview_url": item["preview_url"]  # <-- Add this line
            })
        print(f"Found {len(tracks)} tracks.")
        return tracks

    except Exception as e:
        print(f"\n❌ FAILED TO SEARCH TRACKS ❌")
        print(f"An error occurred during the Spotify search: {e}\n")
        return []