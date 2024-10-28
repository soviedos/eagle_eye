# data/image_loader.py
import cv2
import os
from typing import List

class ImageLoader:
    def __init__(self, directory: str, extension: str):
        self.directory = directory
        self.extension = extension

    def load_images(self) -> List[str]:
        image_files = [f for f in os.listdir(self.directory) if f.endswith(self.extension)]
        image_files.sort()
        return image_files

    def save_image(self, image, filename: str):
        cv2.imwrite(os.path.join(self.directory, filename), image)
