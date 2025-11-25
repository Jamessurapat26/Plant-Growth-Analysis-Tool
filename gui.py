import os
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from plant_analysis import PlantAnalyzer


class PlantGrowthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plant Growth Comparison")
        self.root.geometry("800x600")

        # Initialize analyzer
        self.analyzer = PlantAnalyzer()

        self.img1_path = None
        self.img2_path = None
        self.preview_size = (250, 250)

        self._setup_ui()

    def _setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, text="Plant Growth Calculator", font=("Helvetica", 18, "bold")
        )
        title_label.pack(pady=15)

        # Images Container
        images_frame = tk.Frame(self.root)
        images_frame.pack(pady=10, fill=tk.X, padx=20)

        # Image 1 Section
        self.frame1 = self._create_image_section(
            images_frame, "Select Before Image", self.select_image1, side=tk.LEFT
        )
        self.lbl1_preview = self.frame1.nametowidget("preview_label")
        self.lbl1_path = self.frame1.nametowidget("path_label")

        # Image 2 Section
        self.frame2 = self._create_image_section(
            images_frame, "Select After Image", self.select_image2, side=tk.RIGHT
        )
        self.lbl2_preview = self.frame2.nametowidget("preview_label")
        self.lbl2_path = self.frame2.nametowidget("path_label")

        # Compare Button
        self.compare_btn = tk.Button(
            self.root,
            text="Compare Growth",
            command=self.compare_images,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 14, "bold"),
            padx=20,
            pady=10,
        )
        self.compare_btn.pack(pady=25)

        # Results Section
        self.result_frame = tk.Frame(self.root, relief=tk.GROOVE, borderwidth=2)
        self.result_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

        self.result_label = tk.Label(
            self.result_frame,
            text="Results will appear here",
            font=("Helvetica", 12),
            justify=tk.LEFT,
        )
        self.result_label.pack(pady=20)

    def _create_image_section(self, parent, btn_text, command, side):
        frame = tk.Frame(parent)
        frame.pack(side=side, expand=True, fill=tk.BOTH, padx=10)

        btn = tk.Button(frame, text=btn_text, command=command)
        btn.pack(pady=5)

        # Preview Label
        preview_lbl = tk.Label(
            frame,
            text="No Image",
            relief=tk.SUNKEN,
            width=30,
            height=15,
            name="preview_label",
        )
        preview_lbl.pack(pady=5)

        # Path Label
        path_lbl = tk.Label(
            frame, text="", fg="gray", wraplength=200, name="path_label"
        )
        path_lbl.pack(pady=5)

        return frame

    def select_image1(self):
        path = self._select_image()
        if path:
            self.img1_path = path
            self.lbl1_path.config(text=os.path.basename(path))
            self._update_preview(path, self.lbl1_preview)

    def select_image2(self):
        path = self._select_image()
        if path:
            self.img2_path = path
            self.lbl2_path.config(text=os.path.basename(path))
            self._update_preview(path, self.lbl2_preview)

    def _select_image(self):
        return filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )

    def _update_preview(self, image_path, label_widget):
        try:
            img = Image.open(image_path)
            img.thumbnail(self.preview_size)
            photo = ImageTk.PhotoImage(img)

            label_widget.config(image=photo, text="", width=0, height=0)
            label_widget.image = photo  # Keep reference
        except Exception as e:
            print(f"Error loading preview: {e}")
            label_widget.config(text="Error loading image")

    def compare_images(self):
        if not self.img1_path or not self.img2_path:
            messagebox.showwarning("Missing Images", "Please select both images first.")
            return

        try:
            results = self.analyzer.compare_images(self.img1_path, self.img2_path)

            # Extract results from new data structure
            img1_data = results["image1"]
            img2_data = results["image2"]
            growth_data = results["growth"]

            # Format the results with plant coverage only
            result_text = "BEFORE IMAGE:\n"
            result_text += f"  Plant Coverage: {img1_data['plant_percentage']:.2f}%\n\n"

            result_text += "AFTER IMAGE:\n"
            result_text += f"  Plant Coverage: {img2_data['plant_percentage']:.2f}%\n\n"

            result_text += "GROWTH:\n"
            result_text += f"  Plant Coverage: {growth_data['absolute']:+.2f}% ({growth_data['relative']:+.1f}% relative)"

            self.result_label.config(text=result_text, fg="#333")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlantGrowthApp(root)
    root.mainloop()
