# Smart Music Finder 🎵

A smart, conversational desktop app that recommends Spotify music based on your mood, preferred artists, songs, or even your current activity, using both text and voice input.

## Features ✨

* **Advanced Intent Detection**: Understands whether you're asking for a song by title, artist, activity (e.g., "music for studying"), or just expressing a mood.
* **Conversational Chatbot**: For greetings, questions, and general chat, the app provides natural responses.
* **Mood Analysis**: Utilizes a Natural Language Processing (NLP) model to analyze your text and determine your mood for playlist recommendations.
* **Voice Input**: Speak your requests directly into the app using the built-in voice-to-text feature.
* **Spotify Integration**: Fetches personalized playlists and tracks from Spotify's vast library.
* **Modern & Interactive UI**: A clean and modern user interface built with CustomTkinter.
* **Open in Spotify**: Instantly open any found song or playlist in your web browser.

## How It Works ⚙️

1.  **Input**: The user types a message or uses the microphone.
2.  **Intent Analysis**: The app first tries to understand the user's specific *intent* (e.g., find a song, find an artist, or just casual chat).
3.  **Action**:
   * If a specific intent like finding a song is detected, it queries the Spotify API.
   * If the user is just expressing a feeling (e.g., "I'm happy today"), the NLP mood model predicts the emotion and finds suitable playlists.
   * If the user is just chatting (e.g., "hello", "what can you do?"), the retrieval-based chatbot provides a response.
4.  **Display**: The found playlists or tracks are displayed in the right-hand panel, ready to be opened in Spotify.

## Setup and Installation 🚀

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

* Python 3.7+
* A Spotify Developer account to get API credentials.

### 2. Clone the Repository

```bash
git clone https://github.com/meowster404/smart-mood-player.git
cd smart-mood-player
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Spotify API Credentials

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app or use an existing one
3. Copy your Client ID and Client Secret
4. Create a `.env` file in the project root with the following content:

```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### 5. Train the Models (Optional)

If you want to train the models from scratch:

```bash
python train_all_models.py
```

Or train individual models:

```bash
python training/train_emotion_classifier.py
python training/train_intent_detector.py
python training/train_chatbot.py
```

### 6. Run the Application

```bash
python app.py
```

## Usage Examples 💬

### Finding Songs
- "Play Faded by Alan Walker"
- "I want to listen to Shape of You by Ed Sheeran"
- "Find songs by LiSA"

### Mood-based Search
- "I'm feeling happy today"
- "Need some relaxing music"
- "Music for working out"

### Activity-based Search
- "Music for studying"
- "Songs for workout"
- "Playlist for party"

### General Chat
- "Hello"
- "What can you do?"
- "How are you?"

## Project Structure 📁

```
smart-mood-player/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── FEATURES.md           # Detailed feature documentation
├── workflow.md           # Workflow documentation
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore patterns
├── data/                # Training data and configuration
│   ├── dialogs.txt      # Chatbot training data
│   ├── emotion_dataset_raw.csv  # Emotion classification data
│   ├── emotion_responses.json   # Emotion response mappings
│   └── intent.json      # Intent detection patterns
├── models/              # Trained model files
│   ├── chatbot_model.pkl
│   └── emotion_classifier.pkl
├── utils/               # Utility modules
│   ├── enhanced_chatbot.py
│   ├── enhanced_intent_detector.py
│   ├── enhanced_spotify_utils.py
│   ├── nlp_mood_detector.py
│   ├── performance_analyzer.py
│   ├── voice_input.py
│   └── __init__.py
├── training/            # Model training scripts
│   ├── train_chatbot.py
│   ├── train_emotion_classifier.py
│   └── train_intent_detector.py
├── analysis_logs/       # Performance analysis logs
└── test_*.py           # Test scripts
```

## Configuration ⚙️

The application uses several configuration files:

- **`.env`**: Spotify API credentials
- **`data/intent.json`**: Intent detection patterns and responses
- **`data/emotion_responses.json`**: Mood-based response mappings

## Testing 🧪

Run the test scripts to verify functionality:

```bash
python test_functionality.py
python test_spotify.py
python test_song_extraction.py
```

## Performance Analysis 📊

The application includes built-in performance tracking:

- Accuracy metrics for intent detection and mood analysis
- Response time monitoring
- User satisfaction tracking
- Visual analytics in the `analysis_logs/` directory

## Troubleshooting 🔧

### Common Issues

1. **No module found errors**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Spotify API issues**:
   - Verify your `.env` file contains correct credentials
   - Ensure your Spotify app is properly configured in the developer dashboard

3. **Model loading errors**:
   - Run the training scripts to generate the required `.pkl` files
   - Check that all data files are present in the `data/` directory

4. **Voice input not working**:
   - Check microphone permissions
   - Ensure PyAudio and SpeechRecognition are properly installed

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- Spotify Web API for music data
- CustomTkinter for the modern UI
- NLTK and scikit-learn for NLP capabilities
- The open-source community for various dependencies

---

**Note**: This application requires an active internet connection to access the Spotify Web API. Make sure to handle your API credentials securely and never commit them to version control.