# training/train_chatbot.py

import os
import json
import pickle
import random

# Get the directory of the current script (e.g., .../training/)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (the project root, e.g., .../smart-mood-player/)
project_root = os.path.dirname(script_dir)

# Define paths relative to the project root
DIALOGS_PATH = os.path.join(project_root, "data", "dialogs.txt")
INTENT_PATH = os.path.join(project_root, "data", "intent.json")
MODEL_DIR = os.path.join(project_root, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "chatbot_model.pkl")

# Create models directory if it doesn't exist
os.makedirs(MODEL_DIR, exist_ok=True)

print("🚀 Starting training for the chatbot model...")

# Create a dictionary to store the dialogs
dialogs = {}

# 1. Read the dialogs from the .txt file
try:
    with open(DIALOGS_PATH, "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                # Store a list of responses
                if parts[0] not in dialogs:
                    dialogs[parts[0]] = []
                dialogs[parts[0]].append(parts[1])
except FileNotFoundError:
    print(f"Warning: The dataset was not found at {DIALOGS_PATH}")
    print("Please make sure the 'dialogs.txt' file is in the 'data' directory.")

# 2. Read the intents from the .json file
try:
    with open(INTENT_PATH, "r") as f:
        intent_data = json.load(f)
        for intent in intent_data.get("intents", []):
            responses = intent.get("responses")
            if not responses:
                continue
            for text_trigger in intent.get("text", []):
                # Normalize to lowercase for better matching
                trigger_key = text_trigger.lower()
                if trigger_key not in dialogs:
                    dialogs[trigger_key] = []
                # Add all possible responses for this trigger
                dialogs[trigger_key].extend(responses)
except FileNotFoundError:
    print(f"Error: The intent file was not found at {INTENT_PATH}")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode the JSON from {INTENT_PATH}")
    exit()


# Save the dialogs dictionary as a model
with open(MODEL_PATH, "wb") as f:
    pickle.dump(dialogs, f)

print(f"✅ Chatbot model trained with {len(dialogs)} unique triggers and saved as {MODEL_PATH}")