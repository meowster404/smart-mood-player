# utils/nlp_mood_detector.py
import joblib
import os

class NlpMoodDetector:
    def __init__(self, model_path="smart-mood-player/models/emotion_classifier.pkl"):
        """
        Loads the pre-trained NLP model.
        Assumes the script is run from the project's root directory.
        """
        # --- Simplified Path ---
        # This path is now relative to the project's root directory.
        if not os.path.exists(model_path):
            print(f"❌ MODEL NOT FOUND at '{model_path}'")
            print("Please ensure you have trained the model by running the train_model.py script.")
            # Re-raise the exception to stop the application from running without the model
            raise FileNotFoundError(f"Model not found at {model_path}")
            
        try:
            self.model = joblib.load(model_path)
            print("✅ NLP Mood Detector has been loaded.")
        
        except Exception as e:
            print(f"❌ An error occurred while loading the model: {e}")
            raise

    def predict_mood(self, user_text: str) -> str:
        """Predicts the mood from a user's text input using the loaded NLP model."""
        if not hasattr(self, 'model'):
             return "Error: Model not loaded"
        prediction = self.model.predict([user_text])
        return prediction[0]