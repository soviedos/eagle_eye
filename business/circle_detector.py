import cv2
import numpy as np

class CircleDetector:
    def __init__(self, min_radius=0, max_radius=100, param1=50, param2=30):
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.param1 = param1
        self.param2 = param2

    def detect_circle(self, image, detect_black_circle=False):
        # Convertir la imagen a escala de grises y aplicar desenfoque
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)

        if detect_black_circle:
            # Invertir los colores para resaltar el círculo negro
            _, inverted = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
        else:
            inverted = blurred

        # Detección de círculos
        circles = cv2.HoughCircles(
            inverted, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
            param1=self.param1, param2=self.param2,
            minRadius=self.min_radius, maxRadius=self.max_radius
        )

        return circles

