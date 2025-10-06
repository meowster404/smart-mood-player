# utils/nlp_mood_detector.py
import joblib

class NlpMoodDetector:
    def __init__(self, model_path="models/emotion_classifier.pkl"):
        # Load the pre-trained model
        self.model = joblib.load(open(model_path, "rb"))
        print("✅ NLP Mood Detector has been loaded.")

    def predict_mood(self, user_text: str) -> str:
        """Predicts the mood from a user's text input using the loaded NLP model."""
        prediction = self.model.predict([user_text])
        return prediction[0]