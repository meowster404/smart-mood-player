# app.py (Modern CustomTkinter UI)
import customtkinter as ctk
import threading, queue, webbrowser
from tkinter import messagebox
from dotenv import load_dotenv
from utils.spotify_utils import get_spotify_client, search_for_tracks
from utils.voice_input import SpeechToTextConverter

# Load environment variables
load_dotenv()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SmartSongFinder(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎧 Smart Song Finder")
        self.geometry("920x560")
        self.minsize(800, 500)

        # State variables
        self.selected_track_index = None
        self.song_widgets = []
        self.tracks_data = []
        
        # Queues
        self.spotify_queue = queue.Queue()
        self.voice_queue = queue.Queue()

        # Backend
        self.speech_converter = SpeechToTextConverter()

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
        self.chat_display.insert("end", "🎧 Bot: Hello! Search for a song.\nFor example: 'Blinding Lights' or 'Happy'\n\n")
        self.chat_display.configure(state="disabled")

        # Message entry + buttons
        self.message_entry = ctk.CTkEntry(
            self.chat_frame, placeholder_text="Search for a song...",
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

        self.song_label = ctk.CTkLabel(
            self.player_frame, text="🎵 Found Songs", font=("Poppins", 16, "bold")
        )
        self.song_label.grid(row=0, column=0, pady=(15,10))
        
        self.song_list_frame = ctk.CTkScrollableFrame(
            self.player_frame, fg_color="#121212"
        )
        self.song_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.play_button = ctk.CTkButton(
            self.player_frame, text="▶ Open Selected Song in Spotify",
            command=self.open_selected_track, state="disabled", font=("Poppins", 13, "bold")
        )
        self.play_button.grid(row=2, column=0, padx=10, pady=(10,15), sticky="ew")

        # UI loop updates
        self.after(100, self.check_spotify_queue)
        self.after(100, self.check_voice_queue)

    def update_track_display(self, result):
        # Clear previous results and reset state
        for widget in self.song_widgets:
            widget.destroy()
        self.song_widgets.clear()
        self.tracks_data = []
        self.selected_track_index = None
        self.play_button.configure(state="disabled")

        self.send_button.configure(state="normal")
        if isinstance(result, str) and result.startswith("Error"):
            messagebox.showerror("Spotify Error", result)
            self.add_message("Bot", f"⚠️ {result}")
            return

        if not result:
            self.add_message("Bot", "Couldn't find any songs. Please try something else.")
            no_results_label = ctk.CTkLabel(self.song_list_frame, text="No songs found.")
            no_results_label.pack(pady=10)
            self.song_widgets.append(no_results_label)
            return
            
        self.add_message("Bot", "Here are some songs I found. Select one and press play!")
        self.tracks_data = result
        
        # Create a clickable label for each song for better text alignment
        for i, track in enumerate(self.tracks_data):
            song_item = ctk.CTkLabel(
                self.song_list_frame,
                text=f"{track['name']}\nby {track['artist']}",
                font=("Poppins", 12),
                anchor="w",      # Aligns the text block to the left
                justify="left",  # Aligns multiple lines of text to the left
                padx=10,
                cursor="hand2"
            )
            song_item.pack(fill="x", padx=5, pady=4)
            song_item.bind("<Button-1>", lambda event, index=i: self.select_song(index))
            self.song_widgets.append(song_item)

    def select_song(self, index):
        """Highlights the selected song and enables the play button."""
        self.selected_track_index = index
        self.play_button.configure(state="normal")

        # Highlight the selected label and un-highlight others
        for i, item in enumerate(self.song_widgets):
            if i == index:
                item.configure(fg_color="#007a33", corner_radius=6) # Highlight color
            else:
                item.configure(fg_color="transparent") # Default color

    def open_selected_track(self):
        """Opens the currently selected song in Spotify."""
        if self.selected_track_index is not None:
            try:
                track = self.tracks_data[self.selected_track_index]
                webbrowser.open(track["uri"])
                self.add_message("Bot", f"Opening '{track['name']}' in Spotify...")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open the song: {e}")

    def add_message(self, sender, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{'You' if sender == 'You' else '🎧 Bot'}: {text}\n\n")
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
                self.send_message()
            else:
                self.add_message("Bot", "Sorry, I didn’t catch that. Try again.")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_voice_queue)

    def send_message(self, event=None):
        query = self.message_entry.get().strip()
        if not query:
            return

        self.add_message("You", query)
        self.message_entry.delete(0, "end")
        self.send_button.configure(state="disabled")
        self.add_message("Bot", f"Searching for '{query}' songs...")
        threading.Thread(target=self.fetch_tracks_thread, args=(query,)).start()

    def fetch_tracks_thread(self, query):
        sp = get_spotify_client()
        if not sp:
            self.spotify_queue.put("Error: Could not connect to Spotify.")
            return

        tracks = search_for_tracks(sp, query)
        self.spotify_queue.put(tracks)

    def check_spotify_queue(self):
        try:
            result = self.spotify_queue.get(block=False)
            self.update_track_display(result)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_spotify_queue)


if __name__ == "__main__":
    app = SmartSongFinder()
    app.mainloop()