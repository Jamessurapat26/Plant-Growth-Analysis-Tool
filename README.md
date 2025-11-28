# Plant Growth Analysis Tool

This project provides a Python-based tool to analyze and compare plant growth between two images. It uses computer vision and AI techniques to segment the plant area, calculate green coverage, and estimate growth percentage.

## Features

-   **AI-Based Cropping**: Automatically detects and crops the plant area using a YOLOv8 AI model.
-   **Multi-Panel Support**: Handles images with multiple plant panels (sides) by stitching detected regions together.
-   **Image Enhancement**: Enhances image brightness, contrast, and saturation for better analysis.
-   **Growth Calculation**: Calculates the percentage of plant coverage (green/purple pixels) and compares it between two images (Before vs. After).
-   **GUI Interface**: User-friendly Graphical User Interface (GUI) for easy operation.

## How It Works

### 1. Image Segmentation (AI Cropping)
The tool uses a pre-trained **YOLOv8** model to detect the plant panel in the image.
- **Single Detection**: If one panel is found, it is cropped directly.
- **Multiple Detections**: If multiple panels (sides) are found, they are sorted left-to-right, resized to the same height, and stitched together horizontally into a single image.
- **No Detection**: If no panel is found, the original image is used.

### 2. Image Enhancement
Before analysis, the image can be enhanced to improve detection accuracy:
- **Contrast/Brightness**: Adjusted using linear scaling.
- **Saturation**: Adjusted in the HSV color space to make plant colors more distinct.

### 3. Plant Coverage Analysis
The core analysis uses **Color Thresholding** in the HSV (Hue, Saturation, Value) space.
- **Green Mask**: Detects green leaves (Hue: 35-85).
- **Purple Mask**: Detects purple leaves (Hue: 125-155).
- **Calculation**:
  `Plant Percentage = (Count of Green + Purple Pixels / Total Pixels) * 100`

### 4. Growth Comparison
To measure growth, the tool compares the "Plant Percentage" of the *Before* and *After* images.
- **Absolute Growth**: `Percentage_After - Percentage_Before`
- **Relative Growth**: `(Absolute Growth / Percentage_Before) * 100`

## Prerequisites

-   Python 3.8 or higher
-   **Optional but Recommended**: [uv](https://github.com/astral-sh/uv) (An extremely fast Python package installer and resolver).

## Installation & Usage

You can run this project using either `uv` (recommended) or standard Python/pip.

### Option 1: Using `uv` (Fastest)

If you have `uv` installed, you can run the application directly without manually creating a virtual environment.

1.  **Run the Application**:
    ```bash
    uv run main.py
    ```
    *`uv` will automatically create a virtual environment, install dependencies from `pyproject.toml`, and launch the app.*

2.  **Run Verification Script**:
    ```bash
    uv run verify_full_pipeline.py
    ```

### Option 2: Using Standard Python (`pip`)

1.  **Create and Activate a Virtual Environment**:
    ```bash
    # Create virtual environment
    python3 -m venv .venv

    # Activate virtual environment
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate   # On Windows
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python main.py
    ```

## Using the App

1.  Click **"Select Before Image"** to choose the initial image.
2.  Click **"Select After Image"** to choose the later image.
3.  Click **"Compare Growth"** to run the analysis.
4.  The results (Plant Coverage %, Absolute Growth, Relative Growth) will be displayed.

## Project Structure

-   `src/plant_analysis/`: Source code package.
    -   `analyzer.py`: Core logic for plant analysis.
    -   `cropper.py`: AI-based object detection and cropping.
    -   `gui.py`: Graphical User Interface.
    -   `config.py`: Configuration constants.
-   `main.py`: Entry point for the application.
-   `verify_full_pipeline.py`: Script to verify the pipeline.
-   `Model/weights.pt`: Pre-trained YOLOv8 model weights.
-   `pyproject.toml`: Project configuration and dependencies.

## Troubleshooting

-   **"Model weights not found"**: Check that `Model/weights.pt` exists.
-   **"No object detected"**: The AI model might not have found the plant panel. The tool will fall back to using the original image.
-   **Dependency Issues**: If using `uv`, try running `uv sync` to refresh the environment. If using `pip`, ensure your virtual environment is active.
