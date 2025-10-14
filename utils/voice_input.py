# utils/voice_input.py
import speech_recognition as sr

class SpeechToTextConverter:
    """
    A class to handle speech-to-text conversion using the computer's microphone.
    """
    def __init__(self):
        """Initializes the speech recognizer."""
        self.recognizer = sr.Recognizer()

    def recognize_from_microphone(self):
        """
        Captures audio from the microphone and converts it to text.

        Returns:
            str: The recognized text as a string.
            None: If speech could not be recognized or an error occurred.
        """
        with sr.Microphone() as source:
            print("🎤 Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[SUCCESS] Ready to listen. Please speak now.")

            try:
                # Listen for the user's input with a timeout
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                print("🗣️ Recognizing...")

                # Use Google's speech recognition engine to convert audio to text
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text

            except sr.WaitTimeoutError:
                print("[WARNING] Listening timed out while waiting for phrase to start.")
                return None
            except sr.UnknownValueError:
                print("[ERROR] Google Speech Recognition could not understand the audio.")
                return None
            except sr.RequestError as e:
                print(f"[WARNING] Could not request results from Google Speech Recognition service; {e}")
                return None

# Example of how to use this file directly for testing
if __name__ == "__main__":
    converter = SpeechToTextConverter()
    recognized_text = converter.recognize_from_microphone()

    if recognized_text:
        print("\n--- Recognition Result ---")
        print(f"Text: {recognized_text}")
    else:
        print("\n--- No text was recognized ---")