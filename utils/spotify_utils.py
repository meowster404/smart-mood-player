# utils/spotify_utils.py
import os
import random
import json
import urllib.request
import urllib.parse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --- Mood to Audio Feature Mapping ---
MOOD_TO_FEATURES = {
    "anger":    {"target_valence": 0.2, "target_energy": 0.8, "target_tempo": 140},
    "disgust":  {"target_valence": 0.1, "target_energy": 0.7},
    "fear":     {"target_valence": 0.3, "target_energy": 0.6},
    "joy":      {"target_valence": 0.9, "target_energy": 0.8, "target_tempo": 120},
    "neutral":  {"target_valence": 0.5, "target_energy": 0.5},
    "sadness":  {"target_valence": 0.2, "target_energy": 0.3, "target_tempo": 80},
    "shame":    {"target_valence": 0.3, "target_energy": 0.4},
    "surprise": {"target_valence": 0.8, "target_energy": 0.7}
}

# --- Genre Seeds for Variety ---
FALLBACK_GENRE_SEEDS = [
    "acoustic", "chill", "dance", "happy", "hip-hop",
    "indie", "pop", "r-n-b", "rock", "sad"
]

def get_spotify_client():
    """Authenticate using the Client Credentials Flow."""
    print("Attempting to authenticate with Spotify...")
    try:
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''
        
        auth_manager = SpotifyClientCredentials(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        print("✅ Spotify authentication successful!")
        return sp
    except Exception as e:
        print(f"\n❌ SPOTIFY AUTHENTICATION FAILED ❌")
        print(f"Could not connect. Please check your credentials in the .env file.")
        print(f"Error details: {e}\n")
        return None

def get_spotify_recommendations(sp, mood):
    """
    Get Spotify recommendations by manually building the API request
    using Python's built-in urllib to bypass any conflicts.
    """
    if not sp:
        print("Spotify client is not available. Skipping search.")
        return []

    print(f"🎧 Searching for '{mood}' mood songs on Spotify...")
    
    try:
        # 1. Get a valid access token from the spotipy client
        token_info = sp.auth_manager.get_access_token(as_dict=False)
        access_token = token_info
        
        # 2. Prepare parameters for the recommendation endpoint
        num_seeds = random.randint(1, 2)
        selected_genres = random.sample(FALLBACK_GENRE_SEEDS, num_seeds)
        print(f"Using seed genres: {selected_genres}")

        params = {
            'limit': 20,
            'seed_genres': ",".join(selected_genres),
            'min_popularity': 50  # Added for more popular tracks
        }
        features = MOOD_TO_FEATURES.get(mood.lower(), {})
        params.update(features)

        # 3. Build the URL and request headers
        base_url = "https://api.spotify.com/v1/recommendations" # Corrected URL
        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_string}"
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # 4. Make the API call using the basic 'urllib' library
        req = urllib.request.Request(full_url, headers=headers)
        
        # This context manager handles opening and closing the connection
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                raise Exception(f"HTTP Error {response.status}: {response.reason}")
            response_body = response.read()
            results = json.loads(response_body.decode('utf-8'))

    except Exception as e:
        print(f"❌ FAILED TO GET RECOMMENDATIONS. Error: {e}")
        return []
    
    # Process the tracks from the results
    tracks = []
    track_items = results.get("tracks", [])
    if not track_items:
        print("⚠️ Spotify returned 0 tracks for this mood.")
        return []

    for item in track_items:
        if item and item.get("name"):
            tracks.append({
                "title": item["name"],
                "artist": item["artists"][0]["name"],
                "url": item["external_urls"]["spotify"],
                "preview_url": item.get("preview_url")
            })

    print(f"Found {len(tracks)} tracks.")
    return tracks