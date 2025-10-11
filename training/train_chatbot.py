# training/train_chatbot.py

import os
import pickle

# Get the directory of the current script (e.g., .../training/)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (the project root, e.g., .../smart-mood-player/)
project_root = os.path.dirname(script_dir)

# Define paths relative to the project root
DATA_PATH = os.path.join(project_root, "data", "dialogs.txt")
MODEL_DIR = os.path.join(project_root, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "chatbot_model.pkl")

# Create models directory if it doesn't exist
os.makedirs(MODEL_DIR, exist_ok=True)

print("🚀 Starting training for the chatbot model...")

# Create a dictionary to store the dialogs
dialogs = {}

# Read the dialogs from the file
try:
    with open(DATA_PATH, "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                dialogs[parts[0]] = parts[1]
except FileNotFoundError:
    print(f"Error: The dataset was not found at {DATA_PATH}")
    print("Please make sure the 'dialogs.txt' file is in the 'data' directory.")
    exit()

# Save the dialogs dictionary as a model
with open(MODEL_PATH, "wb") as f:
    pickle.dump(dialogs, f)

print(f"✅ Chatbot model trained and saved as {MODEL_PATH}")