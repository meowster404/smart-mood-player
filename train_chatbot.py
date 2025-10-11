# train_chatbot.py

import os
import joblib

def train_chatbot_model(data_path="smart-mood-player/data/dialogs.txt", model_dir="smart-mood-player/models"):
    """
    Processes the dialogs.txt file and creates a simple conversational model.
    The model is a dictionary mapping user inputs to potential bot responses.
    """
    print("🤖 Starting chatbot model training...")

    # Ensure the models directory exists
    os.makedirs(model_dir, exist_ok=True)
    MODEL_PATH = os.path.join(model_dir, "chatbot_model.pkl")

    # This dictionary will store our conversational pairs
    conversation_dict = {}

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Clean and skip empty lines
                line = line.strip()
                if not line or ':' not in line:
                    continue

                # Split the line into user message and bot response
                parts = line.split(":", 1)
                user_message = parts[0].strip().lower()
                bot_response = parts[1].strip()

                # Store the response. A single input can have multiple potential responses.
                if user_message not in conversation_dict:
                    conversation_dict[user_message] = []
                conversation_dict[user_message].append(bot_response)

    except FileNotFoundError:
        print(f"❌ Error: The data file was not found at '{data_path}'. Make sure 'dialogs.txt' is in the project root.")
        return
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return

    if not conversation_dict:
        print("⚠️ No conversational data was loaded. The model will be empty.")
        return

    print(f"✅ Processed {len(conversation_dict)} unique conversational prompts.")

    # Save the conversation dictionary as our "model"
    print(f"💾 Saving chatbot model to {MODEL_PATH}")
    joblib.dump(conversation_dict, MODEL_PATH)
    print("✨ Chatbot model saved successfully!")

    # --- Verification Step ---
    print("\n--- Model Verification ---")
    reloaded_model = joblib.load(MODEL_PATH)
    test_text = "hi, how are you doing?"  # A known prompt from your dialogs.txt
    if test_text in reloaded_model:
        print(f"🧪 Test: '{test_text}'")
        print(f"↪ Possible Responses: {reloaded_model[test_text]}")
    else:
        print(f"⚠️ Test prompt '{test_text}' not found in the model.")


if __name__ == "__main__":
    # Ensure you run this from the root directory where dialogs.txt is located
    train_chatbot_model(data_path="dialogs.txt")
