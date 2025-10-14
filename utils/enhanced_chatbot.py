import pickle
import os
import json
import random
import re
from datetime import datetime
from collections import deque

class EnhancedChatbot:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "..", "models", "chatbot_model.pkl")
        emotion_path = os.path.join(script_dir, "..", "data", "emotion_responses.json")
        
        # Load chatbot model
        try:
            with open(model_path, "rb") as f:
                self.chat_pairs = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Chatbot model not found at {model_path}. Please run the training script.")
            
        # Load emotion responses
        try:
            with open(emotion_path, "rb") as f:
                self.emotion_responses = json.load(f)["moods"]
        except FileNotFoundError:
            print(f"Warning: Emotion responses not found at {emotion_path}")
            self.emotion_responses = {}
        
        self.conversation_history = deque(maxlen=10)  # Keep last 10 messages for context
        self.session_start = datetime.now()
        self.last_intent = None
        self.last_emotion = None
        self.context = {}

    def _preprocess_input(self, user_input):
        """Normalize and preprocess user input."""
        return user_input.lower().strip()

    def _find_best_match(self, user_input):
        """Find the best matching response using improved pattern matching."""
        normalized_input = self._preprocess_input(user_input)
        
        # Exact match
        if normalized_input in self.chat_pairs:
            return self.chat_pairs[normalized_input]
        
        # Partial match
        best_match = None
        max_overlap = 0
        
        for pattern in self.chat_pairs.keys():
            words = set(normalized_input.split())
            pattern_words = set(pattern.split())
            overlap = len(words.intersection(pattern_words))
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = pattern
        
        if best_match and max_overlap >= 1:  # At least one word matches
            return self.chat_pairs[best_match]
        
        return None

    def get_response(self, user_input, intent=None, emotion=None):
        """Get a response based on user input, emotion and conversation context."""
        # Update conversation history and context
        self.conversation_history.append(("user", user_input))
        self.last_intent = intent
        self.last_emotion = emotion

        # Check for greeting patterns first
        greeting_patterns = [
            r'\b(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))\b',
            r'\b(howdy|what\'?s\s+up|how\s+are\s+you)\b',
            r'\b(nice\s+to\s+meet\s+you|pleased\s+to\s+meet\s+you)\b'
        ]

        is_greeting = any(re.search(pattern, user_input.lower()) for pattern in greeting_patterns)

        # If it's a greeting, use greeting responses
        if is_greeting and "greeting" in self.emotion_responses:
            response = random.choice(self.emotion_responses["greeting"]["responses"])
            self.conversation_history.append(("bot", response))
            return response

        # If we have a detected emotion and emotion responses, prioritize those
        if emotion and emotion in self.emotion_responses:
            response = random.choice(self.emotion_responses[emotion]["responses"])
            self.conversation_history.append(("bot", response))
            return response

        # Otherwise proceed with normal response selection
        responses = self._find_best_match(user_input)
        
        if responses:
            # Get contextually appropriate response
            response = self._select_contextual_response(responses)
        else:
            # Fallback responses based on context
            if self.last_intent:
                response = self._get_intent_based_fallback()
            else:
                response = self._get_general_fallback()

        # Update history with bot response
        self.conversation_history.append(("bot", response))
        return response

    def _select_contextual_response(self, responses):
        """Select the most appropriate response based on conversation context."""
        import random
        
        if not isinstance(responses, list):
            responses = [responses]
            
        # If we have conversation history, try to select a response that hasn't been used recently
        if self.conversation_history:
            recent_responses = set(msg[1] for msg in self.conversation_history if msg[0] == "bot")
            new_responses = [r for r in responses if r not in recent_responses]
            if new_responses:
                return random.choice(new_responses)

        return random.choice(responses)

    def _get_intent_based_fallback(self):
        """Get a fallback response based on the last detected intent."""
        intent_fallbacks = {
            "GREETING": "Hello! How can I help you find some music today?",
            "QUESTION": "I'll try my best to help. What kind of music are you looking for?",
            "ARTIST": "I can help you find music by your favorite artists. Who would you like to listen to?",
            "SONG": "I can help you find specific songs. What song are you looking for?",
            "MOOD": "Tell me more about how you're feeling, and I'll find the perfect music for you.",
            "ACTIVITY": "I can suggest music for different activities. What are you planning to do?"
        }
        
        return intent_fallbacks.get(self.last_intent, self._get_general_fallback())

    def _get_general_fallback(self):
        """Get a general fallback response."""
        fallbacks = [
            "I'm here to help you find music. Tell me what you'd like to listen to!",
            "Not quite sure what you mean. Would you like to find a specific song, artist, or mood-based playlist?",
            "I can help you find music based on your mood or activity. What interests you?",
            "Let me know if you want to find songs by a specific artist or for a particular mood."
        ]
        import random
        return random.choice(fallbacks)

    def get_conversation_summary(self):
        """Get a summary of the current conversation."""
        return {
            "session_duration": (datetime.now() - self.session_start).seconds,
            "message_count": len(self.conversation_history),
            "last_intent": self.last_intent,
            "context": self.context
        }