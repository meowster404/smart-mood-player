# app.py (Modern CustomTkinter UI for Chatbot)

import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv

# Import the new Chatbot class
from utils.chatbot import Chatbot

# Load environment variables (optional, can be removed if not needed)
load_dotenv()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ChatbotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.initialization_successful = False

        try:
            # Initialize the new Chatbot
            self.chatbot = Chatbot()
        except FileNotFoundError:
            self.withdraw() 
            messagebox.showerror("Model Error", "Chatbot model not found. Please run train_chatbot.py.")
            self.destroy()
            return

        self.title("🤖 Conversational Chatbot")
        self.geometry("700x520") # Adjusted size for a single panel
        self.minsize(500, 400)

        # --- Main Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Chat Panel (the only panel now) ---
        self.chat_frame = ctk.CTkFrame(self, corner_radius=15)
        self.chat_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(
            self.chat_frame, wrap="word", font=("Poppins", 13), fg_color="#1E1E1E",
            text_color="white", corner_radius=10, activate_scrollbars=True
        )
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.chat_display.insert("end", "🤖 Bot: Hello! How are you doing today?\n\n")
        self.chat_display.configure(state="disabled")

        # --- Message entry + button ---
        self.message_entry = ctk.CTkEntry(
            self.chat_frame, placeholder_text="Type your message here...",
            font=("Poppins", 12), corner_radius=10
        )
        self.message_entry.grid(row=1, column=0, padx=(10, 5), pady=(0, 10), sticky="ew")
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = ctk.CTkButton(
            self.chat_frame, text="Send ➤", command=self.send_message,
            font=("Poppins", 13, "bold")
        )
        self.send_button.grid(row=1, column=1, padx=(5, 10), pady=(0, 10))
        
        self.initialization_successful = True

    def add_message(self, sender, text):
        """Adds a message to the chat display."""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{'You' if sender == 'You' else '🤖 Bot'}: {text}\n\n")
        self.chat_display.configure(state="disabled")
        # Auto-scroll to the bottom
        self.chat_display.yview("end")

    def send_message(self, event=None):
        """Handles sending a message from the user and getting a response."""
        user_input = self.message_entry.get().strip()
        if not user_input:
            return

        self.add_message("You", user_input)
        self.message_entry.delete(0, "end")
        
        # Disable the send button while the bot "thinks"
        self.send_button.configure(state="disabled")

        # Get the bot's response from our new chatbot model
        bot_response = self.chatbot.get_response(user_input)
        
        # Add a small delay to simulate thinking
        self.after(500, self.add_bot_response, bot_response)

    def add_bot_response(self, response):
        """Adds the bot's response to the chat and re-enables the button."""
        self.add_message("Bot", response)
        self.send_button.configure(state="normal")


if __name__ == "__main__":
    app = ChatbotApp()
    if app.initialization_successful:
        app.mainloop()