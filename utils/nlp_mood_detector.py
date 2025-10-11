# utils/nlp_mood_detector.py
import joblib
import os

# Get the absolute path to the directory containing this script (utils)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one directory to the project root
project_root = os.path.dirname(script_dir)
# Construct the correct model path
DEFAULT_MODEL_PATH = os.path.join(project_root, "models", "emotion_classifier.pkl")

class NlpMoodDetector:
    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        """
        Loads the pre-trained NLP model using a robust path.
        """
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