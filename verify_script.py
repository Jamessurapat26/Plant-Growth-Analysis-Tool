import os

import cv2
import numpy as np

from plant_analysis import PlantAnalyzer


def create_test_image(filename, size, green_ratio=0, purple_ratio=0):
    """Creates a black image with green and purple squares in the center."""
    img = np.zeros((size, size, 3), dtype=np.uint8)

    total_pixels = size * size

    # Calculate green square
    if green_ratio > 0:
        green_pixels_needed = total_pixels * green_ratio
        green_square_side = int(np.sqrt(green_pixels_needed))
        green_start = (size - green_square_side) // 2
        green_end = green_start + green_square_side

        # Draw green square (BGR format: 0, 255, 0)
        img[green_start:green_end, green_start:green_end] = [0, 255, 0]

    # Calculate purple square (positioned to the right of green)
    if purple_ratio > 0:
        purple_pixels_needed = total_pixels * purple_ratio
        purple_square_side = int(np.sqrt(purple_pixels_needed))
        purple_start = (size - purple_square_side) // 2
        purple_end = purple_start + purple_square_side

        # Offset purple square to the right if both colors exist
        if green_ratio > 0:
            purple_start = green_end + 10
            purple_end = purple_start + purple_square_side

            # Ensure purple square stays within image bounds
            if purple_end > size:
                purple_start = (size - purple_square_side) // 2
                purple_end = purple_start + purple_square_side

        # Draw purple square (BGR format: 255, 0, 255 - magenta/purple)
        img[purple_start:purple_end, purple_start:purple_end] = [255, 0, 255]

    total_coverage = green_ratio + purple_ratio
    print(
        f"Created {filename} with {green_ratio * 100:.1f}% green, {purple_ratio * 100:.1f}% purple (total: {total_coverage * 100:.1f}%)"
    )
    cv2.imwrite(filename, img)


def main():
    print("Generating test images for green and purple plant analysis...")
    img1 = "test_img1.jpg"
    img2 = "test_img2.jpg"

    # Create test images with mixed colors
    # Image 1: 10% green, 5% purple (total 15% plant coverage)
    create_test_image(img1, 200, green_ratio=0.1, purple_ratio=0.05)

    # Image 2: 20% green, 10% purple (total 30% plant coverage)
    create_test_image(img2, 200, green_ratio=0.2, purple_ratio=0.1)

    print("\nRunning PlantAnalyzer...")
    analyzer = PlantAnalyzer()

    try:
        results = analyzer.compare_images(img1, img2)

        # Display detailed results
        print("\n=== IMAGE 1 (BEFORE) ===")
        img1_data = results["image1"]
        print(f"Plant Coverage: {img1_data['plant_percentage']:.2f}%")

        print("\n=== IMAGE 2 (AFTER) ===")
        img2_data = results["image2"]
        print(f"Plant Coverage: {img2_data['plant_percentage']:.2f}%")

        print("\n=== GROWTH ANALYSIS ===")
        growth = results["growth"]
        print(
            f"Plant Growth: {growth['absolute']:+.2f}% ({growth['relative']:+.1f}% relative)"
        )

        # Test individual image analysis
        print("\n=== INDIVIDUAL IMAGE TEST ===")
        single_img_result = analyzer.calculate_plant_percentage(img1)
        print(f"Single image analysis - Plant Coverage: {single_img_result:.2f}%")

    except Exception as e:
        print(f"Error: {e}")

    # Cleanup
    # os.remove(img1)
    # os.remove(img2)


if __name__ == "__main__":
    main()
