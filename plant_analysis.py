import os
from typing import Optional, Tuple

import cv2
import numpy as np
from crop import crop_front_panel


class PlantAnalyzer:
    """
    Analyzes plant images to determine growth based on plant pixel coverage.
    """

    def __init__(
        self,
        lower_green: Tuple[int, int, int] = (35, 40, 40),
        upper_green: Tuple[int, int, int] = (85, 255, 255),
        lower_purple: Tuple[int, int, int] = (125, 40, 40),
        upper_purple: Tuple[int, int, int] = (155, 255, 255),
    ):
        """
        Initialize the analyzer with HSV color ranges for plant detection.

        Args:
            lower_green: Lower bound for green color in HSV (H, S, V).
            upper_green: Upper bound for green color in HSV (H, S, V).
            lower_purple: Lower bound for purple color in HSV (H, S, V).
            upper_purple: Upper bound for purple color in HSV (H, S, V).
        """
        self.lower_green = np.array(lower_green)
        self.upper_green = np.array(upper_green)
        self.lower_purple = np.array(lower_purple)
        self.upper_purple = np.array(upper_purple)

    @staticmethod
    def enhance_image(
        image: np.ndarray,
        brightness: float = 0,
        contrast: float = 0,
        saturation: float = 1.0,
    ) -> np.ndarray:
        """
        Enhances the image by adjusting brightness, contrast, and saturation.

        Args:
            image: Input image (BGR).
            brightness: Brightness adjustment (-255 to 255).
            contrast: Contrast adjustment (-127 to 127).
            saturation: Saturation multiplier (1.0 = original).

        Returns:
            Enhanced image.
        """
        # Adjust brightness and contrast
        # Formula: new_img = alpha * old_img + beta
        # alpha = (contrast + 127) / 127 (approx) or similar mapping
        # Common simple approach:
        # if contrast > 0: delta = 127 * contrast / 100, a = 255 / (255 - delta * 2), b = a * (beta - delta)
        # But simpler cv2.convertScaleAbs is often enough for basic tweaks:
        # alpha = 1.0 + contrast / 127.0 ?
        # Let's use a standard simple formula:
        
        # Contrast: 1.0 means no change. Let's map input contrast (approx -100 to 100?) to alpha.
        # User prompt just said "adjust...". I'll assume standard params.
        # Let's treat contrast as a factor (1.0 = original) and brightness as additive.
        
        # However, to match standard "contrast/brightness" sliders often seen:
        # alpha = contrast (where 1.0 is normal)
        # beta = brightness
        
        # If the user passes "contrast" as an additive value (like in some tools), it's different.
        # Let's stick to: contrast is a multiplier (1.0 default), brightness is additive (0 default).
        
        # But for "contrast" argument in standard image processing, it's often a float.
        # Let's use: alpha = 1 + (contrast / 100.0) if we assume input is like percentage?
        # Let's assume the caller provides reasonable alpha/beta.
        # Actually, let's make it simple:
        # brightness: additive offset
        # contrast: multiplier
        
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

        Args:
            image_path: Path to the image file.
            do_crop: Whether to crop the image to the front panel.
            enhance_params: Dict with keys 'brightness', 'contrast', 'saturation'.
            save_debug: Whether to save intermediate images (cropped, enhanced).

        Returns:
            float: Percentage of plant pixels (0-100).
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found at {image_path}")

        # 1. Load and optionally Crop
        if do_crop:
            # We use a temp output path if we want to save, or just None
            debug_crop_path = (
                f"debug_cropped_{os.path.basename(image_path)}" if save_debug else None
            )
            img, _ = crop_front_panel(image_path, out_path=debug_crop_path)
        else:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image {image_path}")

        # 2. Enhance
        if enhance_params:
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

        # Threshold the HSV image to get green and purple colors
        green_mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        purple_mask = cv2.inRange(hsv, self.lower_purple, self.upper_purple)

        # Combine masks to get all plant pixels
        plant_mask = cv2.bitwise_or(green_mask, purple_mask)

        # Calculate percentage
        total_pixels = img.shape[0] * img.shape[1]
        plant_pixels = cv2.countNonZero(plant_mask)

        if total_pixels == 0:
            return 0.0

        plant_percentage = (plant_pixels / total_pixels) * 100
        return plant_percentage

    def calculate_green_percentage(self, image_path: str) -> float:
        """
        Calculates the percentage of plant pixels in an image.
        (Legacy method for backward compatibility)

        Args:
            image_path: Path to the image file.

        Returns:
            float: Percentage of plant pixels (0-100).
        """
        return self.calculate_plant_percentage(image_path)

    def compare_images(
        self,
        img1_path: str,
        img2_path: str,
        do_crop: bool = True,
        enhance_params: Optional[dict] = None,
    ) -> dict:
        """
        Compares two images and returns the growth statistics for plant coverage.

        Args:
            img1_path: Path to the first image (before).
            img2_path: Path to the second image (after).
            do_crop: Whether to apply cropping.
            enhance_params: Enhancement parameters.

        Returns:
            dict: Dictionary containing detailed coverage for both images and growth stats.
        """
        img1_percentage = self.calculate_plant_percentage(
            img1_path, do_crop=do_crop, enhance_params=enhance_params, save_debug=True
        )
        img2_percentage = self.calculate_plant_percentage(
            img2_path, do_crop=do_crop, enhance_params=enhance_params, save_debug=True
        )

        # Calculate growth
        absolute_growth = img2_percentage - img1_percentage

        # Calculate relative growth (avoiding division by zero)
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
