# Eagle Eye - Sistema de Detección y Seguimiento de Robots

Eagle Eye es un sistema de visión por computadora en tiempo real que combina técnicas tradicionales de OpenCV con deep learning (YOLOv5) para detectar y rastrear robots dentro de un área circular definida. El proyecto implementa una arquitectura modular con una interfaz gráfica futurística para ajuste de parámetros en tiempo real.

## 🎯 Características Principales

- **Detección Multimodal**: Combina OpenCV HoughCircles para detección de círculos y YOLOv5 personalizado para detección de robots
- **Análisis Espacial**: Determina si los robots están dentro o fuera del área circular de referencia
- **Tracking Inteligente**: Seguimiento individual de múltiples robots con trayectorias históricas
- **Interfaz Futurística**: Controles personalizados en tiempo real con Tkinter
- **Visualización Avanzada**: Código de colores y ventanas individuales para cada robot

## 🏗️ Arquitectura del Sistema

```
eagle_eye/
├── main.py                    # Punto de entrada principal
├── business/                  # Lógica de negocio
│   ├── circle_detector.py     # Detección de círculos con OpenCV
│   └── robot_detector.py      # Detección de robots con YOLOv5
├── services/                  # Servicios de procesamiento
│   └── image_processing_service.py  # Captura y procesamiento de cámara
├── ui/                        # Interfaz de usuario
│   └── image_adjustment.py    # UI futurística con Tkinter
└── yolov5/                    # Framework YOLOv5 integrado
    └── runs/train/eagle_eye_training/weights/best.pt  # Modelo entrenado
```

## 🚀 Instalación y Configuración

### Prerequisitos

- Python 3.7+
- Cámara web conectada
- Modelo YOLOv5 entrenado

### Dependencias

```bash
pip install opencv-python
pip install torch torchvision
pip install pillow
pip install numpy
pip install pyyaml
```

### Configuración

1. **Clona el repositorio YOLOv5** (se hace automáticamente si no existe):
   ```bash
   git clone https://github.com/ultralytics/yolov5.git
   ```

2. **Asegúrate de tener el modelo entrenado** en:
   ```
   ./yolov5/runs/train/eagle_eye_training/weights/best.pt
   ```

3. **Ejecuta la aplicación**:
   ```bash
   python3 main.py
   ```

## 🎮 Uso de la Aplicación

### Controles Principales

- **Brillo**: Ajusta la luminosidad de la imagen (0-100)
- **Contraste**: Modifica el contraste de la imagen (0-100)
- **Min Radius**: Radio mínimo para detección de círculos (0-150)
- **Max Radius**: Radio máximo para detección de círculos (0-300)

### Indicadores Visuales

- **Círculo Verde**: Área de referencia detectada
- **Punto Rojo**: Centro del círculo
- **Rectángulo Azul**: Robot dentro del área circular
- **Rectángulo Rojo**: Robot fuera del área circular
- **Ventanas Emergentes**: Trayectoria individual de cada robot

## 🔧 Componentes Técnicos

### CircleDetector
- **Algoritmo**: OpenCV HoughCircles
- **Filtrado**: Por intensidad promedio (< 70 para círculos oscuros)
- **Rango de detección**: 147-169 píxeles (configurable)

### RobotDetector
- **Modelo**: YOLOv5 personalizado
- **Umbral de confianza**: ≥ 0.7
- **Salida**: Coordenadas, confianza y clase de cada detección

### ImageProcessingService
- **Entrada**: VideoCapture(0) - Cámara principal
- **Procesamiento**: Ajuste de brillo/contraste en tiempo real
- **Frecuencia**: ~100 FPS (actualización cada 10ms)

### ImageAdjustmentUI
- **Framework**: Tkinter con controles personalizados
- **Características**: Barras futurísticas, tracking multiobjetc, ventanas emergentes

## 📊 Flujo de Procesamiento

1. **Captura de Frame**: Obtiene imagen de la cámara
2. **Ajustes de Imagen**: Aplica brillo y contraste
3. **Detección de Círculos**: Identifica área de referencia
4. **Detección de Robots**: Localiza objetos móviles
5. **Análisis Espacial**: Determina posición relativa
6. **Actualización Visual**: Renderiza resultados
7. **Tracking**: Actualiza trayectorias históricas

## 🎯 Parámetros de Configuración

### Detección de Círculos
- `param1 = 50`: Umbral superior para detector de bordes
- `param2 = 30`: Umbral de acumulación para centros
- `minDist = 50`: Distancia mínima entre círculos
- `dp = 1.2`: Relación inversa de resolución

### Detección de Robots
- `confidence_threshold = 0.7`: Umbral mínimo de confianza
- `model_path`: Ruta al modelo YOLOv5 entrenado

### Interfaz
- `update_interval = 10ms`: Frecuencia de actualización
- `color_coding`: Sistema de colores para estado de robots

## 🔍 Funcionalidades Avanzadas

### Tracking Multiobjetc
- Asignación automática de IDs únicos
- Persistencia de trayectorias entre frames
- Colores distintivos por robot

### Análisis Espacial
- Cálculo de distancia euclidiana robot-centro
- Clasificación automática dentro/fuera
- Alertas visuales en tiempo real

### Calibración Dinámica
- Ajuste de parámetros sin reinicio
- Feedback visual inmediato
- Persistencia de configuración durante sesión

## 🐛 Solución de Problemas

### Errores Comunes

1. **"No se pudo abrir la cámara"**
   - Verificar que la cámara esté conectada
   - Comprobar permisos de acceso
   - Intentar cambiar índice de cámara en código

2. **"Error al cargar el modelo"**
   - Verificar ruta del modelo entrenado
   - Comprobar que YOLOv5 esté instalado
   - Revisar dependencias de PyTorch

3. **"Detección imprecisa"**
   - Ajustar parámetros de brillo/contraste
   - Calibrar rangos de radio
   - Verificar iluminación del entorno

### Optimización de Rendimiento

- Usar GPU si está disponible (CUDA)
- Ajustar resolución de entrada
- Optimizar umbral de confianza
- Limitar número de objetos tracked simultáneamente

## 📈 Roadmap Futuro

- [ ] Exportación de datos de trayectorias
- [ ] Configuración persistente
- [ ] Calibración automática de parámetros
- [ ] Soporte para múltiples cámaras
- [ ] API REST para integración externa
- [ ] Análisis estadístico de comportamiento

## 👥 Contribuciones

Desarrollado por: **Sergio Oviedo**  
Fecha: **Octubre 2024**  
Versión: **1.0**

## 📄 Licencia

Este proyecto forma parte del programa de Maestría en Inteligencia Artificial de la Universidad Cenfotec.

---
*Eagle Eye - Vigilancia Inteligente con Visión por Computadora* 🦅👁️