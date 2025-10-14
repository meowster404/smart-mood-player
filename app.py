# app.py (Modern CustomTkinter UI with Enhanced Features)
import customtkinter as ctk
import threading, queue, webbrowser
import os, json, random
from tkinter import messagebox
from dotenv import load_dotenv
import time, re
from datetime import datetime

# Import modules
from utils.enhanced_spotify_utils import get_spotify_client, search_for_playlists, search_for_track, search_for_artist_top_tracks
from utils.voice_input import SpeechToTextConverter
from utils.nlp_mood_detector import NlpMoodDetector
from utils.enhanced_intent_detector import EnhancedIntentDetector
from utils.enhanced_chatbot import EnhancedChatbot
from utils.performance_analyzer import PerformanceAnalyzer

# Load environment variables
load_dotenv()

# Configure appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Initialize performance analyzer
performance_analyzer = PerformanceAnalyzer()

class SmartPlaylistFinder(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Enable high DPI scaling
        self.tk.call('tk', 'scaling', 2.0)
        
        self.initialization_successful = False

        try:
            # Initialize components
            self.speech_converter = SpeechToTextConverter()
            self.mood_detector = NlpMoodDetector()
            self.intent_detector = EnhancedIntentDetector()
            self.chatbot = EnhancedChatbot()
            self.playlists_data = []
            
            # Session tracking
            self.session_start = datetime.now()
            self.interaction_count = 0
            
            # Performance tracking
            self.last_request_time = None
            
        except FileNotFoundError as e:
            self.withdraw()
            if "emotion_classifier.pkl" in str(e):
                messagebox.showerror("Model Error", "Emotion classifier model not found. Please run train_model.py.")
            elif "chatbot_model.pkl" in str(e):
                messagebox.showerror("Model Error", "Chatbot model not found. Please run train_model.py.")
            else:
                messagebox.showerror("File Error", f"A required file was not found: {e}")
            self.destroy()
            return

        # Window Configuration
        self.title("🎧 Smart Music Player")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Configure modern color scheme
        self.bg_color = "#0F172A"  # Dark blue background
        self.accent_color = "#3B82F6"  # Bright blue accent
        self.secondary_color = "#1E293B"  # Lighter blue secondary
        self.text_color = "#E2E8F0"  # Light gray text
        self.configure(fg_color=self.bg_color)

        # Queues
        self.spotify_queue = queue.Queue()
        self.voice_queue = queue.Queue()

        # Main Layout with improved spacing
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Status Bar
        self.status_frame = ctk.CTkFrame(self, height=30, fg_color=self.secondary_color)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Ready",
            font=("Poppins", 12),
            text_color="#A0AEC0"
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5)

        # Left: Enhanced Chat Panel
        self.chat_frame = ctk.CTkFrame(
            self, 
            corner_radius=15,
            fg_color=self.secondary_color,
            border_width=1,
            border_color=self.accent_color
        )
        self.chat_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.chat_frame.grid_rowconfigure(1, weight=1)  # Make chat area expand
        self.chat_frame.grid_columnconfigure(0, weight=1)
        
        # Configure main window grid
        self.grid_rowconfigure(0, weight=1)  # Make main content expand
        
        # Chat header with reduced height
        self.chat_header = ctk.CTkFrame(
            self.chat_frame,
            fg_color=self.accent_color,
            height=35,  # Reduced height
            corner_radius=10
        )
        self.chat_header.grid(row=0, column=0, columnspan=3, padx=5, pady=(2,0), sticky="ew")  # Reduced top padding
        self.chat_header.grid_propagate(False)

        self.chat_title = ctk.CTkLabel(
            self.chat_header,
            text="💬 Chat with Smart Music Player",
            font=("Poppins", 12, "bold"),  # Slightly smaller font
            text_color="white"
        )
        self.chat_title.place(relx=0.5, rely=0.5, anchor="center")        # Enhanced chat area with custom styling
        self.chat_scroll_frame = ctk.CTkScrollableFrame(
            self.chat_frame, 
            fg_color=self.secondary_color,
            corner_radius=10,
            height=500  # Set a fixed height
        )
        self.chat_scroll_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)  # Reduced padding
        self.chat_frame.grid_rowconfigure(1, weight=1)  # Make chat area expand

        # Welcome message using enhanced chatbot
        welcome_response = self.chatbot.get_response("hello")
        self.add_message("Bot", welcome_response)

        # Enhanced message entry with modern styling
        self.message_frame = ctk.CTkFrame(
            self.chat_frame,
            fg_color=self.secondary_color,
            corner_radius=10
        )
        self.message_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=(0,5), sticky="ew")
        self.message_frame.grid_columnconfigure(0, weight=1)

        self.message_entry = ctk.CTkEntry(
            self.message_frame, 
            placeholder_text="Type a message or ask for music...",
            font=("Poppins", 12),
            corner_radius=15,
            height=32,  # Reduced height
            border_width=1,
            border_color=self.accent_color
        )
        self.message_entry.grid(row=0, column=0, padx=(10,5), pady=5, sticky="ew")
        self.message_entry.bind("<Return>", self.send_message)

        # Enhanced voice button with animation support
        self.voice_button = ctk.CTkButton(
            self.message_frame,
            text="🎙",
            width=40,
            height=40,
            command=self.activate_voice_input,
            font=("Poppins", 14, "bold"),
            fg_color=self.accent_color,
            corner_radius=20
        )
        self.voice_button.grid(row=0, column=1, padx=5, pady=5)

        # Enhanced send button
        self.send_button = ctk.CTkButton(
            self.message_frame,
            text="➤",
            width=40,
            height=40,
            command=self.send_message,
            font=("Poppins", 14, "bold"),
            fg_color=self.accent_color,
            corner_radius=20
        )
        self.send_button.grid(row=0, column=2, padx=(5,10), pady=5)
        
        # Loading indicator (hidden by default)
        self.loading_label = ctk.CTkLabel(
            self.message_frame,
            text="🔄",
            font=("Poppins", 14),
            text_color=self.accent_color
        )
        self.loading_label.grid(row=0, column=3, padx=5, pady=5)
        self.loading_label.grid_remove()

        # Enhanced Recommendations Panel
        self.results_frame = ctk.CTkFrame(
            self, 
            corner_radius=15,
            fg_color=self.secondary_color,
            border_width=1,
            border_color=self.accent_color
        )
        self.results_frame.grid(row=0, column=1, padx=(0,15), pady=15, sticky="nsew")
        self.results_frame.grid_rowconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        # Results header with modern styling
        self.results_header = ctk.CTkFrame(
            self.results_frame,
            fg_color=self.accent_color,
            height=40,
            corner_radius=10
        )
        self.results_header.grid(row=0, column=0, padx=5, pady=(5,0), sticky="ew")
        self.results_header.grid_propagate(False)

        self.results_label = ctk.CTkLabel(
            self.results_header,
            text="🎵 Found Music",
            font=("Poppins", 14, "bold"),
            text_color="white"
        )
        self.results_label.place(relx=0.5, rely=0.5, anchor="center")

        # Enhanced scrollable results area
        self.results_scroll_frame = ctk.CTkScrollableFrame(
            self.results_frame,
            fg_color=self.secondary_color,
            corner_radius=10
        )
        self.results_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # UI loop updates
        self.after(100, self.check_spotify_queue)
        self.after(100, self.check_voice_queue)

        self.initialization_successful = True

    def add_message(self, sender, text):
        """Add a message to the chat with enhanced styling and animations."""
        if sender == "You":  # User message (right side)
            # Container frame for better alignment
            container = ctk.CTkFrame(
                self.chat_scroll_frame,
                fg_color="transparent"
            )
            container.pack(fill="x", pady=2)
            
            # Time label above message
            time_label = ctk.CTkLabel(
                container,
                text=datetime.now().strftime("%H:%M"),
                font=("Poppins", 10, "bold"),
                text_color="#94A3B8"
            )
            time_label.pack(anchor="e", padx=20, pady=(2,0))
            
            # Message bubble
            bubble = ctk.CTkFrame(
                container,
                fg_color=self.accent_color,
                corner_radius=12,
                border_width=1,
                border_color="#60A5FA"
            )
            bubble.pack(anchor="e", padx=15, pady=(0,2), ipadx=12, ipady=8)
            
            # Message text
            label = ctk.CTkLabel(
                bubble,
                text=text,
                font=("Poppins", 13),
                text_color="white",
                wraplength=400,
                justify="left"  # Always left-align text
            )
            label.pack(padx=10, pady=2)  # Increased padding
            
        else:  # Bot
            # Container frame for better alignment
            container = ctk.CTkFrame(
                self.chat_scroll_frame,
                fg_color="transparent"
            )
            container.pack(fill="x", pady=2)
            
            # Time label above message (left side)
            time_label = ctk.CTkLabel(
                container,
                text=datetime.now().strftime("%H:%M"),
                font=("Poppins", 10, "bold"),
                text_color="#94A3B8"
            )
            time_label.pack(anchor="w", padx=20, pady=(2,0))
            
            # Message bubble
            bubble = ctk.CTkFrame(
                container,
                fg_color="#1E293B",
                corner_radius=12,
                border_width=1,
                border_color="#3B82F6"
            )
            bubble.pack(anchor="w", padx=15, pady=(0,2), ipadx=12, ipady=6)
            
            # Bot header with icon
            header_frame = ctk.CTkFrame(
                bubble,
                fg_color="transparent"
            )
            header_frame.pack(fill="x", padx=8, pady=(4,2))
            
            icon_label = ctk.CTkLabel(
                header_frame,
                text="🤖",
                font=("Poppins", 13)
            )
            icon_label.pack(side="left", padx=(0,4))
            
            name_label = ctk.CTkLabel(
                header_frame,
                text="Smart Music Bot",
                font=("Poppins", 11, "bold"),
                text_color="#E2E8F0"
            )
            name_label.pack(side="left")
            
            # Message text
            label = ctk.CTkLabel(
                bubble,
                text=text,
                font=("Poppins", 13),
                text_color="white",
                wraplength=400,
                justify="left"
            )
            label.pack(padx=5)
            
            # Time stamp with better visibility and padding
            time_label = ctk.CTkLabel(
                bubble,
                text=datetime.now().strftime("%H:%M"),
                font=("Poppins", 10, "bold"),  # Made bold
                text_color="#94A3B8"  # Brighter color
            )
            time_label.pack(anchor="w", padx=15, pady=(5,8))  # Increased padding

        # Auto-scroll to latest message
        self.after(10, lambda: self.chat_scroll_frame._parent_canvas.yview_moveto(1.0))
        
        # Update status
        self.status_label.configure(text="Ready")
        if hasattr(self, 'loading_label'):
            self.loading_label.grid_remove()
        
        # Track interaction
        self.interaction_count += 1

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
        """Process and respond to user messages with enhanced handling."""
        user_input = self.message_entry.get().strip()
        if not user_input:
            return

        # Record start time for performance tracking
        start_time = time.time()
        self.last_request_time = start_time

        # Update UI state
        self.add_message("You", user_input)
        self.message_entry.delete(0, "end")
        self.send_button.configure(state="disabled")
        self.loading_label.grid()
        self.status_label.configure(text="Processing message...")

        # Clear previous results before starting new search
        self._clear_results_area()

        # First detect mood using our trained ML model
        detected_mood = self.mood_detector.predict_mood(user_input)
        print(f"Detected mood: {detected_mood}")

        # Get intent using enhanced intent detector
        intent_data = self.intent_detector.detect_intent(user_input)
        intent = intent_data.get("intent")
        entity = intent_data.get("entity")

        # Enhanced logic: Use ML mood detection results
        # If mood detection gives a clear result, prioritize it over pattern matching
        if detected_mood and detected_mood.lower() not in ["neutral", "unknown", "error"]:
            print(f"[ML] Using mood detection: {detected_mood}")
            # Override intent to MoodSearch if we have a clear mood
            intent = "MoodSearch"
            entity = detected_mood.lower()
        elif intent == "MoodSearch" and entity:
            # Use pattern-matched mood if ML didn't detect anything clear
            print(f"[PATTERN] Using pattern-matched mood: {entity}")
            detected_mood = entity
        else:
            # For non-mood intents, use pattern matching as before
            print(f"[PATTERN] Using intent detection: {intent} -> {entity}")

        # Log mood detection performance (ML model accuracy)
        # In a real system, you'd compare detected_mood with ground truth
        mood_accuracy = 1.0 if detected_mood and detected_mood.lower() not in ["neutral", "unknown", "error"] else 0.5
        performance_analyzer.log_mood_detection(
            predicted_mood=detected_mood,
            actual_mood=detected_mood  # Would compare with user feedback in real system
        )

        # Log intent detection performance (now includes ML mood detection)
        performance_analyzer.log_intent_detection(
            predicted_intent=intent,
            actual_intent=intent  # In a real system, you'd compare with ground truth
        )

        # Enhanced Intent Handling with ML integration
        print(f"[DEBUG] Input: '{user_input}'")
        print(f"[DEBUG] ML Mood: '{detected_mood}', Intent: '{intent}', Entity: '{entity}'")
        
        # Check for greetings and general conversation first
        if intent in ["GREETING", "Greeting"]:
            response = self.chatbot.get_response(user_input)
            self.add_message("Bot", response)
            self.send_button.configure(state="normal")
            return

        # Check for help requests
        if intent == "Help":
            help_message = "I can help you find music using AI-powered mood detection! Try saying things like:\n• 'I'm feeling happy' (AI analyzes your mood and finds matching music)\n• 'Play Faded by Alan Walker' (for specific songs)\n• 'Find songs by Taylor Swift' (for artist tracks)\n• 'I want music for studying' (for activity playlists)\n• Just express how you're feeling naturally!"
            self.add_message("Bot", help_message)
            self.send_button.configure(state="normal")
            return

        # Handle specific intents
        if intent == "SongSearch":
            print(f"Song search detected for: {entity}")
            self.status_label.configure(text="🎵 Searching for your song...")
            self.add_message("Bot", "🎵 Let me find that track for you!")
            threading.Thread(
                target=self.fetch_track_thread,
                args=(user_input,),
                daemon=True
            ).start()
            return

        elif intent == "ArtistSearch":
            print(f"Artist search detected for: {entity}")
            self.status_label.configure(text=f"Searching for music by {entity}...")
            self.add_message("Bot", f"🔍 Let me find some great tracks by {entity}...")
            threading.Thread(
                target=self.fetch_artist_tracks_thread,
                args=(entity,),
                daemon=True
            ).start()
            return

        elif intent == "ActivitySearch":
            print(f"Activity search detected: {entity}")
            activity_responses = {
                "studying": ("Finding study music...", "Perfect! I'll find some great music to help you focus and study. Let me search for some concentration-friendly playlists!", "calm"),
                "workout": ("Finding workout music...", "Time to get pumped! I'll find some energetic music to power your workout!", "happy"),
                "relaxation": ("Finding relaxing music...", "I'll help you unwind with some peaceful, relaxing music!", "calm"),
                "party": ("Finding party music...", "Let's get this party started! I'll find some amazing dance music for you!", "happy"),
                "work": ("Finding work music...", "Let me find some productive background music for your work session!", "calm"),
                "gaming": ("Finding gaming music...", "Let's find some epic music for your gaming session!", "happy")
            }
            
            if entity in activity_responses:
                status, message, mood = activity_responses[entity]
                self.status_label.configure(text=status)
                self.add_message("Bot", message)
                threading.Thread(
                    target=self.fetch_playlists_thread,
                    args=(mood,),
                    daemon=True
                ).start()
                return

        elif intent == "DirectMusicSearch":
            print(f"Direct music search detected: {entity}")
            self.status_label.configure(text=f"Finding {entity} music...")
            self.add_message("Bot", f"I'll find some great {entity} music for you!")
            threading.Thread(
                target=self.fetch_playlists_thread,
                args=(entity,),
                daemon=True
            ).start()
            return

        elif intent == "MoodSearch":
            print(f"Mood search detected with ML mood: {detected_mood}")

            # Test Spotify connection first
            print("[DEBUG] Testing Spotify connection...")
            from utils.enhanced_spotify_utils import get_spotify_client
            test_sp = get_spotify_client()
            if not test_sp:
                error_msg = "❌ Spotify connection failed. Please check your .env file with SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET"
                self.add_message("Bot", error_msg)
                self.send_button.configure(state="normal")
                return
            else:
                print("[DEBUG] Spotify connection successful")

            # Use the ML-detected mood for playlist search
            mood_to_use = detected_mood.lower() if detected_mood else entity

            # Provide ML-based empathetic responses for detected emotions
            mood_responses = {
                "sad": [
                    "I can tell you're feeling down. Let me find some comforting music that might help lift your spirits.",
                    "Music can be really healing when we're feeling low. Let me find some soothing tracks for you.",
                    "I understand you're going through a difficult time. Let me find some gentle, comforting music for you."
                ],
                "happy": [
                    "I can sense your positive energy! Let me find some uplifting music to match your great mood!",
                    "That's wonderful to hear! I'll find some fantastic music to keep those good vibes going!",
                    "Your happiness is contagious! Let me find some joyful music to celebrate with you!"
                ],
                "angry": [
                    "I can feel your frustration. Sometimes intense music can help process strong emotions. Let me find something that resonates with how you're feeling.",
                    "It sounds like you're dealing with some intense emotions. Let me find some powerful music that might help you work through this.",
                    "I can sense you're upset. Music can be a great outlet for strong feelings. Let me find something that matches your energy."
                ],
                "calm": [
                    "I can tell you're in a peaceful state of mind. Let me find some serene music that matches your calm energy.",
                    "Your tranquility is beautiful. Let me find some peaceful music to complement your relaxed mood.",
                    "I can sense your inner peace. Let me find some gentle, soothing music for you."
                ],
                "excited": [
                    "I can feel your excitement! Let me find some energetic music to match your enthusiastic mood!",
                    "Your energy is amazing! I'll find some upbeat, exciting music to fuel your enthusiasm!",
                    "I love your positive energy! Let me find some thrilling music to keep you pumped up!"
                ],
                "tired": [
                    "I can tell you're feeling weary. Let me find some gentle, relaxing music to help you unwind.",
                    "You seem like you need some rest. Let me find some soothing, calming music for you.",
                    "I can sense your fatigue. Let me find some peaceful music to help you relax and recharge."
                ]
            }

            # Get appropriate response based on ML-detected mood
            responses = mood_responses.get(mood_to_use, ["Let me find some music that matches how you're feeling."])
            response_message = responses[0]  # Use first response for now

            self.status_label.configure(text=f"Finding {mood_to_use} music based on your mood...")
            self.add_message("Bot", response_message)
            threading.Thread(
                target=self.fetch_playlists_thread,
                args=(mood_to_use,),
                daemon=True
            ).start()
            return

        # For unrecognized intents, provide a helpful response
        if intent == "Chat":
            fallback_response = "I'm not sure I understand, but I can use AI to analyze your mood! Try expressing how you're feeling, or ask me to:\n• Find songs by an artist\n• Play a specific song\n• Get music for activities like studying or working out\n• Just tell me how you're feeling and I'll find matching music!"
            self.add_message("Bot", fallback_response)
            self.send_button.configure(state="normal")
            return

        # Default fallback
        self.add_message("Bot", "I couldn't understand your request. Try asking for music, songs, or playlists!")
        self.send_button.configure(state="normal")

        # Log response time
        end_time = time.time()
        response_time = end_time - start_time
        performance_analyzer.log_response_time(response_time)

    def fetch_track_thread(self, track_name):
        try:
            # First update UI
            self.spotify_queue.put(("Status", "[INFO] Connecting to Spotify..."))

            # Get Spotify client
            sp = get_spotify_client()
            if not sp:
                print("[ERROR] Could not connect to Spotify")
                self.spotify_queue.put(("Error", "[ERROR] Could not connect to Spotify. Please check your internet connection and .env file."))
                return

            self.spotify_queue.put(("Status", "[INFO] Searching for tracks..."))

            # Perform search
            tracks = search_for_track(sp, track_name, limit=5)

            if not tracks:
                print("No tracks found")
                self.spotify_queue.put(("TRACKS", []))
                self.add_message("Bot", "I couldn't find any tracks matching your request. Try being more specific or check the spelling.")
            else:
                print(f"\nFound {len(tracks)} tracks:")
                for i, track in enumerate(tracks, 1):
                    print(f"{i}. {track.get('name')} - {track.get('artist')}")
                self.spotify_queue.put(("TRACKS", tracks))

        except Exception as e:
            print(f"Error while searching: {str(e)}")
            import traceback
            print(traceback.format_exc())
            # Safe error message without Unicode characters
            error_msg = "[ERROR] An error occurred while searching. Please try a different search term."
            self.spotify_queue.put(("Error", error_msg))

    def _parse_song_request(self, query):
        """Enhanced song request parsing."""
        patterns = [
            r"(?i)play\s+(.+?)\s+(?:by|from)\s+(.+)",  # "play X by Y"
            r"(?i)i\s+want\s+(.+?)\s+(?:by|from)\s+(.+)",  # "I want X by Y"
            r"(?i)find\s+(.+?)\s+(?:by|from)\s+(.+)",  # "find X by Y"
            r"(?i)search\s+for\s+(.+?)\s+(?:by|from)\s+(.+)",  # "search for X by Y"
            r"(?i)(.+?)\s+(?:by|from)\s+(.+)"  # "X by Y"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, query)
            if match:
                return {
                    'title': match.group(1).strip(),
                    'artist': match.group(2).strip()
                }
        
        return {
            'title': query,
            'artist': None
        }

    def fetch_artist_tracks_thread(self, artist_name):
        sp = get_spotify_client()
        if not sp:
            self.spotify_queue.put(("Error", "Could not connect to Spotify. Check your .env file."))
            return
        tracks = search_for_artist_top_tracks(sp, artist_name)
        self.spotify_queue.put(("TRACKS", tracks))

    def fetch_playlists_thread(self, mood):
        try:
            print(f"[DEBUG] Starting ML-based playlist search for mood: {mood}")

            # Load emotion responses to get playlist suggestions
            emotion_responses_path = os.path.join(os.path.dirname(__file__), "data", "emotion_responses.json")
            print(f"[DEBUG] Loading emotion responses from: {emotion_responses_path}")

            with open(emotion_responses_path, 'r') as f:
                mood_data = json.load(f)["moods"]
            print(f"[DEBUG] Loaded mood data successfully")

            # Enhanced emotion mapping for ML model outputs
            emotion_map = {
                "sad": "sadness",
                "sadness": "sadness",
                "depressed": "sadness",
                "unhappy": "sadness",
                "happy": "joy",
                "joy": "joy",
                "excited": "joy",
                "energetic": "joy",
                "angry": "anger",
                "anger": "anger",
                "frustrated": "anger",
                "calm": "neutral",
                "neutral": "neutral",
                "peaceful": "neutral",
                "relaxed": "neutral",
                "tired": "sadness",  # Map tired to sadness for mellow music
                "fear": "sadness",   # Map fear to sadness for calming music
                "surprise": "joy",   # Map surprise to joy for upbeat music
                "disgust": "anger"   # Map disgust to anger for intense music
            }

            # Map the input mood to emotion category
            emotion = emotion_map.get(mood.lower(), "neutral")
            print(f"[DEBUG] Mapped ML mood '{mood}' to emotion '{emotion}'")

            # Get playlist keywords for the emotion
            if emotion in mood_data and "playlists" in mood_data[emotion]:
                query = " ".join(mood_data[emotion]["playlists"])
                print(f"[DEBUG] Using ML-enhanced playlist keywords: {mood_data[emotion]['playlists']}")
            else:
                # Fallback: Use the original mood as search query
                query = mood
                print(f"[DEBUG] Using fallback query: {query}")

            print(f"[DEBUG] Final ML-enhanced search query: '{query}'")

            # Get Spotify client
            print(f"[DEBUG] Getting Spotify client...")
            sp = get_spotify_client()
            if not sp:
                error_msg = "Could not connect to Spotify. Please check your SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in the .env file."
                print(f"[ERROR] {error_msg}")
                self.spotify_queue.put(("Error", error_msg))
                return

            print(f"[DEBUG] Spotify client obtained successfully")

            # Search for playlists using ML-enhanced query
            print(f"[DEBUG] Searching for playlists with ML-enhanced query...")
            playlists = search_for_playlists(sp, query)
            print(f"[DEBUG] Search completed. Found {len(playlists) if playlists else 0} playlists")

            if playlists:
                print(f"[DEBUG] Sending {len(playlists)} ML-curated playlists to UI")
                self.spotify_queue.put(("PLAYLISTS", playlists))
            else:
                print(f"[DEBUG] No playlists found, trying fallback searches...")

                # Try multiple fallback strategies for better ML integration
                fallback_queries = [
                    f"{mood} music",
                    f"{emotion} music",
                    "mood music",
                    "music"  # Very generic fallback
                ]

                for fallback_query in fallback_queries:
                    if fallback_query != query:  # Don't repeat the same query
                        print(f"[DEBUG] Trying fallback query: '{fallback_query}'")
                        fallback_playlists = search_for_playlists(sp, fallback_query)
                        if fallback_playlists:
                            print(f"[DEBUG] Found {len(fallback_playlists)} playlists with fallback query")
                            self.spotify_queue.put(("PLAYLISTS", fallback_playlists))
                            break
                else:
                    print(f"[DEBUG] No playlists found even with fallback queries")
                    self.spotify_queue.put(("Error", f"I couldn't find any playlists for '{mood}' mood. Try expressing your feelings differently!"))

        except Exception as e:
            error_msg = f"Error in ML-enhanced playlist search: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            print(traceback.format_exc())
            self.spotify_queue.put(("Error", "An error occurred while searching for mood-based playlists."))

    def check_spotify_queue(self):
        try:
            status, result = self.spotify_queue.get(block=False)
            self.send_button.configure(state="normal")
            
            # Debug print (safely handle Unicode)
            try:
                print(f"Received from Spotify queue - Status: {status}, Result type: {type(result)}")
                if isinstance(result, (list, dict)):
                    print(f"Results count: {len(result) if isinstance(result, list) else 'N/A'}")
            except UnicodeEncodeError:
                print(f"Received from Spotify queue - Status: {status}, Results: [Unicode data]")

            if status == "Error":
                self.add_message("Bot", f"[WARNING] {result}")
                messagebox.showerror("Spotify Error", result)
            elif status in ["TRACKS", "PLAYLISTS"]:
                self.update_results_display(status, result)
            else:
                print(f"Unknown status: {status}")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_spotify_queue)

    def update_results_display(self, result_type, results):
        """Update results display with enhanced styling and metrics tracking."""
        try:
            print(f"\n[UI] Updating results display")
            print(f"[UI] Type: {result_type}")
            print(f"[UI] Results count: {len(results) if results else 0}")
            print(f"[UI] Results data: {results[:2] if results else 'None'}")  # Show first 2 results

            # Clear existing results
            for widget in self.results_scroll_frame.winfo_children():
                widget.destroy()

            # Handle no results case
            if not results:
                print("[UI] No results to display")
                self._show_no_results()
                return

            # Update UI based on result type
            if result_type == "TRACKS":
                self.results_label.configure(text="♪ Found Tracks")
                self.add_message("Bot", "Here are the tracks I found. Click any to open in Spotify!")
                
                print(f"[UI] Creating cards for {len(results)} tracks")
                for idx, track in enumerate(results):
                    try:
                        print(f"[UI] Creating card for track: {track['name']}")
                        card = self._create_result_card(
                            title=track['name'],
                            subtitle=f"by {track['artist']}" + (f" (feat. {', '.join(track['all_artists'][1:])})" if len(track.get('all_artists', [])) > 1 else ""),
                            icon="♪",
                            url=track.get('url', '#'),
                            name=track['name']
                        )
                        card.pack(fill="x", padx=5, pady=2)
                        print(f"[UI] Successfully created card {idx + 1}")
                    except Exception as e:
                        print(f"[Error] Failed to create card for track {idx}: {e}")
                
            elif result_type == "PLAYLISTS":
                self.results_label.configure(text="♫ Found Playlists")
                self.add_message("Bot", "I found these playlists that might interest you. Click any to open in Spotify!")
                
                print(f"[UI] Creating cards for {len(results)} playlists")
                for idx, playlist in enumerate(results):
                    try:
                        print(f"[UI] Creating card for playlist: {playlist['name']}")
                        card = self._create_result_card(
                            title=playlist['name'],
                            subtitle=f"Created by {playlist['owner']}",
                            icon="♫",
                            url=playlist.get('url', '#'),
                            name=playlist['name'],
                            metrics=f"Tracks: {playlist.get('tracks_total', '?')} • Followers: {playlist.get('followers', '?')}"
                        )
                        if card:  # Make sure card was created successfully
                            card.pack(fill="x", padx=5, pady=2)
                            print(f"[UI] Successfully created and packed card {idx + 1}")
                        else:
                            print(f"[ERROR] Card creation returned None for playlist {idx}")
                    except Exception as e:
                        print(f"[Error] Failed to create card for playlist {idx}: {e}")
                        import traceback
                        print(traceback.format_exc())

            # Update metrics
            satisfaction_score = min(len(results) / 10.0, 1.0)
            performance_analyzer.log_chat_satisfaction(satisfaction_score)
            
            # Update status
            self.status_label.configure(text=f"Found {len(results)} results")
            self.loading_label.grid_remove()

        except Exception as e:
            print(f"[Error] Failed to update results display: {str(e)}")
            import traceback
            print(traceback.format_exc())
            self._show_no_results(error=True)

    def _show_no_results(self, error=False):
        """Display a no results or error message."""
        no_results_frame = ctk.CTkFrame(
            self.results_scroll_frame,
            fg_color=self.secondary_color,
            corner_radius=15,
            border_width=1,
            border_color=self.accent_color
        )
        no_results_frame.pack(fill="x", padx=10, pady=10)
        
        icon = "⚠️" if error else "🔍"
        text = "An error occurred while searching" if error else "No results found"
        hint = "Please try again later" if error else "Try being more specific or check the spelling"
        
        # Icon
        icon_label = ctk.CTkLabel(
            no_results_frame,
            text=icon,
            font=("Poppins", 24),
            text_color="#A0AEC0"
        )
        icon_label.pack(pady=(15,5))
        
        # Main message
        message_label = ctk.CTkLabel(
            no_results_frame,
            text=text,
            font=("Poppins", 14, "bold"),
            text_color="#A0AEC0"
        )
        message_label.pack(pady=5)
        
        # Hint
        hint_label = ctk.CTkLabel(
            no_results_frame,
            text=hint,
            font=("Poppins", 12),
            text_color="#64748B"
        )
        hint_label.pack(pady=(0,15))
        
        # Update status
        self.status_label.configure(text="No results found")
        self.loading_label.grid_remove()

    def _clear_results_area(self):
        """Clear the results display area before starting a new search."""
        try:
            # Clear existing results
            for widget in self.results_scroll_frame.winfo_children():
                widget.destroy()

            # Reset results label to default state
            self.results_label.configure(text="♪ Found Music")

        except Exception as e:
            print(f"Error clearing results area: {e}")

    def _create_result_card(self, title, subtitle, icon, url, name, metrics=None):
        """Create a styled result card for tracks and playlists."""
        try:
            # Create main card frame
            card = ctk.CTkFrame(
                self.results_scroll_frame,
                fg_color="#1E293B",
                corner_radius=10,
                cursor="hand2"  # Show hand cursor on hover
            )

            # Use grid geometry manager consistently
            card.grid_columnconfigure(0, weight=1)

            # Make the entire card clickable by binding to the card itself
            card.bind("<Button-1>", lambda e: self.open_in_spotify(url, name))

            # Add hover effect for better UX
            def on_enter(e):
                card.configure(fg_color="#2D3748")  # Slightly lighter on hover

            def on_leave(e):
                card.configure(fg_color="#1E293B")  # Back to original color

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

            # Create content container
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
            content.grid_columnconfigure(1, weight=1)

            # Icon - using simple text symbols instead of Unicode
            icon_text = "♪" if icon == "♪" else "♫"
            icon_label = ctk.CTkLabel(
                content,
                text=icon_text,
                font=("Arial", 20, "bold"),  # Use Arial font for better compatibility
                text_color="#3B82F6"  # Blue color for icons
            )
            icon_label.grid(row=0, column=0, rowspan=3, padx=(5,10))

            # Title
            title_label = ctk.CTkLabel(
                content,
                text=title,
                font=("Poppins", 14, "bold"),
                text_color="white",
                anchor="w",
                justify="left"
            )
            title_label.grid(row=0, column=1, sticky="w")

            # Subtitle
            subtitle_label = ctk.CTkLabel(
                content,
                text=subtitle,
                font=("Poppins", 12),
                text_color="#94A3B8",
                anchor="w",
                justify="left"
            )
            subtitle_label.grid(row=1, column=1, sticky="w", pady=(2,0))

            # Optional metrics
            if metrics:
                metrics_label = ctk.CTkLabel(
                    content,
                    text=metrics,
                    font=("Poppins", 11),
                    text_color="#64748B",
                    anchor="w",
                    justify="left"
                )
                metrics_label.grid(row=2, column=1, sticky="w", pady=(2,0))

            return card

        except Exception as e:
            print(f"Error creating result card: {str(e)}")
            # Return error card
            error_card = ctk.CTkFrame(
                self.results_scroll_frame,
                fg_color="#1E293B",
                corner_radius=10,
                height=80
            )
            error_label = ctk.CTkLabel(
                error_card,
                text="[WARNING] Failed to display result",
                font=("Poppins", 12),
                text_color="#EF4444"
            )
            error_label.pack(expand=True)
            return error_card

    def open_in_spotify(self, url, name):
        try:
            webbrowser.open(url)
            self.add_message("Bot", f"Opening '{name}' in Spotify...")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open the link: {e}")

if __name__ == "__main__":
    app = SmartPlaylistFinder() 
    if app.initialization_successful:
        app.mainloop()