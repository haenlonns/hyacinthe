import threading

class Location:
    def __init__(self, value, position):
        self.value = value
        self.position = position

class DecisionManager:
    def __init__(self, STT, TTS, video_stream):
        self.locations = []
        self.vision = video_stream
        self.STT = STT
        self.TTS = TTS

    def add_location(self, value, position):
        self.locations.insert(0, Location(value, position))
        if(len(self.locations) > 2):
            self.locations.pop()

    def get_surrounding_locations(self):
        return f"You have {self.locations[0].value} on your {self.locations[0].position} and {self.locations[1].value} on your {self.locations[1].position}." 

    def run(self):
        vision_thread = threading.Thread(target=self.vision.threaded_detect)
        vision_thread.start()

        for command in self.stt_engine.listen():
            if("where am i" in command.lower()):
                self.TTS.say(self.get_surrounding_locations())