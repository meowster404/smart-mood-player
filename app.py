# app.py (Modern CustomTkinter UI)
import customtkinter as ctk
import threading, queue, webbrowser
from tkinter import messagebox
from dotenv import load_dotenv
from utils.spotify_utils import get_spotify_client, search_for_playlists
from utils.voice_input import SpeechToTextConverter
from utils.nlp_mood_detector import NlpMoodDetector

# Load environment variables
load_dotenv()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SmartPlaylistFinder(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.initialization_successful = False

        try:
            self.speech_converter = SpeechToTextConverter()
            self.mood_detector = NlpMoodDetector()
            self.playlists_data = []
        except FileNotFoundError:
            self.withdraw() 
            messagebox.showerror("Model Error", "Emotion classifier model not found. Please run train_model.py.")
            self.destroy()
            return

        self.title("🎧 Smart Playlist Finder")
        self.geometry("920x560")
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

        self.chat_display = ctk.CTkTextbox(
            self.chat_frame, wrap="word", font=("Poppins", 13), fg_color="#1E1E1E",
            text_color="white", corner_radius=10, activate_scrollbars=True
        )
        self.chat_display.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=10)
        self.chat_display.insert("end", "🎧 Bot: Hello! Tell me how you are feeling...\n\n")
        self.chat_display.configure(state="disabled")

        # Message entry + buttons
        self.message_entry = ctk.CTkEntry(
            self.chat_frame, placeholder_text="How are you feeling today?",
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
        self.player_frame = ctk.CTkFrame(self, corner_radius=15)
        self.player_frame.grid(row=0, column=1, padx=(0,15), pady=15, sticky="nsew")
        self.player_frame.grid_rowconfigure(1, weight=1)
        self.player_frame.grid_columnconfigure(0, weight=1)

        self.playlist_label = ctk.CTkLabel(
            self.player_frame, text="🎵 Found Playlists", font=("Poppins", 16, "bold")
        )
        self.playlist_label.grid(row=0, column=0, pady=(15,10))

        self.playlist_scroll_frame = ctk.CTkScrollableFrame(
            self.player_frame, fg_color=self.player_frame.cget("fg_color")
        )
        self.playlist_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # UI loop updates
        self.after(100, self.check_spotify_queue)
        self.after(100, self.check_voice_queue)
        
        self.initialization_successful = True

    def add_message(self, sender, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{'You' if sender == 'You' else '🎧 Bot'}: {text}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.yview("end")

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
        
        predicted_mood = self.mood_detector.predict_mood(user_input)
        self.add_message("Bot", f"Detected mood: {predicted_mood}. Searching for playlists...")
        threading.Thread(target=self.fetch_playlists_thread, args=(predicted_mood,), daemon=True).start()

    def fetch_playlists_thread(self, query):
        sp = get_spotify_client()
        if not sp:
            self.spotify_queue.put(("Error", "Could not connect to Spotify. Please check your SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in the .env file."))
            return

        playlists = search_for_playlists(sp, query)
        self.spotify_queue.put(("Success", playlists))

    def check_spotify_queue(self):
        try:
            status, result = self.spotify_queue.get(block=False)
            
            self.send_button.configure(state="normal")
            
            if status == "Error":
                self.add_message("Bot", f"⚠️ {result}")
                messagebox.showerror("Spotify Error", result)
            else:
                self.update_playlist_display(result)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_spotify_queue)

    def update_playlist_display(self, playlists):
        for widget in self.playlist_scroll_frame.winfo_children():
            widget.destroy()

        if not playlists:
            self.add_message("Bot", "Couldn't find any playlists for that mood.")
            no_results_label = ctk.CTkLabel(self.playlist_scroll_frame, text="No playlists found.")
            no_results_label.pack(pady=10, padx=10)
        else:
            self.add_message("Bot", "Here are some playlists I found. Click one to open it!")
            for p in playlists:
                # --- FINAL UI FIX ---
                # Truncate long text to prevent ugly wrapping
                playlist_name = p['name'] # Corrected variable name
                owner_name = p['owner']
                
                if len(playlist_name) > 30:
                    playlist_name = playlist_name[:27] + "..."
                if len(owner_name) > 25:
                    owner_name = owner_name[:22] + "..."

                # Use a single line of text for clean alignment
                btn_text = f"▶ {playlist_name} (by {owner_name})"
                
                playlist_button = ctk.CTkButton(
                    self.playlist_scroll_frame,
                    text=btn_text,
                    font=("Poppins", 13),
                    anchor="w",  # Align text to the left
                    command=lambda url=p['url'], name=p['name']: self.open_in_spotify(url, name)
                )
                playlist_button.pack(fill="x", padx=5, pady=(0, 5))
                # --- END FINAL UI FIX ---

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