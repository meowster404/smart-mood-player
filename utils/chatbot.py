# utils/chatbot.py

import joblib
import os
import random

class Chatbot:
    def __init__(self, model_path="smart-mood-player/models/chatbot_model.pkl"):
        """
        Loads the pre-trained chatbot model (a dictionary of conversation pairs).
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Chatbot model not found at '{model_path}'. "
                f"Please run train_chatbot.py to create the model."
            )
        
        self.model = joblib.load(model_path)
        print("🤖 Chatbot model loaded successfully.")

    def get_response(self, user_text):
        """
        Finds a response for the user's text from the model.
        """
        # Convert user input to lowercase to match the keys in our model
        user_text_lower = user_text.lower()
        
        # Check if the exact user text exists as a key in our model
        if user_text_lower in self.model:
            # If there are multiple possible responses, pick one at random
            return random.choice(self.model[user_text_lower])
        else:
            # Provide a fallback response if the model doesn't recognize the input
            return "I'm not sure how to respond to that. Try asking something else."