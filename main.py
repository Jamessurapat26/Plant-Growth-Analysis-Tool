import tkinter as tk
from src.plant_analysis.gui import PlantGrowthApp
from src.plant_analysis.utils import setup_logging, get_logger

def main():
    # Setup logging
    setup_logging()
    logger = get_logger("Main")
    
    logger.info("Starting Plant Growth Analysis Application...")
    
    try:
        root = tk.Tk()
        app = PlantGrowthApp(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
