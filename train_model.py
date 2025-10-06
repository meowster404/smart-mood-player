# train_model.py
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import neattext.functions as nfx

# Load the dataset
df = pd.read_csv("smart-mood-player\data\emotion_dataset_raw.csv") # Make sure you have this file

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
with open("smart-mood-player\models\emotion_classifier.pkl", "wb") as f:
    joblib.dump(pipeline, f)

print("✅ Model trained and saved as smart-mood-player\models\emotion_classifier.pkl")