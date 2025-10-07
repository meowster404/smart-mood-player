# spotify_utils.py
import os
import random
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

# --------------------- Mood Features & Fallback ---------------------
MOOD_TO_FEATURES = {
    "happy":   {"target_valence": 0.9, "target_energy": 0.8, "target_tempo": 120},
    "sad":     {"target_valence": 0.2, "target_energy": 0.3, "target_tempo": 60},
    "angry":   {"target_valence": 0.1, "target_energy": 0.9, "target_tempo": 140},
    "relaxed": {"target_valence": 0.8, "target_energy": 0.2, "target_tempo": 70},
    "fear":    {"target_valence": 0.1, "target_energy": 0.6},
    "neutral": {"target_valence": 0.5, "target_energy": 0.5}
}

FALLBACK_GENRE_SEEDS = [
    "pop", "rock", "edm", "hiphop", "jazz", "classical", "indie", "reggae"
]

# --------------------- Spotify Client ---------------------
def get_spotify_client():
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

# --------------------- Fetch Recommendations ---------------------
def get_spotify_recommendations(sp, mood):
    if not sp:
        print("⚠️ Spotify client unavailable.")
        return []

    features = MOOD_TO_FEATURES.get(mood.lower(), {})
    genres = random.sample(FALLBACK_GENRE_SEEDS, 2)

    print(f"🎧 Fetching recommendations for mood '{mood}' with genres {genres}...")
    try:
        # Only pass non-None features
        results = sp.recommendations(
            seed_genres=genres,
            limit=15,
            **{k: v for k, v in features.items() if v is not None}
        )
    except Exception as e:
        print(f"⚠️ Spotify API error: {e}")
        return []

    tracks = []
    for item in results.get("tracks", []):
        tracks.append({
            "title": item["name"],
            "artist": item["artists"][0]["name"],
            "url": item["external_urls"]["spotify"],
            "preview_url": item.get("preview_url")
        })

    print(f"✅ Found {len(tracks)} tracks.")
    return tracks
