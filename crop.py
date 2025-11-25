import cv2
import numpy as np
from ultralytics import YOLO
import os

# Initialize model globally to avoid reloading on every call if possible, 
# but for safety in this script context, we'll load it inside or check if loaded.
# Better to load it once if this module is imported.
MODEL_PATH = os.path.join(os.path.dirname(__file__), "Model", "weights.pt")
model = None

def load_model():
    global model
    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model weights not found at {MODEL_PATH}")
        print(f"Loading YOLO model from {MODEL_PATH}...")
        model = YOLO(MODEL_PATH)
    return model

def crop_front_panel(image_path, out_path="output.jpg"):
    """
    Crops the front panel(s) of the plant image using YOLOv8 detection.
    
    Logic:
    - If 1 side detected: Crop and return.
    - If 2+ sides detected: Merge (stitch) them into a single image.
    - If 0 detected: Return original.

    Args:
        image_path (str): Path to the input image.
        out_path (str, optional): Path to save the cropped image. Defaults to "output.jpg".

    Returns:
        tuple: (cropped_image_np_array, output_path_used)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image {image_path}")

    model = load_model()
    
    # Run inference
    results = model(image_path, verbose=False)
    boxes = results[0].boxes
    
    final_img = img
    
    if len(boxes) > 0:
        # Collect valid detections
        detections = []
        for box in boxes:
            # Optional: Filter by confidence if needed, e.g. box.conf > 0.3
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
            print(f"Merged {len(crops)} detected sides into one image.")
    else:
        print(f"Warning: No object detected in {image_path}. Returning original image.")

    if out_path:
        cv2.imwrite(out_path, final_img)
        
    return final_img, out_path


if __name__ == "__main__":
    # Example usage
    try:
        crop_front_panel("test_img1.jpg", "cropped_test_ai.jpg")
        print("Test AI crop successful.")
    except Exception as e:
        print(f"Error: {e}")
