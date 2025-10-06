# backend.py
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils.nlp_mood_detector import NlpMoodDetector
from utils.spotify_utils import get_spotify_client, get_spotify_recommendations

# Load environment variables
load_dotenv()

# Initialize Flask app and other components
app = Flask(__name__)
mood_detector = NlpMoodDetector(model_path="models/emotion_classifier.pkl")
spotify_client = get_spotify_client()

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    """
    API endpoint to get music recommendations based on user text.
    Expects a JSON payload with a "text" key.
    e.g., {"text": "I'm feeling very happy today"}
    """
    # Get the user's text from the request
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid input, "text" field is required.'}), 400

    user_text = data['text']

    # Ensure the Spotify client is available
    if not spotify_client:
        return jsonify({'error': 'Spotify client not initialized. Check server logs.'}), 500

    try:
        # 1. Predict the mood from the text
        predicted_mood = mood_detector.predict_mood(user_text)

        # 2. Get track recommendations from Spotify
        tracks = get_spotify_recommendations(spotify_client, predicted_mood)

        # 3. Return the results as JSON
        return jsonify({
            'mood': predicted_mood,
            'tracks': tracks
        })
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

if __name__ == '__main__':
    # Run the Flask server
    app.run(host='0.0.0.0', port=5000)