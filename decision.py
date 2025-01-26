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

    def get_surrounding_locations(self):
        if(len(self.locations) == 0):
            return "I don't see any locations."
        elif(len(self.locations) == 1):
            return f"You have {self.locations[0].value} on your {self.locations[0].position}."
        return f"You have {self.locations[0].value} on your {self.locations[0].position} and {self.locations[1].value} on your {self.locations[1].position}." 

    def run_vision(self):
        for result in self.vision.threaded_detect():
            self.add_location(result)
    
    def run_stt(self):
        for command in self.STT.listen():
            if("where am i" in command.lower()):
                self.TTS.say(self.get_surrounding_locations())

    def run(self):
        # Create and start threads for vision detection and voice command listening
        vision_thread = threading.Thread(target=self.run_vision())
        voice_thread = threading.Thread(target=self.run_stt())

        vision_thread.start()
        voice_thread.start()

        # Wait for both threads to complete
        vision_thread.join()
        voice_thread.join()