"""
Project: Eagle Eye - Circle Detection System
File: main.py
Description: This script initializes and runs the image processing application for detecting circles
             (both inner black and outer white) using OpenCV. It provides a real-time interface for
             adjusting detection parameters.
             
Author: Sergio Oviedo
Date: 2024-10-27
Version: 1.0

Dependencies:
    - Python 3.7+
    - OpenCV (opencv-python)
    - Numpy
    - Matplotlib

Usage:
    - Run the script from the root directory using:
      python3 main.py
    - Adjust the parameters in the OpenCV window to calibrate the circle detection algorithm.

Notes:
    - Ensure that the 'Fotos' directory contains the input images.
    - The script should be executed from the project root for imports to work correctly.

"""



from data.image_loader import ImageLoader
from business.circle_detector import CircleDetector
from services.image_processing_service import ImageProcessingService
from ui.image_adjustment import ImageAdjustmentUI

def main():
    image_directory = 'Fotos/Fotos Sergio'
    image_extension = '.jpg'
    output_directory = 'Fotos/Generadas/'

    image_loader = ImageLoader(image_directory, image_extension)
    circle_detector = CircleDetector()
    processing_service = ImageProcessingService(image_loader, circle_detector)
    adjustment_ui = ImageAdjustmentUI(processing_service)

    adjustment_ui.setup_adjustment_interface()

if __name__ == "__main__":
    main()
