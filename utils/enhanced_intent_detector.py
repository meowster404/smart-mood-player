# utils/enhanced_intent_detector.py
import re
import json
import os
from collections import defaultdict

class EnhancedIntentDetector:
    def __init__(self):
        # Load intent patterns from JSON
        script_dir = os.path.dirname(os.path.abspath(__file__))
        intent_path = os.path.join(script_dir, "..", "data", "intent.json")
        with open(intent_path, 'r') as f:
            self.intent_data = json.load(f)

        # Initialize conversation context
        self.conversation_context = defaultdict(str)
        self.last_intent = None
        
        # Compile regex patterns for better performance
        self.patterns = {
            "song_patterns": [
                (re.compile(r"(?i)play\s+(.+?)\s+(?:by|from)\s+(.+)"), "SongSearch"),  # "play X by Y"
                (re.compile(r"(?i)i\s+want\s+(?:to\s+hear\s+)?(?:the\s+)?(?:song\s+)?(.+?)\s+(?:by|from)\s+(.+)"), "SongSearch"),  # "I want (to hear) (the) (song) X by Y"
                (re.compile(r"(?i)i\s+want\s+to\s+listen\s+to\s+(?:the\s+)?(?:song\s+)?(.+?)\s+(?:by|from)\s+(.+)"), "SongSearch"),  # "I want to listen to X by Y"
                (re.compile(r"(?i)i\s+want\s+to\s+hear\s+(?:the\s+)?song\s+from\s+(.+)"), "ArtistSearch"),  # "I want to hear the song from X" -> Artist search
                (re.compile(r"(?i)i\s+want\s+to\s+listen\s+to\s+(?:the\s+)?(?:song\s+)?(.+)"), "SongSearch"),  # "I want to listen to (the) (song) X"
                (re.compile(r"(?i)i\s+want\s+to\s+hear\s+(?:the\s+)?(?:song\s+)?(.+)"), "SongSearch"),  # "I want to hear (the) (song) X"
                (re.compile(r"(?i)find\s+(?:me\s+)?(?:the\s+)?song\s+(.+)"), "SongSearch"),  # "find (me) (the) song X"
                (re.compile(r"(?i)search\s+for\s+(.+?)\s+(?:by|from)\s+(.+)"), "SongSearch"),  # "search for X by Y"
                (re.compile(r"(?i)play\s+(?:the\s+)?(?:song\s+)?(.+)"), "SongSearch"),  # "play (the) (song) X"
                (re.compile(r"(?i)(?:the\s+)?song\s+(?:from|by)\s+(?:the\s+)?(.+)"), "ArtistSearch"),  # "(the) song (from/by) (the) X"
            ],
            "artist_patterns": [
                (re.compile(r"(?i)play\s+songs?\s+by\s+(.+)"), "ArtistSearch"),
                (re.compile(r"(?i)find\s+music\s+(?:by|from)\s+(.+)"), "ArtistSearch"),
                (re.compile(r"(?i)show\s+(?:me\s+)?(?:songs?|tracks?)\s+by\s+(.+)"), "ArtistSearch"),
                (re.compile(r"(?i)music\s+by\s+(.+)"), "ArtistSearch")
            ],
            "mood_patterns": [
                # Direct emotional statements (should get empathetic response)
                (re.compile(r"(?i)i(?:'m|\s+am)\s+feeling\s+(.+)"), "MoodSearch"),
                (re.compile(r"(?i)i\s+feel\s+(.+)"), "MoodSearch"),
                (re.compile(r"(?i)feeling\s+(.+)"), "MoodSearch"),
                (re.compile(r"(?i)i\s+want\s+to\s+die"), "MoodSearch"),
                (re.compile(r"(?i)i\s+am\s+(sad|depressed|down|upset|angry|mad|happy|excited|tired|stressed|anxious|worried)"), "MoodSearch"),
                (re.compile(r"(?i)i'm\s+(sad|depressed|down|upset|angry|mad|happy|excited|tired|stressed|anxious|worried)"), "MoodSearch"),
                (re.compile(r"(?i)i\s+(hate|love)\s+(.+)"), "MoodSearch"),
                (re.compile(r"(?i)life\s+is\s+(hard|difficult|tough|great|good|bad)"), "MoodSearch"),
                (re.compile(r"(?i)i\s+can't\s+(take|handle)\s+(.+)"), "MoodSearch"),
                # Music requests for specific moods (should get music directly)
                (re.compile(r"(?i)i\s+want\s+to\s+listen\s+to\s+(sad|happy|angry|calm|energetic)\s+(?:songs?|music)"), "DirectMusicSearch"),
                (re.compile(r"(?i)play\s+(sad|happy|angry|calm|energetic)\s+(?:songs?|music)"), "DirectMusicSearch"),
                (re.compile(r"(?i)find\s+(sad|happy|angry|calm|energetic)\s+(?:songs?|music)"), "DirectMusicSearch")
            ],
            "activity_patterns": [
                (re.compile(r"(?i)music\s+for\s+(.+)"), "ActivitySearch"),
                (re.compile(r"(?i)songs?\s+for\s+(.+)"), "ActivitySearch"),
                (re.compile(r"(?i)playlist\s+for\s+(.+)"), "ActivitySearch"),
                (re.compile(r"(?i)i\s+want\s+to\s+(study|workout|work|relax|sleep|dance|party|exercise|focus|concentrate)"), "ActivitySearch"),
                (re.compile(r"(?i)i\s+need\s+to\s+(study|workout|work|relax|sleep|dance|party|exercise|focus|concentrate)"), "ActivitySearch"),
                (re.compile(r"(?i)want\s+to\s+(study|workout|work|relax|sleep|dance|party|exercise|focus|concentrate)"), "ActivitySearch"),
                (re.compile(r"(?i)need\s+to\s+(study|workout|work|relax|sleep|dance|party|exercise|focus|concentrate)"), "ActivitySearch")
            ]
        }

        # Initialize keyword dictionaries
        self.initialize_keywords()

    def initialize_keywords(self):
        """Initialize keyword dictionaries for intent matching"""
        self.mood_keywords = {
            "happy": ["happy", "joyful", "cheerful", "excited", "good", "great", "amazing", "wonderful", "fantastic", "love", "loving"],
            "sad": ["sad", "down", "depressed", "blue", "unhappy", "melancholic", "die", "death", "hurt", "pain", "crying", "tears", "lonely", "empty", "hopeless", "worthless", "hate", "hating"],
            "energetic": ["energetic", "pumped", "energized", "active", "hyped", "motivated"],
            "calm": ["calm", "peaceful", "relaxed", "chill", "tranquil", "serene"],
            "romantic": ["romantic", "love", "dreamy", "passionate", "loving"],
            "angry": ["angry", "mad", "furious", "rage", "aggressive", "frustrated", "annoyed", "pissed", "irritated"]
        }

        self.activity_keywords = {
            "studying": ["study", "studying", "focus", "concentrate", "homework", "want to study", "need to study", "i want to study"],
            "workout": ["workout", "exercise", "gym", "training", "running", "want to workout", "need to workout", "i want to workout", "want to exercise"],
            "relaxation": ["relax", "meditation", "sleep", "rest", "chill", "want to relax", "need to relax", "want to sleep"],
            "party": ["party", "celebration", "dance", "dancing", "fun", "want to party", "want to dance"],
            "work": ["work", "working", "office", "productivity", "want to work"],
            "gaming": ["gaming", "game", "playing", "want to game"]
        }

        self.genre_keywords = {
            "rock": ["rock", "metal", "alternative", "indie"],
            "pop": ["pop", "popular"],
            "jazz": ["jazz", "blues", "swing"],
            "classical": ["classical", "orchestra", "symphony"],
            "electronic": ["electronic", "edm", "techno", "house"],
            "hip-hop": ["hip-hop", "rap", "hip hop", "trap"]
        }

    def detect_intent(self, text, conversation_id="default"):
        """
        Detect intent from user input with enhanced pattern matching and context awareness
        """
        text = text.lower().strip()
        
        # Check context for continuous conversation
        current_context = self.conversation_context[conversation_id]
        
        # 1. Check for Greeting
        if self._is_greeting(text):
            self.last_intent = "Greeting"
            return {"intent": "Greeting", "entity": None, "context": current_context}

        # 2. Check for Song Search
        song_info = self._match_song_patterns(text)
        if song_info:
            self.last_intent = "SongSearch"
            return song_info

        # 3. Check for Artist Search
        artist_info = self._match_artist_patterns(text)
        if artist_info:
            self.last_intent = "ArtistSearch"
            return artist_info

        # 4. Check for Mood
        mood_info = self._match_mood_patterns(text)
        if mood_info:
            self.last_intent = "MoodSearch"
            return mood_info

        # 5. Check for Activity
        activity_info = self._match_activity_patterns(text)
        if activity_info:
            self.last_intent = "ActivitySearch"
            return activity_info

        # 6. Check for Genre
        genre_info = self._match_genre(text)
        if genre_info:
            self.last_intent = "GenreSearch"
            return genre_info

        # 7. Check for Feedback in context
        if current_context in ["songProvided", "artistProvided", "moodProvided"]:
            feedback_info = self._match_feedback(text)
            if feedback_info:
                return feedback_info

        # 8. Check for Help
        if self._is_help_request(text):
            return {"intent": "Help", "entity": None, "context": current_context}

        # Fallback to general chat
        return {"intent": "Chat", "entity": text, "context": current_context}

    def _is_greeting(self, text):
        """Check if text is a greeting"""
        greeting_words = set(['hi', 'hello', 'hey', 'hola', 'greetings', 'good morning', 
                            'good afternoon', 'good evening'])
        return text.split()[0] in greeting_words

    def _match_song_patterns(self, text):
        """Enhanced song pattern matching"""
        for pattern, intent_type in self.patterns["song_patterns"]:
            match = pattern.search(text)  # Use search instead of match
            if match:
                groups = match.groups()
                if len(groups) == 2:  # Song and artist specified
                    return {
                        "intent": "SongSearch",
                        "entity": groups[0].strip(),
                        "artist": groups[1].strip(),
                        "context": "songSearch"
                    }
                elif len(groups) == 1:  # Only song specified
                    song_title = groups[0].strip()
                    # Clean up common phrases
                    song_title = re.sub(r'\b(?:the\s+song\s+)?(?:from|by)\s+', '', song_title, flags=re.IGNORECASE)
                    return {
                        "intent": "SongSearch",
                        "entity": song_title,
                        "context": "songSearch"
                    }
        return None

    def _match_artist_patterns(self, text):
        """Enhanced artist pattern matching"""
        for pattern, intent_type in self.patterns["artist_patterns"]:
            match = pattern.search(text)  # Use search instead of match
            if match:
                artist = match.group(1).strip()
                # Handle cases like "LiSA" vs "LISA"
                normalized_artist = self._normalize_artist_name(artist)
                return {
                    "intent": "ArtistSearch",
                    "entity": normalized_artist,
                    "context": "artistSearch"
                }
        return None

    def _normalize_artist_name(self, artist):
        """Normalize artist names for better matching"""
        # Special cases like "LiSA", "SZA", etc.
        special_cases = {
            "lisa": "LiSA",
            "sza": "SZA",
            "ac/dc": "AC/DC",
        }
        
        normalized = artist.lower()
        if normalized in special_cases:
            return special_cases[normalized]
        
        return artist

    def _match_mood_patterns(self, text):
        """Enhanced mood pattern matching"""
        print(f"[DEBUG] Checking mood patterns for: '{text}'")
        for pattern, intent_type in self.patterns["mood_patterns"]:
            match = pattern.search(text)  # Use search instead of match
            if match:
                print(f"[DEBUG] Matched pattern: {pattern.pattern}")
                # Check if this is a direct music request first
                if "i want to listen to" in text.lower() and any(mood in text.lower() for mood in ["sad", "happy", "angry", "calm", "energetic"]):
                    # Extract the mood from the text
                    for mood in ["sad", "happy", "angry", "calm", "energetic"]:
                        if mood in text.lower():
                            print(f"[DEBUG] Detected DirectMusicSearch for mood: {mood}")
                            return {
                                "intent": "DirectMusicSearch",
                                "entity": mood,
                                "original_mood": text,
                                "context": "directMusicSearch"
                            }
                
                # Handle specific emotional statements
                if "want to die" in text.lower():
                    print(f"[DEBUG] Detected MoodSearch: want to die -> sad")
                    return {
                        "intent": "MoodSearch",
                        "entity": "sad",
                        "original_mood": "want to die",
                        "context": "moodSearch"
                    }
                elif "life is" in text.lower():
                    if any(word in text.lower() for word in ["hard", "difficult", "tough", "bad"]):
                        print(f"[DEBUG] Detected MoodSearch: life is hard -> sad")
                        return {
                            "intent": "MoodSearch",
                            "entity": "sad",
                            "original_mood": text,
                            "context": "moodSearch"
                        }
                    elif any(word in text.lower() for word in ["great", "good", "amazing"]):
                        print(f"[DEBUG] Detected MoodSearch: life is good -> happy")
                        return {
                            "intent": "MoodSearch",
                            "entity": "happy",
                            "original_mood": text,
                            "context": "moodSearch"
                        }
                elif "can't take" in text.lower() or "can't handle" in text.lower():
                    print(f"[DEBUG] Detected MoodSearch: can't take -> sad")
                    return {
                        "intent": "MoodSearch",
                        "entity": "sad",
                        "original_mood": text,
                        "context": "moodSearch"
                    }
                elif len(match.groups()) >= 1:
                    mood = match.group(1).strip()
                    detected_mood = self._categorize_mood(mood)
                    print(f"[DEBUG] Pattern matched mood: '{mood}' -> categorized as: '{detected_mood}'")
                    if detected_mood:
                        return {
                            "intent": "MoodSearch",
                            "entity": detected_mood,
                            "original_mood": mood,
                            "context": "moodSearch"
                        }
                else:
                    # For patterns without groups, categorize the whole text
                    detected_mood = self._categorize_mood(text)
                    print(f"[DEBUG] No groups in pattern, categorizing whole text as: '{detected_mood}'")
                    if detected_mood:
                        return {
                            "intent": "MoodSearch",
                            "entity": detected_mood,
                            "original_mood": text,
                            "context": "moodSearch"
                        }
        print(f"[DEBUG] No mood patterns matched for: '{text}'")
        return None

    def _match_activity_patterns(self, text):
        """Enhanced activity pattern matching"""
        for pattern, intent_type in self.patterns["activity_patterns"]:
            match = pattern.search(text)  # Use search instead of match
            if match:
                if len(match.groups()) >= 1:
                    activity = match.group(1).strip()
                    detected_activity = self._categorize_activity(activity)
                    if detected_activity:
                        return {
                            "intent": "ActivitySearch",
                            "entity": detected_activity,
                            "original_activity": activity,
                            "context": "activitySearch"
                        }
                else:
                    # For patterns that capture the activity directly
                    # Check if the text contains activity keywords
                    for activity, keywords in self.activity_keywords.items():
                        if any(keyword in text.lower() for keyword in keywords):
                            return {
                                "intent": "ActivitySearch", 
                                "entity": activity,
                                "original_activity": text,
                                "context": "activitySearch"
                            }
        return None

    def _match_genre(self, text):
        """Match genre-related queries"""
        for genre, keywords in self.genre_keywords.items():
            if any(keyword in text for keyword in keywords):
                return {
                    "intent": "GenreSearch",
                    "entity": genre,
                    "context": "genreSearch"
                }
        return None

    def _match_feedback(self, text):
        """Match user feedback on previous results"""
        positive_feedback = ["good", "great", "perfect", "yes", "like", "love", "awesome"]
        negative_feedback = ["bad", "no", "don't like", "not", "different", "other"]
        
        is_positive = any(word in text for word in positive_feedback)
        is_negative = any(word in text for word in negative_feedback)
        
        if is_positive or is_negative:
            return {
                "intent": "Feedback",
                "entity": "positive" if is_positive else "negative",
                "context": "feedback"
            }
        return None

    def _is_help_request(self, text):
        """Check if text is a help request"""
        help_keywords = ["help", "how", "what can you", "guide", "explain"]
        return any(keyword in text for keyword in help_keywords)

    def _categorize_mood(self, mood_text):
        """Categorize mood text into predefined categories"""
        for mood, keywords in self.mood_keywords.items():
            if any(keyword in mood_text for keyword in keywords):
                return mood
        return "general"  # Default mood category

    def _categorize_activity(self, activity_text):
        """Categorize activity text into predefined categories"""
        activity_text = activity_text.lower()
        
        # Direct activity mapping
        direct_mapping = {
            "study": "studying",
            "studying": "studying", 
            "focus": "studying",
            "concentrate": "studying",
            "homework": "studying",
            "workout": "workout",
            "exercise": "workout",
            "gym": "workout",
            "training": "workout",
            "running": "workout",
            "relax": "relaxation",
            "relaxation": "relaxation",
            "meditation": "relaxation",
            "sleep": "relaxation",
            "rest": "relaxation",
            "chill": "relaxation",
            "party": "party",
            "celebration": "party",
            "dance": "party",
            "dancing": "party",
            "fun": "party",
            "work": "work",
            "working": "work",
            "office": "work",
            "productivity": "work",
            "gaming": "gaming",
            "game": "gaming",
            "playing": "gaming"
        }
        
        if activity_text in direct_mapping:
            return direct_mapping[activity_text]
                
        # Fallback to keyword matching
        for activity, keywords in self.activity_keywords.items():
            if any(keyword in activity_text for keyword in keywords):
                return activity
        return "general"  # Default activity category

    def update_context(self, conversation_id, context):
        """Update conversation context"""
        self.conversation_context[conversation_id] = context

    def get_context(self, conversation_id):
        """Get current conversation context"""
        return self.conversation_context[conversation_id]

    def clear_context(self, conversation_id):
        """Clear conversation context"""
        self.conversation_context[conversation_id] = ""
        self.last_intent = None