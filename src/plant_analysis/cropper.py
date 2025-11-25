import cv2
import numpy as np
import os
from ultralytics import YOLO

from .config import MODEL_WEIGHTS_PATH
from .utils import get_logger

logger = get_logger("PlantAnalysis.Cropper")

# Initialize model globally to avoid reloading
_model = None

def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_WEIGHTS_PATH):
            logger.error(f"Model weights not found at {MODEL_WEIGHTS_PATH}")
            raise FileNotFoundError(f"Model weights not found at {MODEL_WEIGHTS_PATH}")
        
        logger.info(f"Loading YOLO model from {MODEL_WEIGHTS_PATH}...")
        try:
            _model = YOLO(MODEL_WEIGHTS_PATH)
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    return _model

def crop_front_panel(image_path, out_path=None):
    """
    Crops the front panel(s) of the plant image using YOLOv8 detection.
    
    Logic:
    - If 1 side detected: Crop and return.
    - If 2+ sides detected: Merge (stitch) them into a single image.
    - If 0 detected: Return original.

    Args:
        image_path (str): Path to the input image.
        out_path (str, optional): Path to save the cropped image.

    Returns:
        tuple: (cropped_image_np_array, output_path_used)
    """
    logger.info(f"Processing image for cropping: {image_path}")
    
    img = cv2.imread(image_path)
    if img is None:
        logger.error(f"Could not read image {image_path}")
        raise ValueError(f"Could not read image {image_path}")

    try:
        model = load_model()
        results = model(image_path, verbose=False)
        boxes = results[0].boxes
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return img, out_path

    final_img = img
    
    if len(boxes) > 0:
        logger.info(f"Detected {len(boxes)} objects.")
        # Collect valid detections
        detections = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            detections.append({'coords': (x1, y1, x2, y2)})
        
        # Sort left-to-right
        detections.sort(key=lambda d: d['coords'][0])
        
        crops = []
        h_img, w_img = img.shape[:2]
        
        for d in detections:
            x1, y1, x2, y2 = d['coords']
            # Clip to bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_img, x2), min(h_img, y2)
            
            crop = img[y1:y2, x1:x2]
            if crop.size > 0:
                crops.append(crop)
        
        if len(crops) == 1:
            final_img = crops[0]
        elif len(crops) >= 2:
            # Merge logic: Resize to match the height of the tallest crop
            max_h = max(c.shape[0] for c in crops)
            resized_crops = []
            for c in crops:
                h, w = c.shape[:2]
                if h != max_h:
                    scale = max_h / h
                    new_w = int(w * scale)
                    resized = cv2.resize(c, (new_w, max_h))
                    resized_crops.append(resized)
                else:
                    resized_crops.append(c)
            
            # Stitch horizontally
            final_img = cv2.hconcat(resized_crops)
            logger.info(f"Merged {len(crops)} detected sides into one image.")
    else:
        logger.warning(f"No object detected in {image_path}. Returning original image.")

    if out_path:
        cv2.imwrite(out_path, final_img)
        logger.info(f"Saved cropped image to {out_path}")
        
    return final_img, out_path
