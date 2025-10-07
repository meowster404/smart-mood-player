# Smart Mood Player 🎵

A desktop application that intelligently recommends Spotify songs based on your current mood, detected from either text or voice input.

## Features ✨

* **Mood Detection**: Utilizes a Natural Language Processing (NLP) model to analyze your text and determine your mood.
* **Voice Input**: Speak your mood directly into the app using the built-in voice-to-text feature.
* **Spotify Integration**: Fetches personalized song recommendations from Spotify's vast library that match your emotional state.
* **Interactive UI**: A simple and clean user interface built with Tkinter to chat and manage your playlist.
* **Song Previews**: Listen to 30-second previews of recommended songs directly within the application.
* **Open in Spotify**: Instantly open the full song in your web browser if a preview isn't available.

## How It Works ⚙️

1.  The user enters text or uses the microphone to describe their feelings.
2.  The input text is processed by a pre-trained scikit-learn NLP model to predict the primary emotion (e.g., joy, sadness, anger).
3.  Based on the detected mood, the application queries the Spotify API for song recommendations with specific audio features (like valence, energy, and tempo) that match the mood.
4.  A playlist of recommended songs is displayed in the GUI.
5.  The user can select a song to hear a preview, which is streamed and played using Pygame.

## Setup and Installation 🚀

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

* Python 3.7+
* A Spotify Developer account to get API credentials.

### 2. Clone the Repository

```bash
git clone [https://github.com/meowster404/smart-mood-player.git](https://github.com/meowster404/smart-mood-player.git)
cd smart-mood-player