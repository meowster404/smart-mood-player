# app.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import queue
import io
import pygame
import webbrowser
import requests
from dotenv import load_dotenv

# Import the necessary utilities
from utils.nlp_mood_detector import NlpMoodDetector
from utils.spotify_utils import get_spotify_client, get_spotify_recommendations
from utils.voice_input import SpeechToTextConverter

# Load environment variables from .env file
load_dotenv()

class ChatPlayerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Mood Player")
        self.root.geometry("800x500")
        self.root.minsize(600, 400)

        pygame.mixer.init()

        # --- Main Layout Frames ---
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.chat_frame = tk.Frame(root, bg="#f0f0f0")
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.player_frame = tk.Frame(root)
        self.player_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.player_frame.grid_rowconfigure(1, weight=1)
        self.player_frame.grid_columnconfigure(0, weight=1)

        # --- Chat Window ---
        self.chat_window = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state='disabled', font=("Helvetica", 11))
        self.chat_window.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # --- Message Input ---
        self.message_entry = tk.Entry(self.chat_frame, font=("Helvetica", 11))
        self.message_entry.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.message_entry.bind("<Return>", self.send_message)
        
        # --- Buttons ---
        self.chat_frame.grid_columnconfigure(0, weight=10) 
        self.chat_frame.grid_columnconfigure(1, weight=1)
        self.chat_frame.grid_columnconfigure(2, weight=1)

        self.voice_button = tk.Button(self.chat_frame, text="🎤", command=self.activate_voice_input, font=("Helvetica", 10))
        self.voice_button.grid(row=1, column=1, sticky="ew", pady=(10, 0), padx=5)
        
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=2, sticky="ew", pady=(10, 0))
        
        # --- Player/Playlist Side ---
        self.playlist_label = tk.Label(self.player_frame, text="🎵 Recommendations", font=("Helvetica", 12, "bold"))
        self.playlist_label.grid(row=0, column=0, sticky="w", pady=5)
        self.playlist_listbox = tk.Listbox(self.player_frame, height=15, selectbackground="#c3c3c3")
        self.playlist_listbox.grid(row=1, column=0, sticky="nsew")
        self.play_button = tk.Button(self.player_frame, text="▶️ Play Selected Song", command=self.play_selected_song, state=tk.DISABLED)
        self.play_button.grid(row=2, column=0, sticky="ew", pady=10)

        # --- Backend Logic Initialization ---
        self.spotify_queue = queue.Queue()
        self.mood_detector = NlpMoodDetector()
        self.speech_converter = SpeechToTextConverter() 
        self.tracks_data = []

        self.add_message("Bot", "Hello! Tell me how you're feeling or what you're in the mood for.")
        self.check_spotify_queue()

    def add_message(self, sender, message):
        self.chat_window.config(state='normal')
        if sender == "You":
            self.chat_window.insert(tk.END, f"You: {message}\n", 'user_tag')
        else:
            self.chat_window.insert(tk.END, f"Bot: {message}\n\n", 'bot_tag')
        self.chat_window.config(state='disabled')
        self.chat_window.yview(tk.END)

    def activate_voice_input(self):
        """Handles the voice input process in a separate thread."""
        self.voice_button.config(state=tk.DISABLED)
        self.add_message("Bot", "Listening...")
        threading.Thread(target=self.voice_input_thread).start()

    def voice_input_thread(self):
        """Recognizes speech and puts the result in the message entry."""
        recognized_text = self.speech_converter.recognize_from_microphone()
        self.voice_button.config(state=tk.NORMAL)
        if recognized_text:
            self.message_entry.delete(0, tk.END)
            self.message_entry.insert(0, recognized_text)
            self.add_message("Bot", f"I heard: '{recognized_text}'. Press Send to get recommendations.")
        else:
            self.add_message("Bot", "I couldn't understand that. Please try again or type your message.")


    def send_message(self, event=None):
        user_input = self.message_entry.get()
        if not user_input:
            return
        
        self.add_message("You", user_input)
        self.message_entry.delete(0, tk.END)
        
        predicted_mood = self.mood_detector.predict_mood(user_input)
        self.add_message("Bot", f"I sense you're feeling '{predicted_mood}'. Searching for music on Spotify...")
        
        self.send_button.config(state=tk.DISABLED)
        threading.Thread(target=self.fetch_spotify_data_thread, args=(predicted_mood,)).start()

    def fetch_spotify_data_thread(self, mood):
        try:
            sp = get_spotify_client()
            tracks = get_spotify_recommendations(sp, mood)
            self.spotify_queue.put(tracks)
        except Exception as e:
            self.spotify_queue.put(f"Error: {e}")

    def check_spotify_queue(self):
        try:
            result = self.spotify_queue.get(block=False)
            self.update_ui_with_results(result)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_spotify_queue)

    def update_ui_with_results(self, result):
        self.send_button.config(state=tk.NORMAL)
        if isinstance(result, str):
            messagebox.showerror("Spotify Error", result)
            self.add_message("Bot", "Sorry, I ran into an error connecting to Spotify.")
            return

        self.tracks_data = result
        self.playlist_listbox.delete(0, tk.END)
        
        if not self.tracks_data:
            self.add_message("Bot", "I couldn't find any tracks for that mood. Please try something else!")
            self.play_button.config(state=tk.DISABLED)
            return

        for track in self.tracks_data:
            self.playlist_listbox.insert(tk.END, f"{track['title']} - {track['artist']}")
        
        self.add_message("Bot", "I've found some songs for you! Select one from the list and press play.")
        self.play_button.config(state=tk.NORMAL)

    def play_selected_song(self):
        selected_indices = self.playlist_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("No Selection", "Please select a song from the list first.")
            return

        selected_track = self.tracks_data[selected_indices[0]]
        preview_url = selected_track.get("preview_url")

        if preview_url:
            try:
                pygame.mixer.music.stop()
                response = requests.get(preview_url, stream=True)
                if response.status_code == 200:
                    pygame.mixer.music.load(io.BytesIO(response.content))
                    pygame.mixer.music.play()
                    self.add_message("Bot", f"▶️ Playing preview: {selected_track['title']}")
                else:
                    messagebox.showerror("Download Error", "Could not fetch the song preview.")
            except Exception as e:
                messagebox.showerror("Playback Error", f"An error occurred: {e}")
        else:
            self.add_message("Bot", "No preview available. Opening full song in browser...")
            webbrowser.open(selected_track["url"])

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatPlayerGUI(root)
    root.mainloop()