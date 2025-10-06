# main.py
# Smart Mood-Based Music Player (Spotify Integrated v2.0)

import os
import random
import webbrowser
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv
from utils.voice_input import get_voice_command
from utils.mood_detector import detect_intent
from utils.spotify_utils import get_spotify_client, get_spotify_recommendations

# Load environment variables
load_dotenv()

def train_mock_model():
    """Train a mock ML model for mood classification."""
    data = {
        "energy": [0.2, 0.8, 0.9, 0.3, 0.4],
        "valence": [0.5, 0.9, 0.8, 0.2, 0.5],
        "danceability": [0.4, 0.8, 0.9, 0.3, 0.5],
        "tempo": [80, 120, 140, 60, 90],
        "acousticness": [0.9, 0.2, 0.1, 0.8, 0.7],
        "mood": ["calm", "happy", "energetic", "sad", "calm"]
    }

    df = pd.DataFrame(data)
    X = df[["energy", "valence", "danceability", "tempo", "acousticness"]]
    y = df["mood"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y_encoded)

    return model


def main():
    print("\n🎶 Smart Mood-Based Music Player (Spotify Integrated v2.0)\n")
    choice = input("Use voice command? (y/n): ").strip().lower()

    if choice == "y":
        command = get_voice_command()
        if not command:
            print("Fallback to text input.")
            command = input("Type your mood/activity: ")
    else:
        command = input("Enter your mood/activity (e.g., 'play something to study'): ")

    predicted_mood = detect_intent(command)
    print(f"🧠 Predicted Mood: {predicted_mood}")

    sp = get_spotify_client()
    tracks = get_spotify_recommendations(sp, predicted_mood)

    if not tracks:
        print("⚠️ No tracks found.")
        return

    print("\n🎵 Top Recommendations:")
    for i, t in enumerate(tracks, start=1):
        print(f"{i}. {t['title']} - {t['artist']}")

    selected = random.choice(tracks)
    print(f"\n▶️ Now playing: {selected['title']} by {selected['artist']}")
    webbrowser.open(selected["url"])


if __name__ == "__main__":
    train_mock_model()
    main()
