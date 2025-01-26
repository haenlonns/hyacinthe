import sys
from os import system

class TTSEngine:
    def __init__(self):
        self.platform = sys.platform
        if self.platform != 'darwin':
            import pyttsx3
            self.engine = pyttsx3.init()
            self.voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', self.voices[1].id)
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 2)
        else:
            self.allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
    
    def say(self, text: str):
        if self.platform == "darwin":
            clean_text = ''.join(c for c in text if c in self.allowed_chars)
            system(f"say '{clean_text}'")
        else:
            self.engine.say(text)
            self.engine.runAndWait()


if __name__ == "__main__":
    voice_engine = TTSEngine()
    voice_engine.say("Hello, world!")
    voice_engine.say("This is a test.")
    voice_engine.say("Andre is a good boy.")
