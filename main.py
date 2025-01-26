from stt import STTEngine
from tts import TTSEngine

if __name__ == "__main__":
    stt_engine = STTEngine(wake_word="start", exit_word="stop")
    tts_engine = TTSEngine()
    for command in stt_engine.listen():
        tts_engine.say(command)