import cv2
import numpy as np

class CircleDetector:
    def __init__(self):
        self.param1 = 50
        self.param2 = 30
        self.min_radius = 120
        self.max_radius = 135

    def detect(self, image):
        # Convertir la imagen a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Aplicar un desenfoque gaussiano para suavizar la imagen y reducir el ruido
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)

        # Detectar círculos usando HoughCircles
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=50,
            param1=self.param1,
            param2=self.param2,
            minRadius=self.min_radius,
            maxRadius=self.max_radius
        )

        # Asegurarse de que se detectaron círculos
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            # Filtrar círculos que son oscuros (negros) en la imagen original
            black_circles = []
            for (x, y, r) in circles:
                # Extraer la región del círculo
                mask = np.zeros_like(gray)
                cv2.circle(mask, (x, y), r, 255, -1)  # Máscara circular
                mean_intensity = cv2.mean(gray, mask=mask)[0]  # Intensidad media dentro del círculo

                # Considerar solo los círculos negros (intensidad baja)
                if mean_intensity < 70:  # Ajusta el umbral si es necesario para mejorar la precisión
                    black_circles.append((x, y, r))

            return black_circles

        return None

