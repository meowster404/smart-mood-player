# utils/nlp_mood_detector.py
import joblib
import os

class NlpMoodDetector:
    def __init__(self, model_path="models/emotion_classifier.pkl"):
        """
        Loads the pre-trained NLP model.
        The path is constructed relative to this script's location
        to avoid 'FileNotFoundError' when run from different directories.
        """
        try:
            # Get the absolute path to the directory containing this script (utils/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one directory to the project root (smart-mood-player/)
            project_root = os.path.dirname(script_dir)
            # Join the root path with the relative model path
            absolute_model_path = os.path.join(project_root, model_path)

            # Load the model using the correct, absolute path
            self.model = joblib.load(open(absolute_model_path, "rb"))
            print("✅ NLP Mood Detector has been loaded.")
        
        except FileNotFoundError:
            print(f"❌ MODEL NOT FOUND at '{absolute_model_path}'")
            print("Please ensure you have trained the model by running the train_model.py script.")
            # Re-raise the exception to stop the application from running without the model
            raise

    def predict_mood(self, user_text: str) -> str:
        """Predicts the mood from a user's text input using the loaded NLP model."""
        prediction = self.model.predict([user_text])
        return prediction[0]