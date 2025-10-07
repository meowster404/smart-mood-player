# app.py (Modern CustomTkinter UI)
import customtkinter as ctk
import threading, queue, io, pygame, requests, webbrowser
from tkinter import messagebox
from dotenv import load_dotenv
from utils.nlp_mood_detector import NlpMoodDetector
from utils.spotify_utils import get_spotify_client, get_spotify_recommendations
from utils.voice_input import SpeechToTextConverter

# Load environment variables
load_dotenv()

# Initialize pygame mixer
pygame.mixer.init()

ctk.set_appearance_mode("dark")      # Options: "dark" / "light"
ctk.set_default_color_theme("green") # Spotify vibe

class SmartMoodPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎧 Smart Mood Player")
        self.geometry("920x560")
        self.minsize(800, 500)

        # Queues
        self.spotify_queue = queue.Queue()
        self.voice_queue = queue.Queue()

        # Backend
        self.mood_detector = NlpMoodDetector()
        self.speech_converter = SpeechToTextConverter()
        self.tracks_data = []

        # Main Layout (2-column grid)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left: Chat Panel
        self.chat_frame = ctk.CTkFrame(self, corner_radius=15)
        self.chat_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(1, weight=0)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(
            self.chat_frame,
            wrap="word",
            font=("Poppins", 13),
            fg_color="#1E1E1E",
            text_color="white",
            corner_radius=10,
            activate_scrollbars=True
        )
        self.chat_display.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=10)
        self.chat_display.insert("end", "🎧 Bot: Hello! Tell me how you're feeling today.\n\n")
        self.chat_display.configure(state="disabled")

        # Message entry + buttons
        self.message_entry = ctk.CTkEntry(
            self.chat_frame,
            placeholder_text="Type how you feel or say 'play relaxing music'...",
            font=("Poppins", 12),
            corner_radius=10
        )
        self.message_entry.grid(row=1, column=0, padx=(10,5), pady=(0,10), sticky="ew")
        self.message_entry.bind("<Return>", self.send_message)

        self.voice_button = ctk.CTkButton(
            self.chat_frame, text="🎙", width=45,
            command=self.activate_voice_input, font=("Poppins", 13, "bold")
        )
        self.voice_button.grid(row=1, column=1, padx=5, pady=(0,10))

        self.send_button = ctk.CTkButton(
            self.chat_frame, text="Send ➤",
            command=self.send_message, font=("Poppins", 13, "bold")
        )
        self.send_button.grid(row=1, column=2, padx=(5,10), pady=(0,10))

        # Right: Player / Playlist Panel
        self.player_frame = ctk.CTkFrame(self, corner_radius=15)
        self.player_frame.grid(row=0, column=1, padx=(0,15), pady=15, sticky="nsew")
        self.player_frame.grid_rowconfigure(1, weight=1)
        self.player_frame.grid_columnconfigure(0, weight=1)

        self.playlist_label = ctk.CTkLabel(
            self.player_frame, text="🎵 Spotify Recommendations",
            font=("Poppins", 16, "bold")
        )
        self.playlist_label.grid(row=0, column=0, pady=(15,10))

        self.playlist_box = ctk.CTkTextbox(
            self.player_frame, height=320, font=("Poppins", 12),
            fg_color="#121212", text_color="white"
        )
        self.playlist_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.play_button = ctk.CTkButton(
            self.player_frame, text="▶ Play Selected Song",
            command=self.play_selected_song, state="disabled", font=("Poppins", 13, "bold")
        )
        self.play_button.grid(row=2, column=0, padx=10, pady=(10,15), sticky="ew")

        # UI loop updates
        self.after(100, self.check_spotify_queue)
        self.after(100, self.check_voice_queue)

    # ---------------------------- UI LOGIC ----------------------------

    def add_message(self, sender, text):
        self.chat_display.configure(state="normal")
        if sender == "You":
            self.chat_display.insert("end", f"You: {text}\n", "user")
        else:
            self.chat_display.insert("end", f"🎧 Bot: {text}\n\n", "bot")
        self.chat_display.configure(state="disabled")
        self.chat_display.yview("end")

    def activate_voice_input(self):
        self.voice_button.configure(state="disabled")
        self.add_message("Bot", "Listening...")
        threading.Thread(target=self.voice_input_thread).start()

    def voice_input_thread(self):
        recognized_text = self.speech_converter.recognize_from_microphone()
        self.voice_queue.put(recognized_text)

    def check_voice_queue(self):
        try:
            text = self.voice_queue.get(block=False)
            self.voice_button.configure(state="normal")
            if text:
                self.message_entry.delete(0, "end")
                self.message_entry.insert(0, text)
                self.add_message("Bot", f"I heard: '{text}'. Press Send to continue.")
            else:
                self.add_message("Bot", "Sorry, I didn’t catch that. Try again.")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_voice_queue)

    def send_message(self, event=None):
        user_input = self.message_entry.get().strip()
        if not user_input:
            return

        self.add_message("You", user_input)
        self.message_entry.delete(0, "end")

        mood = self.mood_detector.predict_mood(user_input)
        self.add_message("Bot", f"You're feeling {mood}. Fetching Spotify tracks...")

        self.send_button.configure(state="disabled")
        threading.Thread(target=self.fetch_spotify_data_thread, args=(mood,)).start()

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
            self.update_playlist(result)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_spotify_queue)

    def update_playlist(self, result):
        self.send_button.configure(state="normal")
        if isinstance(result, str) and result.startswith("Error"):
            messagebox.showerror("Spotify Error", result)
            self.add_message("Bot", "⚠️ Error connecting to Spotify.")
            return

        self.tracks_data = result
        self.playlist_box.configure(state="normal")
        self.playlist_box.delete("1.0", "end")

        if not result:
            self.playlist_box.insert("end", "No songs found. Try another mood.\n")
            self.play_button.configure(state="disabled")
            return

        for i, track in enumerate(result, 1):
            self.playlist_box.insert("end", f"{i}. {track['title']} - {track['artist']}\n")

        self.playlist_box.configure(state="disabled")
        self.play_button.configure(state="normal")
        self.add_message("Bot", "Here are your songs! Choose one to play.")

    def play_selected_song(self):
        try:
            selected_line = self.playlist_box.get("insert linestart", "insert lineend").strip()
            if not selected_line:
                messagebox.showinfo("No Selection", "Click a song line first.")
                return

            index = int(selected_line.split(".")[0]) - 1
            track = self.tracks_data[index]
            preview_url = track.get("preview_url")

            if preview_url:
                pygame.mixer.music.stop()
                r = requests.get(preview_url, stream=True)
                pygame.mixer.music.load(io.BytesIO(r.content))
                pygame.mixer.music.play()
                self.add_message("Bot", f"▶️ Playing: {track['title']}")
            else:
                self.add_message("Bot", "No preview available. Opening full track...")
                webbrowser.open(track["url"])
        except Exception as e:
            messagebox.showerror("Playback Error", f"Error: {e}")

# Run App
if __name__ == "__main__":
    app = SmartMoodPlayer()
    app.mainloop()
