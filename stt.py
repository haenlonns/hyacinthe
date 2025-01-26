import speech_recognition as sr

class STTEngine:
    def __init__(self, wake_word="hey assistant", exit_word="goodbye"):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.wake_word = wake_word.lower()  # Set the wake word
        self.exit_word = exit_word.lower()  # Set the exit word
        self.is_listening = False  # Flag to control listening mode

        # Adjust for ambient noise once during initialization
        with self.microphone as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready to listen!")

    def listen(self):
        """Continuously listen and yield the recognized commands."""
        print("Listening for the wake word...")
        with self.microphone as source:
            while True:
                try:
                    # Listen continuously
                    audio = self.recognizer.listen(source, phrase_time_limit=10)
                    text: str = self.recognizer.recognize_google(audio)

                    # Recognize speech
                    if self.is_listening:
                        print("Recognizing command...")
                        
                        if self.exit_word in text.lower():
                            print(f"Exit word '{self.exit_word}' detected! Stopping command mode...")
                            self.is_listening = False
                            print("Waiting for the wake word again...")
                        else:
                            print(f"Command recognized: {text}")
                            yield text

                    else:
                        print("Recognizing potential wake word...")

                        if self.wake_word in text.lower():
                            print(f"Wake word '{self.wake_word}' detected! Entering command mode...")
                            self.is_listening = True

                except sr.WaitTimeoutError:
                    print("[ERROR] Listening timed out.")
                except sr.UnknownValueError:
                    print("[ERROR] Audio not understood.")
                except sr.RequestError as e:
                    print(f"[ERROR] Could not request results; {e}")

if __name__ == "__main__":
    text_engine = STTEngine(wake_word="start", exit_word="stop")

    # Loop over the output of listen() to continuously get commands
    for command in text_engine.listen():
        print(f"Sending command to TTS: {command}")
