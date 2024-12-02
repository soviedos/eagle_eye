import tkinter as tk
import numpy as np
from tkinter import Button, Frame, Label
from services.image_processing_service import ImageProcessingService
from PIL import Image, ImageTk
#from business.robot_detector import RobotDetector
import cv2
from PIL import Image, ImageDraw, ImageTk

class FuturisticScale(tk.Canvas):
    def __init__(self, parent, label, min_value, max_value, initial_value, row, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.command = command

        self.width = 330
        self.height = 33

        # Crear la etiqueta del nombre de la barra
        self.label_widget = tk.Label(parent, text=label, fg="white", bg="black")
        self.label_widget.grid(row=row, column=1, pady=5, sticky="n")

        # Etiquetas de Min y Max
        self.min_label = tk.Label(parent, text="Min", fg="white", bg="black")
        self.min_label.grid(row=row + 1, column=0, sticky="e", padx=5)

        self.max_label = tk.Label(parent, text="Max", fg="white", bg="black")
        self.max_label.grid(row=row + 1, column=2, sticky="w", padx=5)

        # Configurar el canvas de la barra futurista
        self.config(width=self.width, height=self.height, bg="black", highlightthickness=0)
        self.grid(row=row + 1, column=1, pady=5, padx=10)

        # Mostrar el valor actual debajo de la barra
        self.value_label = tk.Label(parent, text=f"Valor: {self.value}", fg="white", bg="black")
        self.value_label.grid(row=row + 2, column=1, pady=2, sticky="n")

        # Dibujar la barra inicial
        self.draw_scale()

        # Eventos de clic y movimiento del mouse
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)

    def draw_scale(self):
        self.delete("all")

        # Calcular el llenado de la barra basado en el valor actual
        fill_width = int((self.value / (self.max_value - self.min_value)) * self.width)

        # Dibujar la barra llena con un gradiente
        color_start = "#003B63"
        color_end = "#00A8E8"
        self.create_rectangle(0, 0, fill_width, self.height, fill=color_end, outline="")

        # Actualizar el valor mostrado
        self.value_label.config(text=f"Valor: {self.value}")

    def on_click(self, event):
        self.update_value(event.x)

    def on_drag(self, event):
        self.update_value(event.x)

    def update_value(self, x):
        # Calcular el valor basado en la posición del mouse
        new_value = int((x / self.width) * (self.max_value - self.min_value))
        self.value = max(self.min_value, min(self.max_value, new_value))
        self.draw_scale()

        # Llamar a la función de callback si se proporciona
        if self.command:
            self.command(self.value)

class ImageAdjustmentUI:
    def __init__(self, processing_service: ImageProcessingService):
        self.processing_service = processing_service
        #self.robot_detector = RobotDetector()
        self.roi_rect = (0, 0, 100, 100)  # Example values, adjust as needed
        self.root = tk.Tk()
        self.root.title("Eagle Eye Software")
        self.root.configure(bg="black")

        # Frame para la cámara
        self.camera_frame = Frame(self.root, bg="black")
        self.camera_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Frame para los controles
        self.control_frame = Frame(self.root, bg="black")
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        # Crear un widget de etiqueta para mostrar el video en el frame de la cámara
        self.video_label = tk.Label(self.camera_frame, bg="black")
        self.video_label.pack()

        # Crear las barras futuristas para brillo, contraste, min radius y max radius en el frame de controles
        self.brightness_scale = FuturisticScale(self.control_frame, "Brillo", 0, 100, 50, row=0, command=self.update_image)
        self.contrast_scale = FuturisticScale(self.control_frame, "Contraste", 0, 100, 50, row=3, command=self.update_image)
        self.min_radius_scale = FuturisticScale(self.control_frame, "Min Radius", 0, 150, 120, row=6, command=self.update_radius)
        self.max_radius_scale = FuturisticScale(self.control_frame, "Max Radius", 0, 300, 135, row=9, command=self.update_radius)
    
        # Crear un frame para encerrar las etiquetas de distancia en un rectángulo futurista
        self.distance_frame = Frame(self.control_frame, bg="black", highlightbackground="#00A8E8", highlightthickness=2)
        self.distance_frame.grid(row=13, column=1, pady=10, padx=10)

        # Etiqueta para mostrar la distancia en píxeles
        self.distance_pixels_label = Label(self.distance_frame, text="Distancia en píxeles:", fg="white", bg="black", font=("Helvetica", 10, "bold"))
        self.distance_pixels_label.grid(row=0, column=0, pady=5, padx=5, sticky="e")
        self.distance_pixels_value = Label(self.distance_frame, text="0", fg="white", bg="black", font=("Helvetica", 10, "bold"))

        # Iniciar la actualización de la ventana
        self.update_frame()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_radius(self, _):
        self.processing_service.circle_detector.min_radius = self.min_radius_scale.value
        self.processing_service.circle_detector.max_radius = self.max_radius_scale.value

    def update_image(self, _):
        pass

    def update_frame(self):
        frame = self.processing_service.get_frame()
        if frame is None:
            print("No se pudo capturar el video desde la cámara. Saliendo...")
            self.root.quit()
            return

        brightness = self.brightness_scale.value
        contrast = self.contrast_scale.value
        frame = self.processing_service.apply_brightness_contrast(frame, brightness, contrast)

        circles = self.processing_service.detect_circles(frame)
        global radius
        roi_circle = None  # Initialize roi_circle to ensure it is defined

        if circles is not None and len(circles) > 0:
            for (x, y, radius) in circles:
                cv2.circle(frame, (x, y), radius, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
                cv2.putText(frame, f"Radio: {radius}px", (x - 50, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                self.distance_pixels_label.config(text=f"Distancia en píxeles: {radius}")
                # Extraer la región de interés (ROI) dentro del círculo
                x1, y1 = max(0, x - radius), max(0, y - radius)
                x2, y2 = min(frame.shape[1], x + radius), min(frame.shape[0], y + radius)
                roi_circle = frame[y1:y2, x1:x2]
        
        # Detectar robots en el cuadro
        if roi_circle is not None:
            rectangles = self.processing_service.detect_robots(frame)
            for (x, y, w, h, angle) in rectangles:
                # Crear una caja delimitadora rotada
                rect = ((x + w / 2, y + h / 2), (w, h), angle)
                box = cv2.boxPoints(rect)
                box = np.int32(box)
                cv2.drawContours(frame, [box], 0, (255, 0, 0), 2)
                cv2.putText(roi_circle, "Robot", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        # Contar la cantidad de robots dentro del roi_circle
        robot_count = 0
        if roi_circle is not None:
            for (x, y, w, h, angle) in rectangles:
                if x1 <= x <= x2 and y1 <= y <= y2:
                    robot_count += 1

        # Mostrar la cantidad de robots en la interfaz
        self.distance_pixels_label.config(text=f"Distancia en píxeles: {radius} | Robots detectados: {robot_count-1}")
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        image_tk = ImageTk.PhotoImage(image)
        self.video_label.config(image=image_tk)
        self.video_label.image = image_tk
        self.root.after(10, self.update_frame)

    def radius_value(self):
        return radius

    def on_closing(self):
        self.processing_service.release()
        self.root.destroy()