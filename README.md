# Plant Growth Analysis Tool

This project provides a Python-based tool to analyze and compare plant growth between two images. It uses computer vision and AI techniques to segment the plant area, calculate green coverage, and estimate growth percentage.

## Features

-   **AI-Based Cropping**: Automatically detects and crops the plant area using a YOLOv8 AI model.
-   **Multi-Panel Support**: Handles images with multiple plant panels (sides) by stitching detected regions together.
-   **Image Enhancement**: Enhances image brightness, contrast, and saturation for better analysis.
-   **Growth Calculation**: Calculates the percentage of plant coverage (green/purple pixels) and compares it between two images (Before vs. After).
-   **GUI Interface**: User-friendly Graphical User Interface (GUI) for easy operation.

## Prerequisites

-   Python 3.8 or higher
-   A virtual environment is recommended.

## Installation

1.  **Clone or Download** the repository to your local machine.

2.  **Create and Activate a Virtual Environment**:
    It is highly recommended to use a virtual environment to manage dependencies.

    ```bash
    # Create virtual environment
    python3 -m venv .venv

    # Activate virtual environment
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    Install the required Python packages using `pip`.

    ```bash
    pip install -r requirements.txt
    ```

    *Note: This will install `opencv-python`, `numpy`, `pillow`, and `ultralytics`.*

4.  **Model Weights**:
    Ensure the YOLOv8 model weights file is located at `Model/weights.pt`.

## Usage

### Running the GUI Application

The easiest way to use the tool is via the Graphical User Interface.

1.  **Activate the virtual environment** (if not already active):
    ```bash
    source .venv/bin/activate
    ```

2.  **Run the GUI script**:
    ```bash
    python gui.py
    ```

3.  **Using the App**:
    -   Click **"Select Before Image"** to choose the initial image.
    -   Click **"Select After Image"** to choose the later image.
    -   Click **"Compare Growth"** to run the analysis.
    -   The results (Plant Coverage %, Absolute Growth, Relative Growth) will be displayed.

### Running the Verification Script

To verify the pipeline works correctly on test images:

```bash
source .venv/bin/activate
python verify_full_pipeline.py
```

This script will process `test_img1.jpg` and `test_img2.jpg` (if present), generating debug images (`debug_cropped_*.jpg`, `debug_enhanced_*.jpg`) and printing growth statistics.

## Project Structure

-   `gui.py`: Main entry point for the GUI application.
-   `plant_analysis.py`: Core logic for plant analysis, including color thresholding and percentage calculation.
-   `crop.py`: Handles AI-based object detection and cropping using YOLOv8.
-   `verify_full_pipeline.py`: Script to verify the full processing pipeline.
-   `Model/weights.pt`: Pre-trained YOLOv8 model weights for plant detection.
-   `requirements.txt`: List of Python dependencies.

## Troubleshooting

-   **"No module named ..."**: Ensure you have activated the virtual environment (`source .venv/bin/activate`) and installed requirements.
-   **"Model weights not found"**: Check that `Model/weights.pt` exists.
-   **"No object detected"**: The AI model might not have found the plant panel. The tool will fall back to using the original image.

## License

[Your License Here]
