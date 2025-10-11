# utils/intent_detector.py
import re

class IntentDetector:
    def __init__(self):
        # Define keywords and patterns for different intents
        self.greeting_keywords = ['hi', 'hello', 'hey', 'greetings', 'yo']
        self.question_keywords = ['how are you', 'who are you', 'what are you']
        self.activity_keywords = {
            "study": ["study", "studying", "focus", "work", "working"],
            "workout": ["workout", "gym", "running", "exercise", "pumping iron"],
            "sleep": ["sleep", "sleeping", "nap", "relax", "relaxing", "calm"],
            "party": ["party", "dancing", "celebrate", "celebrating"]
        }
        self.artist_patterns = [r"songs by (.+)", r"music by (.+)", r"artist (.+)", r"from (.+)"]
        self.song_patterns = [r"play (.+)", r"hear (.+)", r"find (.+)", r"search for (.+)"]
        self.activity_patterns = [r"songs for (.+)", r"music for (.+)"]

    def detect_intent(self, text):
        text = text.lower().strip()

        # 1. Greeting Intent (check for exact word match)
        words = re.findall(r'\b\w+\b', text)
        if words and words[0] in self.greeting_keywords:
            return {"intent": "GREETING", "entity": None}

        # 2. Question Intent
        if any(phrase in text for phrase in self.question_keywords):
            return {"intent": "QUESTION", "entity": None}

        # 3. Artist Intent
        for pattern in self.artist_patterns:
            match = re.search(pattern, text)
            if match and match.group(1):
                return {"intent": "ARTIST", "entity": match.group(1).strip()}

        # 4. Activity Intent
        for pattern in self.activity_patterns:
            match = re.search(pattern, text)
            if match and match.group(1):
                activity = match.group(1).strip()
                for mood, keywords in self.activity_keywords.items():
                    if any(key in activity for key in keywords):
                        return {"intent": "ACTIVITY", "entity": activity, "mood": mood}

        # 5. Song Intent (must be after Artist and Activity to avoid ambiguity)
        for pattern in self.song_patterns:
            match = re.search(pattern, text)
            if match and match.group(1):
                # Avoid capturing entities from other intents
                if not any(kw in text for kw in ["by", "for"]):
                    return {"intent": "SONG", "entity": match.group(1).strip()}

        # 6. Default to Mood
        return {"intent": "MOOD", "entity": text}