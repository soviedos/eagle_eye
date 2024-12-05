import tkinter as tk
import numpy as np
from tkinter import Button, Frame, Label
from services.image_processing_service import ImageProcessingService
from PIL import Image, ImageTk
from business.robot_detector import RobotDetector
import cv2
from PIL import Image, ImageDraw, ImageTk
import random  # Import the random module

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
        self.roi_rect = (0, 0, 100, 100)  # Example values, adjust as needed
        self.root = tk.Tk()
        self.robot_paths = {}  # Initialize robot_paths
        self.robot_windows = {}  # Initialize robot_windows
        self.robot_colors = {}  # Initialize robot_colors
        self.robot_counter = 0  # Initialize robot_counter
        self.robot_ids = {}  # Initialize robot_ids
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

    def create_robot_window(self, robot_id):
            window = tk.Toplevel(self.root)
            window.title(f"Recorrido del Robot {robot_id}")
            window.configure(bg="black")
            label = tk.Label(window, bg="black")
            label.pack()
            self.robot_windows[robot_id] = label

    def update_robot_window(self, robot_id):
        path_image = np.zeros((500, 500, 3), dtype=np.uint8)
        path_image.fill(0)  # Fondo negro
        color = self.robot_colors[robot_id]  # Obtener el color asignado al robot
        for position in self.robot_paths[robot_id]:
            cv2.circle(path_image, position, 3, color, -1)  # Dibujar un punto en cada posición
        path_image = cv2.cvtColor(path_image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(path_image)
        image_tk = ImageTk.PhotoImage(image)
        self.robot_windows[robot_id].config(image=image_tk)
        self.robot_windows[robot_id].image = image_tk

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
        circle_x, circle_y = None, None  # Initialize circle_x and circle_y

        if circles is not None and len(circles) > 0:
            for (circle_x, circle_y, radius) in circles:
                cv2.circle(frame, (circle_x, circle_y), radius, (0, 255, 0), 2)
                cv2.circle(frame, (circle_x, circle_y), 2, (0, 0, 255), 3)
                self.distance_pixels_label.config(text=f"Distancia en píxeles: {radius}")
                # Extraer la región de interés (ROI) dentro del círculo
                x1, y1 = max(0, circle_x - radius), max(0, circle_y - radius)
                x2, y2 = min(frame.shape[1], circle_x + radius), min(frame.shape[0], circle_y + radius)
                roi_circle = frame[y1:y2, x1:x2]

        robots = self.processing_service.detect_robots(frame)
        if robots is not None and len(robots) > 0:
            for (x, y, w, h, conf, cls) in robots:
                # Verificar si el robot está fuera del círculo
                robot_center_x = x + w // 2
                robot_center_y = y + h // 2
                if circle_x is not None and circle_y is not None:
                    distance_to_center = ((robot_center_x - circle_x) ** 2 + (robot_center_y - circle_y) ** 2) ** 0.5
                    if distance_to_center > radius:
                        color = (0, 0, 255)  # Rojo
                        cv2.putText(frame, "Fuera del círculo", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    else:
                        color = (255, 0, 0)  # Azul
                else:
                    color = (255, 0, 0)  # Azul

                # Dibujar el rectángulo del robot
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

                # Asignar un ID único al robot
                if (x, y, w, h) not in self.robot_ids:
                    self.robot_ids[(x, y, w, h)] = self.robot_counter
                    self.robot_counter += 1
                robot_id = self.robot_ids[(x, y, w, h)]

                #label = f"Robot {robot_id} {conf:.2f}"
                #cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # Actualizar el mapa del recorrido del robot
                robot_id = int(cls)
                if robot_id not in self.robot_paths:
                    self.robot_paths[robot_id] = []
                    # Asignar un color sólido al robot y asegurarse de que sea único
                    while True:
                        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        if color not in self.robot_colors.values():
                            self.robot_colors[robot_id] = color
                            break
                    self.create_robot_window(robot_id)
                self.robot_paths[robot_id].append((robot_center_x, robot_center_y))

                # Dibujar el recorrido del robot en su ventana
                self.update_robot_window(robot_id)

        
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