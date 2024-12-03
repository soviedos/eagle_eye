import os
import torch
from pathlib import Path
import yaml
import cv2
import subprocess
import warnings
import numpy as np
warnings.filterwarnings("ignore", category=FutureWarning)

# Ruta del directorio de YOLOv5
yolov5_path = Path('./yolov5')
if not yolov5_path.exists():
    # Clonar YOLOv5 si no se encuentra
    print(f"Clonando YOLOv5 en {yolov5_path}...")
    subprocess.run(['git', 'clone', 'https://github.com/ultralytics/yolov5.git', str(yolov5_path)])
class RobotDetector:
    def __init__(self):
        # Ruta del modelo entrenado
        self.model_path = Path('./yolov5/runs/train/eagle_eye_training/weights/best.pt')
        self.model = self.load_model()
        if self.model is None:
            print("Error: El modelo no está cargado.")
        print("RobotDetector initialized.")

    def load_model(self):
        if not self.model_path.exists():
            print(f"Error: No se encontró el modelo entrenado en {self.model_path}. Por favor, asegúrate de que el modelo esté entrenado y la ruta sea correcta.")
            return None
        else:
            print("Cargando modelo entrenado...")

        # Cargar el modelo entrenado
        try:
            model = torch.hub.load('./yolov5', 'custom', path=str(self.model_path), source='local')
            return model
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            return None

    def detect(self, image):
        if self.model is None:
            print("Error: El modelo no está cargado.")
            return []
        else:
            print("Realizando detección de robots...")  

        # Realizar la detección
        results = self.model(image)

        # Filtrar detecciones por umbral de confianza
        threshold = 0.7
        detections = results.xyxy[0].cpu().numpy()  # Obtener las detecciones en formato xyxy
        filtered_detections = [d for d in detections if d[4] >= threshold]  # Filtrar por umbral de confianza
        num_robots = len(filtered_detections)
        print(f"Número de robots detectados: {num_robots}")
        
        # Preparar la información para dibujar los rectángulos
        rectangles = []
        for detection in filtered_detections:
            x1, y1, x2, y2, confidence, class_id = detection
            rectangles.append((int(x1), int(y1), int(x2 - x1), int(y2 - y1), float(confidence), int(class_id)))

        return rectangles
        

    