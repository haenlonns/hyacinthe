import re
from collections import defaultdict
from ultralytics import YOLO
import cv2
from doctr.models import ocr_predictor
import threading


class VideoStream:
    def __init__(self):
        self.model = ocr_predictor(pretrained=True)
        self.trained = YOLO('sign.pt')
        self.ids = defaultdict(int)
        self.cap = cv2.VideoCapture(1) if cv2.VideoCapture(1).isOpened() else cv2.VideoCapture(0)

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def threaded_detect(self):
        while True:
            # Capture frame-by-frame
            ret, frame = self.cap.read()

            if not ret:
                print("Error: Failed to capture image.")
                break

            # Run YOLO inference on the frame
            results = self.trained.track(frame, persist=True, verbose=False, tracker='bytetrack.yaml', show=True, conf=0.65)
            
            for result in results[0].boxes:
                # Extract bounding box, confidence, and class
                box = result.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                if(result.id is not None):
                    self.ids[(int(result.id.cpu().item()))] += 1
                    if(self.ids[int(result.id.cpu().item())] < 3):
                        thread = threading.Thread(target=self.crop_and_detect_text, args=(frame, box))
                        thread.start()
                        # Break the loop if 'q' is pressed
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def crop_and_detect_text(self, frame, box):
        # Crop the frame around the detected object
        x1, y1, x2, y2 = map(int, box)
        cropped_object = frame[y1:y2, x1:x2]

        # Convert the cropped image to RGB
        cropped_object_rgb = cv2.cvtColor(cropped_object, cv2.COLOR_BGR2RGB)

        # Use doctr to predict text
        response = self.model([cropped_object_rgb])
        
        text = ""

        for page in response.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        if(word.confidence > 0.5):
                            text += word.value
                    text += "\n"

        
        print(re.sub(r'[^a-zA-Z0-9]', '', text))


if __name__ == "__main__":
    vs = VideoStream()
    vs.threaded_detect()
