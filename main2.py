import re
from ultralytics import YOLO
import cv2
from doctr.models import ocr_predictor
import threading
import ollama

# Initialize the OCR model
model = ocr_predictor(pretrained=True)

# Initialize the YOLO model
trained = YOLO('sign.pt')

ids = {}

def interpret_sign(text, position):
    content = """
        Given this OCR text output ({text}) containing a concatenated room name and number with potential typos, process the text to extract and correct the room name and number. Ensure the following steps are taken:
        Extract Information: Use regular expressions to separate the room name and number from a concatenated string (e.g., "lacture2024" should be parsed into "lacture" and "2024").
        Identify and Correct Typos: Check the extracted room name for common OCR errors and correct them based on a predefined list of known room names (e.g., "lacture" should be corrected to "lecture"). Use a dictionary approach where each misspelled word has a corresponding correct spelling.
        Format Output: Combine the corrected room name and number into a standard format (e.g., "Lecture Hall 2024"). If the room name does not match any entry in the known list, return an empty string.
        Return Result: Output the formatted string if corrections are successful and valid; otherwise, return an empty string if the room name cannot be validated.

            Example Input: "men2024"
            Expected Output: "Men's Room 2024"

            Example Input: "lacture2034"
            Expected Output: "Lecture Hall 2034"

            Example Input: "confrence3001"
            Expected Output: "Conference Room 3001"
        """.format(text=text)
        
    response = ollama.chat(
        model='llama3.2',
        messages=[{
            'role': 'user',
            'content': content
        }]
    )
    print(content)
    print(response)

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
    cropped_object_rgb = cv2.cvtColor(cropped_object, cv2.COLOR_BGR2RGB)

    # Use doctr to predict text
    response = model([cropped_object_rgb])
    
    text = ""

    for page in response.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    if(word.confidence > 0.5):
                        text += word.value
                text += "\n"
                
    print(re.sub(r'[^a-zA-Z0-9]', '', text))

    if(text != ""):
        interpret_sign_thread = threading.Thread(target=interpret_sign, args=(re.sub(r'[^a-zA-Z0-9]', '', text,), (x1+x2)/2 < cap.get(3)/2))
        interpret_sign_thread.start()
    

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