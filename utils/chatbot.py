# utils/chatbot.py
import pickle
import os

class Chatbot:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "..", "models", "chatbot_model.pkl")
        with open(model_path, "rb") as f:
            self.chat_pairs = pickle.load(f)

    def get_response(self, user_input):
        return self.chat_pairs.get(user_input, "I'm not sure how to respond to that. Tell me how you are feeling, and I can find some music for you.")