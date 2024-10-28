# services/image_processing_service.py
import numpy as np
import cv2
import os
from business.circle_detector import CircleDetector
from data.image_loader import ImageLoader

class ImageProcessingService:
    def __init__(self, image_loader: ImageLoader, circle_detector: CircleDetector):
        self.image_loader = image_loader
        self.circle_detector = circle_detector

    def process_images(self, detect_black_circle=False):
        images = self.image_loader.load_images()
        for image_file in images:
            image_path = os.path.join(self.image_loader.directory, image_file)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Imagen {image_file} no se pudo cargar.")
                continue

            circles = self.circle_detector.detect_circle(image, detect_black_circle)

            if circles is not None:
                self._draw_circles(image, circles)
                output_path = os.path.join(self.image_loader.directory, f"detected_{image_file}")
                self.image_loader.save_image(image, output_path)
            else:
                print(f"Imagen {image_file}: No se encontraron círculos.")

    def _draw_circles(self, image, circles):
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)
            cv2.circle(image, (x, y), 2, (0, 0, 255), 3)
            diameter = 2 * r
            cv2.putText(image, f"Diameter: {diameter}px", (x - 50, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
