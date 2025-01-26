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
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
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

            # cv2.imwrite("cropped.jpg", cropped_image)
            scaled_image = enlarge(cropped_image)
            # cv2.imwrite("scaled.jpg", scaled_image)
            normalized_image = normalize(scaled_image)
            # cv2.imwrite("normal.jpg", normalized_image)
            grayscale_image = grayscale(normalized_image)
            # cv2.imwrite("grayscale.jpg", grayscale_image)
            thresholded_image = image_smoothen(grayscale_image)

            # inverted_image = cv2.bitwise_not(eroded_image)
            # cv2.imwrite("inverted.jpg", inverted_image)

            return thresholded_image

        except Exception as e:
            print(f"Error processing frame: {e}")
            return None

    def crop_and_detect_text(self, frame, box):
        processed_image = self.preprocess_image(frame, box)
        if processed_image is not None:
            custom_config = r"--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789"
            image_text = pytesseract.image_to_string(
                processed_image, lang="eng", config=custom_config
            )
            print(f"OCR text: {image_text}")
        else:
            print("Skipping OCR due to preprocessing error.")


def normalize(image):
    norm_img = np.zeros((image.shape[0], image.shape[1]))
    normalized_image = cv2.normalize(image, norm_img, 0, 255, cv2.NORM_MINMAX)
    return normalized_image


def deskew(image):
    # Check if image is empty or has no non-zero pixels
    if np.count_nonzero(image) == 0:
        print("Image is empty or has no non-zero pixels.")
        return image

    co_ords = np.column_stack(np.where(image > 0))

    # If there are no coordinates, return the original image
    if len(co_ords) == 0:
        print("No non-zero pixels found.")
        return image

    # Find the minimum area rectangle
    angle = cv2.minAreaRect(co_ords)[-1]

    # Correct the angle to deskew
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated_image


def enlarge(image):
    height, width = image.shape[:2]
    resized_image = cv2.resize(
        image, (width * 3, height * 3), interpolation=cv2.INTER_LINEAR
    )
    return resized_image


def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def image_smoothen(img):
    # Step 1: Apply binary thresholding to the input image
    ret1, th1 = cv2.threshold(img, 88, 255, cv2.THRESH_BINARY)

    # Step 2: Apply Otsu's thresholding to further enhance the binary image
    ret2, th2 = cv2.threshold(th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Step 3: Perform Gaussian blurring to reduce noise
    blur = cv2.GaussianBlur(th2, (5, 5), 0)

    # Step 4: Apply another Otsu's thresholding to obtain the final smoothed image
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    denoised = cv2.fastNlMeansDenoising(th3, None, 10, 7, 21)

    return denoised


if __name__ == "__main__":
    vs = VideoStream()
    vs.threaded_detect()
