# services/image_processing_service.py
import cv2
import numpy as np

class ImageProcessingService:
    def __init__(self, circle_detector, robot_detector):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Error: No se pudo abrir la cámara.")
        self.robot_detector = robot_detector
        self.circle_detector = circle_detector

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error: No se pudo capturar el cuadro de la cámara.")
            return None
        return frame

    def apply_brightness_contrast(self, image, brightness=50, contrast=50):
        # Ajustar brillo y contraste
        brightness = (brightness - 50) * 2
        contrast = (contrast - 50) * 2

        image = np.int16(image)
        image = image + brightness
        image = np.clip(image, 0, 255)

        if contrast != 0:
            factor = (131 * (contrast + 127)) / (127 * (131 - contrast))
            image = 128 + factor * (image - 128)
            image = np.clip(image, 0, 255)

        return np.uint8(image)

    def detect_circles(self, image):
        return self.circle_detector.detect(image)
    
    def detect_robots(self, image):
        # Implement robot detection logic using self.robot_detector
        print("Detecting robots...step 1")
        return self.robot_detector.detect(image)

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap.release()
