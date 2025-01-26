import re
from collections import defaultdict
from ultralytics import YOLO
import cv2
from doctr.models import ocr_predictor
from concurrent.futures import ThreadPoolExecutor
import queue
from PIL import Image
import pytesseract
import numpy as np
import imutils


class VideoStream:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
        self.model = ocr_predictor(pretrained=True)
        self.trained = YOLO("sign.pt")
        self.ids = defaultdict(int)
        self.allowed_chars = r"[^a-zA-Z0-9]"
        self.cap = (
            cv2.VideoCapture(1)
            if cv2.VideoCapture(1).isOpened()
            else cv2.VideoCapture(0)
        )
        self.text_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(
            max_workers=3
        )  # Limit concurrent OCR operations
        self.running = True

    def __del__(self):
        self.running = False
        if hasattr(self, "cap"):
            self.cap.release()
        self.executor.shutdown(wait=False)
        cv2.destroyAllWindows()

    def threaded_detect(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                break

            results = self.trained.track(
                frame,
                persist=True,
                verbose=False,
                tracker="bytetrack.yaml",
                show=True,
                conf=0.65,
            )

            for result in results[0].boxes:
                box = result.xyxy[0].cpu().numpy()
                if result.id is not None:
                    box_id = int(result.id.cpu().item())
                    self.ids[box_id] += 1
                    if self.ids[box_id] < 3:
                        self.executor.submit(
                            self.crop_and_detect_text, frame.copy(), box
                        )

    def preprocess_image(self, frame, box):
        try:
            x1, y1, x2, y2 = map(int, box)
            cropped_image = frame[y1:y2, x1:x2]

            # Convert to grayscale
            gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur to reduce noise
            blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

            # Apply thresholding
            _, thresholded_image = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Resize the image to a standard size
            resized_image = cv2.resize(thresholded_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            return resized_image
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return None

    def crop_and_detect_text(self, frame, box):
        processed_image = self.preprocess_image(frame, box)
        if processed_image is not None:
            # Use Tesseract with a specific Page Segmentation Mode (PSM) for better text detection
            custom_config = r"--oem 3 --psm 4 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            image_text = pytesseract.image_to_string(
                processed_image, config=custom_config
            )
            print(f"OCR text: {image_text}")
        else:
            print("Skipping OCR due to preprocessing error.")


if __name__ == "__main__":
    vs = VideoStream()
    vs.threaded_detect()
