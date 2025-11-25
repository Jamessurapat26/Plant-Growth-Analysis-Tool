import os
import cv2
import numpy as np
from typing import Optional, Tuple

from .config import LOWER_GREEN, UPPER_GREEN, LOWER_PURPLE, UPPER_PURPLE
from .cropper import crop_front_panel
from .utils import get_logger

logger = get_logger("PlantAnalysis.Analyzer")

class PlantAnalyzer:
    """
    Analyzes plant images to determine growth based on plant pixel coverage.
    """

    def __init__(self):
        """
        Initialize the analyzer with HSV color ranges from config.
        """
        self.lower_green = LOWER_GREEN
        self.upper_green = UPPER_GREEN
        self.lower_purple = LOWER_PURPLE
        self.upper_purple = UPPER_PURPLE

    @staticmethod
    def enhance_image(
        image: np.ndarray,
        brightness: float = 0,
        contrast: float = 0,
        saturation: float = 1.0,
    ) -> np.ndarray:
        """
        Enhances the image by adjusting brightness, contrast, and saturation.
        """
        # Adjust brightness and contrast
        # alpha = 1.0 + contrast (where 1.0 is normal)
        # beta = brightness
        img_enhanced = cv2.convertScaleAbs(image, alpha=1.0 + contrast, beta=brightness)

        # Adjust saturation
        if saturation != 1.0:
            hsv = cv2.cvtColor(img_enhanced, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            s = s.astype(np.float32) * saturation
            s = np.clip(s, 0, 255).astype(np.uint8)
            hsv = cv2.merge([h, s, v])
            img_enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return img_enhanced

    def calculate_plant_percentage(
        self,
        image_path: str,
        do_crop: bool = True,
        enhance_params: Optional[dict] = None,
        save_debug: bool = False,
    ) -> float:
        """
        Calculates the percentage of plant pixels in an image.
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file not found at {image_path}")
            raise FileNotFoundError(f"Image file not found at {image_path}")

        logger.info(f"Analyzing image: {image_path}")

        # 1. Load and optionally Crop
        if do_crop:
            debug_crop_path = (
                f"debug_cropped_{os.path.basename(image_path)}" if save_debug else None
            )
            img, _ = crop_front_panel(image_path, out_path=debug_crop_path)
        else:
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Could not read image {image_path}")
                raise ValueError(f"Could not read image {image_path}")

        # 2. Enhance
        if enhance_params:
            logger.info(f"Applying enhancement: {enhance_params}")
            img = self.enhance_image(
                img,
                brightness=enhance_params.get("brightness", 0),
                contrast=enhance_params.get("contrast", 0),
                saturation=enhance_params.get("saturation", 1.0),
            )
            if save_debug:
                cv2.imwrite(f"debug_enhanced_{os.path.basename(image_path)}", img)

        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Threshold the HSV image
        green_mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        purple_mask = cv2.inRange(hsv, self.lower_purple, self.upper_purple)

        # Combine masks
        plant_mask = cv2.bitwise_or(green_mask, purple_mask)

        # Calculate percentage
        total_pixels = img.shape[0] * img.shape[1]
        plant_pixels = cv2.countNonZero(plant_mask)

        if total_pixels == 0:
            return 0.0

        plant_percentage = (plant_pixels / total_pixels) * 100
        logger.info(f"Plant percentage: {plant_percentage:.2f}%")
        return plant_percentage

    def compare_images(
        self,
        img1_path: str,
        img2_path: str,
        do_crop: bool = True,
        enhance_params: Optional[dict] = None,
    ) -> dict:
        """
        Compares two images and returns the growth statistics.
        """
        logger.info(f"Comparing images: {img1_path} vs {img2_path}")
        
        img1_percentage = self.calculate_plant_percentage(
            img1_path, do_crop=do_crop, enhance_params=enhance_params, save_debug=True
        )
        img2_percentage = self.calculate_plant_percentage(
            img2_path, do_crop=do_crop, enhance_params=enhance_params, save_debug=True
        )

        # Calculate growth
        absolute_growth = img2_percentage - img1_percentage
        relative_growth = (
            (absolute_growth / img1_percentage * 100) if img1_percentage > 0 else 0.0
        )

        return {
            "image1": {
                "plant_percentage": img1_percentage,
            },
            "image2": {
                "plant_percentage": img2_percentage,
            },
            "growth": {
                "absolute": absolute_growth,
                "relative": relative_growth,
            },
        }
