# test_spotify_api.py
import os
import random
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# --------------------- Load .env ---------------------
load_dotenv()  # Make sure your .env file is in the same directory
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    print("❌ Missing Spotify credentials in .env")
    exit()

# --------------------- Spotify Client ---------------------
try:
    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET
    )
    sp = Spotify(auth_manager=auth_manager)
    print("✅ Spotify client authenticated successfully!")
except Exception as e:
    print(f"❌ Failed to authenticate Spotify client: {e}")
    exit()

# --------------------- Fetch Sample Recommendations ---------------------
MOOD_FEATURES = {
    "relaxed": {"target_valence": 0.8, "target_energy": 0.2, "target_tempo": 70}
}
GENRES = ["pop", "rock", "jazz", "classical", "indie"]

try:
    mood = "relaxed"
    genres = random.sample(GENRES, 2)
    print(f"🎧 Fetching sample tracks for mood '{mood}' with genres {genres}...\n")

    results = sp.recommendations(
        seed_genres=genres,
        limit=5,
        **MOOD_FEATURES[mood]
    )

    for i, track in enumerate(results["tracks"], 1):
        print(f"{i}. {track['name']} - {track['artists'][0]['name']}")
        print(f"   Spotify URL: {track['external_urls']['spotify']}")
        print(f"   Preview URL: {track.get('preview_url')}\n")

    print("✅ Spotify API fetch successful!")

except Exception as e:
    print(f"❌ Error fetching tracks: {e}")
