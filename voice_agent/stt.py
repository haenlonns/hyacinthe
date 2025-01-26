import speech_recognition as sr

class STTEngine:
    def __init__(self, wake_word="hey assistant"):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.wake_word = wake_word.lower()  # Set the wake word

    def listen(self) -> str:
        print("Listening for the wake word...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for ambient noise
            while True:
                try:
                    audio = self.recognizer.listen(source)
                    print("Recognizing potential wake word...")
                    text = self.recognizer.recognize_google(audio).lower()

                    if self.wake_word in text:
                        print(f"Wake word '{self.wake_word}' detected!")
                        break
                    else:
                        print("Wake word not detected. Continuing to listen...")

                except sr.UnknownValueError:
                    print("[ERROR] Audio not understood.")
                except sr.RequestError as e:
                    print(f"[ERROR] Could not request results; {e}")

        return self.activate_command_mode()

    def activate_command_mode(self) -> str:
        """This method is triggered when the wake word is detected."""
        print("Command mode activated. Listening for your command...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)
        
        try:
            print("Recognizing command...")
            return self.recognizer.recognize_google(audio)

        except sr.UnknownValueError:
            print("[ERROR] Command not understood.")
            return ""

    
if __name__ == "__main__":
    text_engine = STTEngine(wake_word="hey assistant")
    while True:
        command = text_engine.listen()
        print(f"Command: {command}")
