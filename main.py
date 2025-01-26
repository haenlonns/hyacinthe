from stt import STTEngine
from tts import TTSEngine
from vision import VideoStream
from decision import InformationManager
import threading

if __name__ == "__main__":
    
    stt_engine = STTEngine(wake_word="start", exit_word="stop")
    tts_engine = TTSEngine()
    video_stream = VideoStream()
    decision_manager = InformationManager(stt_engine, tts_engine, video_stream)

    
