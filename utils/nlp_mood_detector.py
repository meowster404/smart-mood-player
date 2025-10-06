# utils/nlp_mood_detector.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

class NlpMoodDetector:
    def __init__(self):
        # A larger, more diverse dataset is needed for a real-world application.
        # This is a sample dataset to demonstrate the functionality.
        data = {
            'text': [
                "I want to party all night",
                "Let's get this workout started",
                "Time to dance!",
                "I feel so happy and cheerful today",
                "This is a joyful moment",
                "I'm feeling really sad",
                "I'm down and need something to cry to",
                "I need to focus on my homework",
                "Playing something to help me relax and study",
                "I need to calm down"
            ],
            'mood': [
                "energetic", "energetic", "energetic",
                "happy", "happy",
                "sad", "sad",
                "calm", "calm", "calm"
            ]
        }
        
        df = pd.DataFrame(data)
        X = df['text']
        y = df['mood']

        # We create a pipeline that first vectorizes the text and then applies the classifier.
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english')),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])

        # Train the model on our sample data
        self.pipeline.fit(X, y)
        print("✅ NLP Mood Detector has been trained.")

    def predict_mood(self, user_text: str) -> str:
        """Predicts the mood from a user's text input using the trained NLP model."""
        predicted_mood = self.pipeline.predict([user_text])
        return predicted_mood[0]