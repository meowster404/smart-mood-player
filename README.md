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
git clone [https://github.com/meowster404/smart-mood-player.git](https://github.com/meowster404/smart-mood-player.git)
cd smart-mood-player