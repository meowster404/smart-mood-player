# utils/chatbot.py
import pickle
import os
import random

class Chatbot:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "..", "models", "chatbot_model.pkl")
        try:
            with open(model_path, "rb") as f:
                self.chat_pairs = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Chatbot model not found at {model_path}. Please run the training script.")

    def get_response(self, user_input):
        """
        Finds a response for the user's input.
        If an exact match is found, returns a random response from the list.
        Otherwise, returns a default message.
        """
        # Normalize user input to match the keys in our model
        user_input_normalized = user_input.lower()

        # Get the list of possible responses for the input
        possible_responses = self.chat_pairs.get(user_input_normalized)

        if possible_responses:
            # If responses are found, pick one at random
            return random.choice(possible_responses)
        else:
            # Fallback response if no match is found
            return "I'm not sure how to respond to that. Tell me how you are feeling, and I can find some music for you."