import speech_recognition as sr

class STTEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    
    def listen(self) -> str:
        with self.microphone as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening for speech...")
            audio = self.recognizer.listen(source)
        
        try:
            print("Recognizing speech...")
            return self.recognizer.recognize_faster_whisper(audio)

        except sr.UnknownValueError:
            print("[ERROR] Audio not understood.")
            return ""

if __name__ == "__main__":
    text_engine = STTEngine()
    text = text_engine.listen()
    print(text)
