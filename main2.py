import re
from ultralytics import YOLO
import cv2
import base64
import threading
import ollama
from OpenAIUtil import get_room_information

# Initialize the OCR model
model = ocr_predictor(pretrained=True)

# Initialize the YOLO model
trained = YOLO('sign.pt')

ids = {}

def threaded_detect(cap):
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture image.")
            break

        # Run YOLO inference on the frame
        results = trained.track(frame, persist=True, verbose=False, tracker='bytetrack.yaml', show=True, conf=0.65)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()  # YOLOv8 has built-in plotting for results
        
        for result in results[0].boxes:
            # Extract bounding box, confidence, and class
            box = result.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
            if(result.id is not None):
                if(int(result.id.cpu().item()) not in ids):
                    ids[(int(result.id.cpu().item()))] = 1
                    # Break the loop if 'q' is pressed
                elif(ids[int(result.id.cpu().item())] == 1):
                    ids[(int(result.id.cpu().item()))] += 1
                    thread = threading.Thread(target=crop_and_detect_text, args=(frame, box))
                    thread.start()
                    # Break the loop if 'q' is pressed
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def crop_and_detect_text(frame, box):
    # Crop the frame around the detected object
    x1, y1, x2, y2 = map(int, box)
    cropped_object = frame[y1:y2, x1:x2]

    # Convert the cropped image to RGB
    # Encode the cropped image to JPG format
    _, encoded_image = cv2.imencode('.jpg', cropped_object)

    # Convert encoded image to bytes, then to base64
    jpg_as_bytes = encoded_image.tobytes()
    base64_encoded_image = base64.b64encode(jpg_as_bytes)

    # If you need it as a string
    base64_image_string = base64_encoded_image.decode('utf-8')
    
    get_room_information(base64_image_string, (x1+x2)/2 < cap.get(3)/2)
    
    

if __name__ == "__main__":
    # Open the webcam
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    threaded_detect(cap)

    # When everything is done, release the capture and close the window
    cap.release()
    cv2.destroyAllWindows()