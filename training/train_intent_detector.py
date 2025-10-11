# training/train_intent_detector.py

import json
import os

# Get the directory of the current script (e.g., .../training/)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (the project root, e.g., .../smart-mood-player/)
project_root = os.path.dirname(script_dir)

# Define the path relative to the project root
INTENT_DATA_PATH = os.path.join(project_root, "data", "intent.json")

print("🚀 Analyzing the intent detector...")

# Explain how the intent detector works
print("""
The intent detector is a rule-based system that uses keywords and regular expressions to identify user intents.
It does not require a machine learning model to be trained.

The intents are defined in `data/intent.json`, which contains patterns and keywords for different intents such as:
- Greeting
- Asking questions
- Requesting songs by artist or title
- Requesting songs for a specific activity (e.g., study, workout)

The `utils/intent_detector.py` script contains the logic to match user input against these predefined patterns.
Therefore, no training is necessary for this component.
""")

# Verify that the intent data file exists
if os.path.exists(INTENT_DATA_PATH):
    print(f"✅ Intent data file found at {INTENT_DATA_PATH}")
else:
    # This error message will now show the correct, expected path
    print(f"❌ Error: The intent data file was not found at {INTENT_DATA_PATH}")