from stt import STTEngine
from tts import TTSEngine
from vision import VideoStream
from decision import DecisionManager
import threading

if __name__ == "__main__":
    
    stt_engine = STTEngine(wake_word="start", exit_word="stop")
    tts_engine = TTSEngine()
    video_stream = VideoStream()
    decision_manager = DecisionManager(stt_engine, tts_engine, video_stream)

    decision_thread = threading.Thread(target=decision_manager.run)
    decision_thread.start()

    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting program...")
        decision_manager.navigation_cancelled.set()
        decision_thread.join()

    
