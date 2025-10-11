# app.py (Modern CustomTkinter UI with Intent-based Chatbot)
import customtkinter as ctk
import threading, queue, webbrowser
from tkinter import messagebox
from dotenv import load_dotenv
from utils.spotify_utils import get_spotify_client, search_for_playlists, search_for_track, search_for_artist_top_tracks
from utils.voice_input import SpeechToTextConverter
from utils.nlp_mood_detector import NlpMoodDetector
from utils.intent_detector import IntentDetector

# Load environment variables
load_dotenv()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SmartPlaylistFinder(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.initialization_successful = False

        try:
            self.speech_converter = SpeechToTextConverter()
            self.mood_detector = NlpMoodDetector()
            self.intent_detector = IntentDetector()
            self.playlists_data = []
        except FileNotFoundError as e:
            self.withdraw()
            if "emotion_classifier.pkl" in str(e):
                messagebox.showerror("Model Error", "Emotion classifier model not found. Please run train_model.py.")
            else:
                messagebox.showerror("File Error", f"A required file was not found: {e}")
            self.destroy()
            return

        self.title("🎧 Smart Music Finder")
        self.geometry("1000x600")
        self.minsize(800, 500)

        # Queues
        self.spotify_queue = queue.Queue()
        self.voice_queue = queue.Queue()

        # Main Layout
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left: Chat Panel
        self.chat_frame = ctk.CTkFrame(self, corner_radius=15)
        self.chat_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_scroll_frame = ctk.CTkScrollableFrame(self.chat_frame, fg_color=self.chat_frame.cget("fg_color"))
        self.chat_scroll_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=10)


        self.add_message("Bot", "Hi, how can I help you? You can ask for songs by artist, title, activity, or tell me how you're feeling!")

        # Message entry + buttons
        self.message_entry = ctk.CTkEntry(
            self.chat_frame, placeholder_text="e.g., 'play happy songs' or 'songs by Queen'",
            font=("Poppins", 12), corner_radius=10
        )
        self.message_entry.grid(row=1, column=0, padx=(10,5), pady=(0,10), sticky="ew")
        self.message_entry.bind("<Return>", self.send_message)

        self.voice_button = ctk.CTkButton(
            self.chat_frame, text="🎙", width=45, command=self.activate_voice_input,
            font=("Poppins", 13, "bold")
        )
        self.voice_button.grid(row=1, column=1, padx=5, pady=(0,10))

        self.send_button = ctk.CTkButton(
            self.chat_frame, text="Send ➤", command=self.send_message,
            font=("Poppins", 13, "bold")
        )
        self.send_button.grid(row=1, column=2, padx=(5,10), pady=(0,10))

        # Right: Recommendations Panel
        self.results_frame = ctk.CTkFrame(self, corner_radius=15)
        self.results_frame.grid(row=0, column=1, padx=(0,15), pady=15, sticky="nsew")
        self.results_frame.grid_rowconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        self.results_label = ctk.CTkLabel(
            self.results_frame, text="🎵 Found Music", font=("Poppins", 16, "bold")
        )
        self.results_label.grid(row=0, column=0, pady=(15,10))

        self.results_scroll_frame = ctk.CTkScrollableFrame(
            self.results_frame, fg_color=self.results_frame.cget("fg_color")
        )
        self.results_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # UI loop updates
        self.after(100, self.check_spotify_queue)
        self.after(100, self.check_voice_queue)

        self.initialization_successful = True

    def add_message(self, sender, text):
        if sender == "You":
            bubble = ctk.CTkFrame(self.chat_scroll_frame, fg_color="#3B82F6", corner_radius=15)
            bubble.pack(anchor="e", padx=10, pady=5, ipadx=10, ipady=5)
            label = ctk.CTkLabel(bubble, text=text, font=("Poppins", 13), text_color="white", wraplength=400, justify="right")
            label.pack()
        else: # Bot
            bubble = ctk.CTkFrame(self.chat_scroll_frame, fg_color="#4B5563", corner_radius=15)
            bubble.pack(anchor="w", padx=10, pady=5, ipadx=10, ipady=5)
            label = ctk.CTkLabel(bubble, text=text, font=("Poppins", 13), text_color="white", wraplength=400, justify="left")
            label.pack()

        self.chat_scroll_frame._parent_canvas.yview_moveto(1.0)


    def activate_voice_input(self):
        self.voice_button.configure(state="disabled")
        self.add_message("Bot", "Listening...")
        threading.Thread(target=self.voice_input_thread, daemon=True).start()

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
                self.send_message()
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
        self.send_button.configure(state="disabled")

        # 1. Detect Intent
        intent_data = self.intent_detector.detect_intent(user_input)
        intent = intent_data.get("intent")
        entity = intent_data.get("entity")

        # 2. Handle Intent
        if intent == "GREETING":
            self.add_message("Bot", "Hello! How can I help you find some music today?")
            self.send_button.configure(state="normal")
        elif intent == "QUESTION":
            self.add_message("Bot", "I'm a bot designed to help you find music based on your mood, artists, songs, or activities!")
            self.send_button.configure(state="normal")
        elif intent == "ARTIST":
            self.add_message("Bot", f"Searching for top tracks by {entity}...")
            threading.Thread(target=self.fetch_artist_tracks_thread, args=(entity,), daemon=True).start()
        elif intent == "SONG":
            self.add_message("Bot", f"Searching for the song '{entity}'...")
            threading.Thread(target=self.fetch_track_thread, args=(entity,), daemon=True).start()
        elif intent == "ACTIVITY":
            mood = intent_data["mood"]
            self.add_message("Bot", f"For {entity}, I recommend some {mood} music. Would you like me to find some?")
            # For simplicity, we search directly. A more advanced bot could wait for a "yes" response.
            threading.Thread(target=self.fetch_playlists_thread, args=(mood,), daemon=True).start()
        elif intent == "MOOD":
            predicted_mood = self.mood_detector.predict_mood(user_input)
            self.add_message("Bot", f"It sounds like you're feeling {predicted_mood}. Let me find some playlists for that...")
            threading.Thread(target=self.fetch_playlists_thread, args=(predicted_mood,), daemon=True).start()
        else:
            self.add_message("Bot", "I'm not sure I understood. You can ask me to play a song, find an artist, or tell me your mood.")
            self.send_button.configure(state="normal")


    def fetch_track_thread(self, track_name):
        sp = get_spotify_client()
        if not sp:
            self.spotify_queue.put(("Error", "Could not connect to Spotify. Check your .env file."))
            return
        tracks = search_for_track(sp, track_name)
        self.spotify_queue.put(("TRACKS", tracks))

    def fetch_artist_tracks_thread(self, artist_name):
        sp = get_spotify_client()
        if not sp:
            self.spotify_queue.put(("Error", "Could not connect to Spotify. Check your .env file."))
            return
        tracks = search_for_artist_top_tracks(sp, artist_name)
        self.spotify_queue.put(("TRACKS", tracks))

    def fetch_playlists_thread(self, query):
        sp = get_spotify_client()
        if not sp:
            self.spotify_queue.put(("Error", "Could not connect to Spotify. Please check your SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in the .env file."))
            return
        playlists = search_for_playlists(sp, query)
        self.spotify_queue.put(("PLAYLISTS", playlists))

    def check_spotify_queue(self):
        try:
            status, result = self.spotify_queue.get(block=False)
            self.send_button.configure(state="normal")

            if status == "Error":
                self.add_message("Bot", f"⚠️ {result}")
                messagebox.showerror("Spotify Error", result)
            else:
                self.update_results_display(status, result)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_spotify_queue)

    def update_results_display(self, result_type, results):
        for widget in self.results_scroll_frame.winfo_children():
            widget.destroy()

        if not results:
            self.add_message("Bot", "Sorry, I couldn't find anything for that.")
            no_results_label = ctk.CTkLabel(self.results_scroll_frame, text="No results found.")
            no_results_label.pack(pady=10, padx=10)
            return

        if result_type == "PLAYLISTS":
            self.results_label.configure(text="🎵 Found Playlists")
            self.add_message("Bot", "Here are some playlists I found. Click one to open it!")
            for p in results:
                playlist_name = p['name']
                owner_name = p['owner']
                if len(playlist_name) > 30: playlist_name = playlist_name[:27] + "..."
                if len(owner_name) > 25: owner_name = owner_name[:22] + "..."
                btn_text = f"▶ {playlist_name} (by {owner_name})"
                btn = ctk.CTkButton(
                    self.results_scroll_frame, text=btn_text, font=("Poppins", 13), anchor="w",
                    command=lambda url=p['url'], name=p['name']: self.open_in_spotify(url, name)
                )
                btn.pack(fill="x", padx=5, pady=(0, 5))

        elif result_type == "TRACKS":
            self.results_label.configure(text="🎵 Found Tracks")
            self.add_message("Bot", "Here are some tracks I found. Click one to open it!")
            for t in results:
                track_name = t['name']
                artist_name = t['artist']
                if len(track_name) > 30: track_name = track_name[:27] + "..."
                if len(artist_name) > 25: artist_name = artist_name[:22] + "..."
                btn_text = f"🎵 {track_name} (by {artist_name})"
                btn = ctk.CTkButton(
                    self.results_scroll_frame, text=btn_text, font=("Poppins", 13), anchor="w",
                    command=lambda url=t['url'], name=t['name']: self.open_in_spotify(url, name)
                )
                btn.pack(fill="x", padx=5, pady=(0, 5))


    def open_in_spotify(self, url, name):
        try:
            webbrowser.open(url)
            self.add_message("Bot", f"Opening '{name}' in Spotify...")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open the playlist: {e}")

if __name__ == "__main__":
    app = SmartPlaylistFinder()
    if app.initialization_successful:
        app.mainloop()