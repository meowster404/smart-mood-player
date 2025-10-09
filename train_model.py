# train_model.py

import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import neattext.functions as nfx

# Get the absolute path to the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one directory to the project root
project_root = os.path.dirname(script_dir)

# Define paths relative to the project root
DATA_PATH = os.path.join(project_root, "data", "emotion_dataset_raw.csv")
MODEL_DIR = os.path.join(project_root, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "emotion_classifier.pkl")

# Create models directory if it doesn't exist
os.makedirs(MODEL_DIR, exist_ok=True)

# Load the dataset
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    print(f"Error: The dataset was not found at {DATA_PATH}")
    print("Please make sure the 'emotion_dataset_raw.csv' file is in the correct directory.")
    exit()


# Data Cleaning
df['Clean_Text'] = df['Text'].apply(nfx.remove_userhandles)
df['Clean_Text'] = df['Clean_Text'].apply(nfx.remove_stopwords)

# Features and Labels
Xfeatures = df['Clean_Text']
ylabels = df['Emotion']

# Create a pipeline with CountVectorizer and LogisticRegression
pipeline = Pipeline(steps=[
    ('cv', CountVectorizer()),
    ('lr', LogisticRegression(max_iter=1000)) # Increased max_iter for convergence
])

# Train the model
pipeline.fit(Xfeatures, ylabels)

# Save the model
with open(MODEL_PATH, "wb") as f:
    joblib.dump(pipeline, f)

print(f"✅ Model trained and saved as {MODEL_PATH}")