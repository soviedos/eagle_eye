import tkinter as tk
from tkinter import Button, Frame, Label
from services.image_processing_service import ImageProcessingService
from PIL import Image, ImageTk
import cv2

class FuturisticScale(tk.Canvas):
    def __init__(self, parent, label, min_value, max_value, initial_value, row, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.command = command

        self.width = 300
        self.height = 30

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
        self.root = tk.Tk()
        self.root.title("Eagle Eye - Interfaz de Ajuste Futurística")
        self.root.configure(bg="black")

        # Relación cm/px (se inicializa en 0 y se calculará usando el rectángulo de referencia)
        self.cm_per_px_x = 0.0
        self.cm_per_px_y = 0.0

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
        self.min_radius_scale = FuturisticScale(self.control_frame, "Min Radius", 0, 150, 0, row=6, command=self.update_radius)
        self.max_radius_scale = FuturisticScale(self.control_frame, "Max Radius", 0, 300, 100, row=9, command=self.update_radius)

        # Estado de calibración
        self.calibration_active = False

        # Botón de calibración futurista en el frame de controles
        self.calibrate_button = Button(self.control_frame, text="Calibrar", command=self.toggle_calibration,
                                       bg="#003B63", fg="white", activebackground="#00A8E8",
                                       font=("Helvetica", 12, "bold"), bd=0, relief="flat")
        self.calibrate_button.grid(row=12, column=1, pady=20)

        # Crear un frame para encerrar las etiquetas de distancia en un rectángulo blanco
        self.distance_frame = Frame(self.control_frame, bg="black", highlightbackground="white", highlightthickness=2)
        self.distance_frame.grid(row=13, column=1, pady=10, padx=10)

        # Etiqueta para mostrar la distancia en píxeles
        self.distance_pixels_label = Label(self.distance_frame, text="Distancia en píxeles: 0", fg="white", bg="black")
        self.distance_pixels_label.pack(pady=5, padx=5)

        # Etiqueta para mostrar la distancia en centímetros
        self.distance_cm_label = Label(self.distance_frame, text="Distancia en cm: 0.0", fg="white", bg="black")
        self.distance_cm_label.pack(pady=5, padx=5)

        # Calcular la relación cm/px usando el rectángulo de referencia
        self.calculate_cm_per_pixel()

        # Iniciar la actualización de la ventana
        self.update_frame()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        #********************************************************************************************************************
        #********************************************************************************************************************

    def calculate_cm_per_pixel(self):
        # Obtener un cuadro de la cámara para calcular la relación
        frame = self.processing_service.get_frame()
        if frame is None:
            print("No se pudo capturar el video desde la cámara para la calibración.")
            return

        # Convertir la imagen a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Limitar el área de búsqueda a la esquina superior izquierda
        h, w = gray.shape
        #roi = gray[0:int(h * 0.32), 0:int(w * 0.36)]

        # Mover la ROI un 20% hacia la derecha y un 15% hacia abajo
        offset_x = int(w * 0.27)  # Desplazamiento hacia la derecha
        offset_y = int(h * 0.17) # Desplazamiento hacia abajo

        # Definir las dimensiones de la ROI después del desplazamiento
        roi_width = int(w * 0.09)
        roi_height = int(h * 0.10)

        # Asegurar que no se salga de los límites de la imagen
        roi_x_end = min(offset_x + roi_width, w)
        roi_y_end = min(offset_y + roi_height, h)

        roi = gray[offset_y:roi_y_end, offset_x:roi_x_end]

        # Aplicar un desenfoque para reducir el ruido
        roi_blurred = cv2.GaussianBlur(roi, (5, 5), 0)

        # Aplicar un umbral binario simple en lugar de un umbral adaptativo
        _, thresh = cv2.threshold(roi_blurred, 200, 255, cv2.THRESH_BINARY)

        # Invertir la imagen para que los contornos blancos sean detectados mejor
        thresh = cv2.bitwise_not(thresh)

        # Encontrar contornos en la región limitada (ROI)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Crear una copia de la ROI para dibujar el rectángulo
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)

        # Encontrar contornos en la región limitada (ROI)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Variable para rastrear si se encuentra un rectángulo
        rect_found = False

        # Buscar el contorno que corresponda al rectángulo blanco
        for contour in contours:
            x, y, w_rect, h_rect = cv2.boundingRect(contour)
            aspect_ratio = w_rect / h_rect
            area = cv2.contourArea(contour)

            # Ajustar el criterio del aspecto del rectángulo y su área mínima
            if 1.0 <= aspect_ratio <= 1.6 and area > 100:
                self.cm_per_px_x = w_rect / 14
                self.cm_per_px_y = h_rect / 10.5
                print(f"Rectángulo detectado: Ancho (px) = {w_rect}, Alto (px) = {h_rect}")
                print(f"Relación cm/px calculada: {self.cm_per_px_x:.4f} cm/px (ancho), {self.cm_per_px_y:.4f} cm/px (alto)")

                # Dibujar el rectángulo detectado en la ROI
                cv2.rectangle(roi_rgb, (x, y), (x + w_rect, y + h_rect), (0, 255, 0), 2)
                rect_found = True
                break

        if not rect_found:
            print("No se encontró un rectángulo blanco en la ROI.")

         # Convertir la ROI a formato compatible con Tkinter
        roi_image = Image.fromarray(roi_rgb)
        roi_tk = ImageTk.PhotoImage(roi_image)

        # Si la ventana de la ROI ya existe, actualizarla; si no, crearla
        if not hasattr(self, 'roi_window') or not self.roi_window.winfo_exists():
            self.roi_window = tk.Toplevel(self.root)
            self.roi_window.title("ROI - Rectángulo de Referencia")
            self.roi_label = tk.Label(self.roi_window, image=roi_tk)
            self.roi_label.image = roi_tk  # Mantener una referencia para evitar que la imagen sea recolectada por el garbage collector
            self.roi_label.pack()

            # Mover la ventana a la posición deseada (e.g., 100 px hacia la derecha y 100 px hacia abajo)
            self.roi_window.geometry("+500+235")
        else:
            self.roi_label.config(image=roi_tk)
            self.roi_label.image = roi_tk

        # Forzar la actualización de la ventana de Tkinter
        self.roi_window.update_idletasks()
        self.roi_window.update()


        #*********************************************************************************************************************
        #*********************************************************************************************************************
        #*********************************************************************************************************************

    def toggle_calibration(self):
        self.calibration_active = not self.calibration_active
        if self.calibration_active:
            self.calibrate_button.config(bg="green", fg="black")
        else:
            self.calibrate_button.config(bg="#003B63", fg="white")
        print(f"Calibración {'activada' if self.calibration_active else 'desactivada'}")

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

        if circles is not None and len(circles) > 0:
            for (x, y, radius) in circles:
                cv2.circle(frame, (x, y), radius, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
                if self.cm_per_px_x > 0 and self.cm_per_px_y > 0:
                    radius_cm = self.convert_pixels_to_cm(radius, axis='x')
                    cv2.putText(frame, f"Radio: {radius_cm:.2f} cm", (x - 50, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Actualizar las etiquetas con las distancias en píxeles y centímetros
                    self.distance_pixels_label.config(text=f"Distancia en píxeles: {radius}")
                    self.distance_cm_label.config(text=f"Distancia en cm: {radius_cm:.2f}")
                else:
                    cv2.putText(frame, f"Radio: {radius}px", (x - 50, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    self.distance_pixels_label.config(text=f"Distancia en píxeles: {radius}")
                    self.distance_cm_label.config(text="Distancia en cm: N/A")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        image_tk = ImageTk.PhotoImage(image)
        self.video_label.config(image=image_tk)
        self.video_label.image = image_tk
        self.root.after(10, self.update_frame)

    def convert_pixels_to_cm(self, pixels, axis='x'):
        if axis == 'x':
            return pixels * self.cm_per_px_x
        elif axis == 'y':
            return pixels * self.cm_per_px_y
        return 0

    def on_closing(self):
        self.processing_service.release()
        self.root.destroy()