# app.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import queue
import io
import pygame
import webbrowser
import requests # Make sure 'requests' is imported
from dotenv import load_dotenv

# Local imports are no longer needed here as the backend handles them
# from utils.nlp_mood_detector import NlpMoodDetector
# from utils.spotify_utils import get_spotify_client, get_spotify_recommendations

load_dotenv()

class ChatPlayerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Mood Player (Frontend)")
        self.root.geometry("800x500")
        self.root.minsize(600, 400)

        pygame.mixer.init()

        # --- GUI Setup (No changes here) ---
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
        self.chat_window = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state='disabled', font=("Helvetica", 11))
        self.chat_window.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.message_entry = tk.Entry(self.chat_frame, font=("Helvetica", 11))
        self.message_entry.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.message_entry.bind("<Return>", self.send_message)
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, sticky="ew", pady=(10, 0), padx=(5, 0))
        self.playlist_label = tk.Label(self.player_frame, text="🎵 Recommendations", font=("Helvetica", 12, "bold"))
        self.playlist_label.grid(row=0, column=0, sticky="w", pady=5)
        self.playlist_listbox = tk.Listbox(self.player_frame, height=15, selectbackground="#c3c3c3")
        self.playlist_listbox.grid(row=1, column=0, sticky="nsew")
        self.play_button = tk.Button(self.player_frame, text="▶️ Play Selected Song", command=self.play_selected_song, state=tk.DISABLED)
        self.play_button.grid(row=2, column=0, sticky="ew", pady=10)
        
        self.backend_queue = queue.Queue()
        self.tracks_data = []

        self.add_message("Bot", "Hello! Tell me how you're feeling or what you're in the mood for.")
        self.check_backend_queue()

    def add_message(self, sender, message):
        self.chat_window.config(state='normal')
        if sender == "You":
            self.chat_window.insert(tk.END, f"You: {message}\n", 'user_tag')
        else:
            self.chat_window.insert(tk.END, f"Bot: {message}\n\n", 'bot_tag')
        self.chat_window.config(state='disabled')
        self.chat_window.yview(tk.END)

    def send_message(self, event=None):
        user_input = self.message_entry.get()
        if not user_input:
            return
        
        self.add_message("You", user_input)
        self.message_entry.delete(0, tk.END)
        self.add_message("Bot", "Thinking... Contacting the mood analysis service...")
        
        self.send_button.config(state=tk.DISABLED)
        # Call the new function to fetch data from the backend
        threading.Thread(target=self.fetch_from_backend_thread, args=(user_input,)).start()

    def fetch_from_backend_thread(self, text):
        """Sends a request to the backend server and puts the response in a queue."""
        backend_url = "http://127.0.0.1:5000/recommendations"
        try:
            response = requests.post(backend_url, json={"text": text}, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            self.backend_queue.put(response.json())
        except requests.exceptions.RequestException as e:
            error_message = f"Error: Could not connect to the backend at {backend_url}. Please ensure it is running."
            print(f"{error_message}\nDetails: {e}")
            self.backend_queue.put({"error": error_message})

    def check_backend_queue(self):
        """Checks the queue for results from the backend thread."""
        try:
            result = self.backend_queue.get(block=False)
            self.update_ui_with_results(result)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_backend_queue)

    def update_ui_with_results(self, result):
        self.send_button.config(state=tk.NORMAL)

        # Handle any errors returned from the backend
        if "error" in result:
            messagebox.showerror("Backend Error", result["error"])
            self.add_message("Bot", "Sorry, I ran into an error getting recommendations.")
            return

        # Extract data from the backend's JSON response
        predicted_mood = result.get('mood', 'unknown')
        self.tracks_data = result.get('tracks', [])
        
        self.add_message("Bot", f"I sense you're feeling '{predicted_mood}'. Here are some songs I found for you!")
        
        self.playlist_listbox.delete(0, tk.END)
        if not self.tracks_data:
            self.add_message("Bot", "I couldn't find any tracks for that mood. Try something else!")
            self.play_button.config(state=tk.DISABLED)
            return

        for track in self.tracks_data:
            self.playlist_listbox.insert(tk.END, f"{track['title']} - {track['artist']}")
        
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