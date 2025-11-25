import cv2
import numpy as np

def create_dummy_image(filename, color):
    # Create a 100x100 image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    # Fill with color (BGR)
    img[:] = color
    cv2.imwrite(filename, img)
    print(f"Created {filename}")

if __name__ == "__main__":
    # Greenish
    create_dummy_image("test_img1.jpg", (40, 200, 40))
    # More Greenish
    create_dummy_image("test_img2.jpg", (40, 255, 40))
