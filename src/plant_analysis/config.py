import os
import numpy as np

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, "Model")
MODEL_WEIGHTS_PATH = os.path.join(MODEL_DIR, "weights.pt")

# Color Ranges (HSV)
LOWER_GREEN = np.array([35, 40, 40])
UPPER_GREEN = np.array([85, 255, 255])

LOWER_PURPLE = np.array([125, 40, 40])
UPPER_PURPLE = np.array([155, 255, 255])

# GUI Settings
WINDOW_TITLE = "Plant Growth Comparison"
WINDOW_SIZE = "800x600"
PREVIEW_SIZE = (250, 250)

# Analysis Defaults
DEFAULT_CONFIDENCE_THRESHOLD = 0.25
