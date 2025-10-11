# train_model.py

import subprocess
import sys
import os

def run_script(script_name):
    """Runs a Python script located in the 'training' directory and checks for errors."""
    script_path = os.path.join("training", script_name)
    try:
        print(f"--- Running {script_path} ---")
        subprocess.run([sys.executable, script_path], check=True)
        print(f"--- Finished {script_path} ---\n")
    except FileNotFoundError:
        print(f"❌ Error: Script not found at {script_path}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting all training processes...\n")

    run_script("train_emotion_classifier.py")
    run_script("train_chatbot.py")
    run_script("train_intent_detector.py") # This script just prints info

    print("✅ All training processes completed successfully!")