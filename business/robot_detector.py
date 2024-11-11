import cv2
import numpy as np
from ui.image_adjustment import ImageAdjustmentUI

class RobotDetector:
    def __init__(self, dojo_diameter_cm=80):
        self.dojo_diameter_cm = dojo_diameter_cm
        self.px_to_cm_ratio_value = None

    def px_to_cm_ratio(self):
        # Calcular la relación de conversión píxeles a centímetros
        dojo_radius_cm = self.dojo_diameter_cm / 2
        self.px_to_cm_ratio_value = dojo_radius_cm / ImageAdjustmentUI.radius_value(self)
        print(ImageAdjustmentUI.radius_value(self))
        return self.px_to_cm_ratio_value

    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        radio_value = self.px_to_cm_ratio()

        print(radio_value)

        rectangles = []
        for contour in contours:
            # Aproximar el contorno a un polígono
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:
                # Obtener el rectángulo delimitador del polígono
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                if 0.8 <= aspect_ratio <= 1.2:  # Verificar si el contorno es aproximadamente un cuadrado
                    # Convertir las dimensiones del rectángulo de píxeles a centímetros
                    width_cm = w * radio_value
                    height_cm = h * radio_value
                    # Verificar si las dimensiones están dentro del rango deseado
                    if 6 <= width_cm <= 15 and 6 <= height_cm <= 15:
                        rectangles.append((x, y, w, h))
                        # Dibujar el rectángulo detectado en la imagen para depuración
                        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return rectangles