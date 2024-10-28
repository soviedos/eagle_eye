# ui/image_adjustment.py
import cv2
from services.image_processing_service import ImageProcessingService

class ImageAdjustmentUI:
    def __init__(self, processing_service: ImageProcessingService):
        self.processing_service = processing_service

    def setup_adjustment_interface(self):
        cv2.namedWindow('Ajustes')
        cv2.createTrackbar('param1', 'Ajustes', 50, 300, self._nothing)
        cv2.createTrackbar('param2', 'Ajustes', 30, 100, self._nothing)
        cv2.createTrackbar('minRadius', 'Ajustes', 0, 100, self._nothing)
        cv2.createTrackbar('maxRadius', 'Ajustes', 100, 300, self._nothing)
        cv2.createTrackbar('Detect Black Circle', 'Ajustes', 0, 1, self._nothing)

        while True:
            param1 = cv2.getTrackbarPos('param1', 'Ajustes')
            param2 = cv2.getTrackbarPos('param2', 'Ajustes')
            min_radius = cv2.getTrackbarPos('minRadius', 'Ajustes')
            max_radius = cv2.getTrackbarPos('maxRadius', 'Ajustes')
            detect_black_circle = cv2.getTrackbarPos('Detect Black Circle', 'Ajustes') == 1

            self.processing_service.circle_detector.param1 = param1
            self.processing_service.circle_detector.param2 = param2
            self.processing_service.circle_detector.min_radius = min_radius
            self.processing_service.circle_detector.max_radius = max_radius

            self.processing_service.process_images(detect_black_circle)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    def _nothing(self, x):
        pass
