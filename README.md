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

## How It Works 🤖

The Smart Music Player uses **Machine Learning** and **Natural Language Processing** to understand your emotions and recommend music that matches your mood.

### ML-Powered Mood Detection

1. **Input Analysis** 🎤
   - You type a message or speak into the microphone
   - Voice input is converted to text using speech recognition

2. **AI Mood Detection** 🧠
   - **Trained ML Model** analyzes your text using Natural Language Processing
   - **Emotion Classification** identifies your emotional state (happy, sad, angry, calm, excited, etc.)
   - **Context-Aware Analysis** considers conversation history and emotional context

3. **Intelligent Processing** ⚡
   - **Pattern Matching** detects specific requests (songs, artists, activities)
   - **ML Mood Integration** uses AI-detected emotions for music selection
   - **Hybrid Approach** combines rule-based intent detection with ML mood analysis

4. **Smart Music Discovery** 🎵
   - **Emotion-Based Search** finds playlists matching your detected mood
   - **Spotify API Integration** accesses millions of songs and playlists
   - **Personalized Recommendations** based on your emotional state

### Example ML Mood Detection

```
Input: "I'm feeling really happy today!"
AI Analysis: "happy" mood detected
Result: Upbeat, joyful music playlists

Input: "I'm so stressed and tired"
AI Analysis: "sadness" + "tired" mood detected  
Result: Calming, relaxing music playlists

Input: "Play Faded by Alan Walker"
Pattern Match: "SongSearch" intent detected
Result: Direct song search (no mood analysis needed)
```

### Technical Architecture

- **Frontend**: Modern CustomTkinter GUI with real-time interaction
- **AI Core**: Machine Learning model for emotion classification
- **Backend**: Multi-threaded processing for responsive user experience
- **External APIs**: Spotify Web API for music data access
- **Analytics**: Performance tracking and mood detection accuracy monitoring

The system intelligently combines traditional pattern matching with advanced ML mood detection to provide the most accurate music recommendations possible!

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

This project is released under a **Creative Commons Attribution License**.

You are free to:
- **Use** this code for any purpose (personal, educational, or commercial)
- **Modify** and adapt the code as needed
- **Share** your modifications with others

**The only requirement is that you must give appropriate credit to the original author and mention that this is based on the Smart Music Player project.**

### Attribution Format:
```
Based on "Smart Music Player" by [Your Name/Username]
Original project: https://github.com/meowster404/smart-mood-player
```

**Note**: This is an educational project created to demonstrate music recommendation systems using NLP and the Spotify API. Feel free to learn from it and build upon it!

## Acknowledgments 🙏

- Spotify Web API for music data
- CustomTkinter for the modern UI
- NLTK and scikit-learn for NLP capabilities
- The open-source community for various dependencies

---

**Note**: This application requires an active internet connection to access the Spotify Web API. Make sure to handle your API credentials securely and never commit them to version control.