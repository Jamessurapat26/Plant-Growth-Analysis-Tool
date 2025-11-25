import os
import json
from plant_analysis import PlantAnalyzer

def main():
    print("Starting verification of full pipeline...")
    
    analyzer = PlantAnalyzer()
    
    img1 = "test_img1.jpg"
    img2 = "test_img2.jpg"
    
    if not os.path.exists(img1) or not os.path.exists(img2):
        print(f"Error: Test images not found. {img1}: {os.path.exists(img1)}, {img2}: {os.path.exists(img2)}")
        return

    # Define enhancement parameters
    # Increase contrast by 20% (0.2), brightness by 10, saturation by 1.2x
    enhance_params = {
        "brightness": 10,
        "contrast": 0.2,
        "saturation": 1.2
    }
    
    print(f"Running comparison with enhancement: {enhance_params}")
    
    try:
        results = analyzer.compare_images(
            img1, 
            img2, 
            do_crop=True, 
            enhance_params=enhance_params
        )
        
        print("\nResults:")
        print(json.dumps(results, indent=2))
        
        # Check for debug images
        debug_files = [
            f"debug_cropped_{img1}",
            f"debug_cropped_{img2}",
            f"debug_enhanced_{img1}",
            f"debug_enhanced_{img2}"
        ]
        
        print("\nChecking for debug output files:")
        for f in debug_files:
            if os.path.exists(f):
                print(f"[OK] {f} generated.")
            else:
                print(f"[FAIL] {f} NOT generated.")
                
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
