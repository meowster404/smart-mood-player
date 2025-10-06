# utils/mood_detector.py

mood_mapping = {
    "study": "calm",
    "focus": "calm",
    "relax": "calm",
    "party": "energetic",
    "workout": "energetic",
    "happy": "happy",
    "sad": "sad",
    "sleep": "calm",
    "dance": "energetic"
}

def detect_intent(user_text: str) -> str:
    """Detect user intent based on keywords."""
    user_text = user_text.lower()
    for key in mood_mapping:
        if key in user_text:
            return mood_mapping[key]
    return "calm"  # fallback
