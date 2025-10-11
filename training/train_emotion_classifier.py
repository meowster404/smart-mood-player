# training/train_emotion_classifier.py

import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import neattext.functions as nfx

# Get the directory of the current script (e.g., .../training/)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (the project root, e.g., .../smart-mood-player/)
project_root = os.path.dirname(script_dir)

# Define paths relative to the project root
DATA_PATH = os.path.join(project_root, "data", "emotion_dataset_raw.csv")
MODEL_DIR = os.path.join(project_root, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "emotion_classifier.pkl")

# Create models directory if it doesn't exist
os.makedirs(MODEL_DIR, exist_ok=True)

print("🚀 Starting training for the emotion classifier model...")

# Load the dataset
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    print(f"Error: The dataset was not found at {DATA_PATH}")
    print("Please make sure the 'emotion_dataset_raw.csv' file is in the 'data' directory.")
    exit()

# Data Cleaning
df['Clean_Text'] = df['Text'].apply(nfx.remove_userhandles)
df['Clean_Text'] = df['Clean_Text'].apply(nfx.remove_stopwords)

# Features and Labels
Xfeatures = df['Clean_Text']
ylabels = df['Emotion']

# Create a pipeline
pipeline = Pipeline(steps=[
    ('cv', CountVectorizer()),
    ('lr', LogisticRegression(max_iter=1000))
])

# Train the model
pipeline.fit(Xfeatures, ylabels)

# Save the model
with open(MODEL_PATH, "wb") as f:
    joblib.dump(pipeline, f)

print(f"✅ Emotion classifier model trained and saved as {MODEL_PATH}")