import threading
from vision import VideoStream
from OpenAIUtil import get_room_number, find_closest_command

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
        self.navigation_thread = None
        self.navigation_cancelled = threading.Event()
        self.commands = ["SURROUNDINGS", "NAVIGATE", "CANCEL", "TRYAGAIN"]

    def add_location(self, value, position):
        self.locations.insert(0, Location(value, position))
        if len(self.locations) > 2:
            self.locations.pop()

    def get_surrounding_locations(self):
        if len(self.locations) == 0:
            return "I don't see any locations. Please walk around more!"
        elif len(self.locations) == 1:
            return f"You have {self.locations[0].value} on your {self.locations[0].position}."
        return f"You have {self.locations[0].value} on your {self.locations[0].position} and {self.locations[1].value} on your {self.locations[1].position}."

    def alert_on_detection(self, box):
        # This function will be called whenever an object is detected
        print(f"Alert: Object detected at {box}")

    def run_vision(self):
        for result in self.vision.threaded_detect():
            self.add_location(result)

    def navigate(self, destination):
        self.TTS.say(f"Navigating to room {destination}.")
        while not self.navigation_cancelled.is_set():
            # Simulate navigation process
            if len(self.locations) < 1:
                self.TTS.say("I'm sorry, I do not know where you are. Please walk around a bit more so I can find where you are. Then try navigating again.")
                return
            else:
                if self.locations[0].value == destination:
                    self.TTS.say(f"Arrived at room {destination}.")
                    return
                elif abs(self.locations[0].value - destination) < abs(self.locations[1].value - destination):
                    self.TTS.say("You are going the wrong way. Turn around.")
                else:
                    self.TTS.say("You are going the right way. Keep going.")
            self.navigation_cancelled.wait(1)  # Check for cancellation every second
        self.TTS.say("Navigation cancelled.")

    def run_stt(self):
        self.TTS.say("Ready to listen.")
        for command in self.STT.listen():
            closest_command, destination = find_closest_command(command, self.commands)
            if closest_command == "NAVIGATE":
                print(destination)
                if(destination == None or destination == -1):
                    self.TTS.say("Please include the room number you wish to navigate to. Examples include: Navigate to room 2000.")
                else:
                    if self.navigation_thread and self.navigation_thread.is_alive():
                        self.TTS.say("Already navigating.")
                    else:
                        self.navigation_cancelled.clear()
                        self.navigation_thread = threading.Thread(target=self.navigate, args=(destination, ))
                        self.navigation_thread.start()
            elif closest_command == "SURROUNDINGS":
                self.TTS.say(self.get_surrounding_locations())
            elif closest_command == "CANCEL":
                self.navigation_cancelled.set()
                self.TTS.say("Navigation cancelled.")
            elif closest_command == "TRYAGAIN":
                self.TTS.say("I'm sorry, I didn't understand that. Please try again.")

    def run(self):
        # Create and start threads for vision detection and voice command listening
        vision_thread = threading.Thread(target=self.run_vision)
        voice_thread = threading.Thread(target=self.run_stt)

        vision_thread.start()
        voice_thread.start()

        # Wait for both threads to complete
        vision_thread.join()
        voice_thread.join()