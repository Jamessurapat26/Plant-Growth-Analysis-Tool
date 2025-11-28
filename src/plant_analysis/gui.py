import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font as tkfont
from PIL import Image, ImageTk

from .analyzer import PlantAnalyzer
from .config import WINDOW_TITLE, WINDOW_SIZE, PREVIEW_SIZE
from .utils import get_logger

logger = get_logger("PlantAnalysis.GUI")

class PlantGrowthApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        
        # Make window responsive - wider for 2-column layout
        self.root.geometry("1400x750")
        self.root.minsize(1200, 650)
        
        # Center window on screen
        self._center_window()
        
        # Modern Apple-style color scheme
        self.colors = {
            'bg_primary': '#FFFFFF',      # Pure white background
            'bg_secondary': '#F5F5F7',    # Light gray (Apple style)
            'bg_card': '#FAFAFA',         # Card background
            'accent': '#007AFF',          # Apple blue
            'accent_hover': '#0051D5',    # Darker blue
            'success': '#34C759',         # Apple green
            'success_hover': '#248A3D',   # Darker green
            'danger': '#FF3B30',          # Apple red
            'danger_hover': '#C8190E',    # Darker red
            'text_primary': '#1D1D1F',    # Near black
            'text_secondary': '#86868B',  # Gray
            'border': '#D2D2D7',          # Light border
            'shadow': '#00000015'         # Subtle shadow
        }
        
        # Set background
        self.root.configure(bg=self.colors['bg_secondary'])

        # Initialize analyzer
        self.analyzer = PlantAnalyzer()

        self.img1_path = None
        self.img2_path = None
        self.preview_size = (280, 280)
        self.last_result = None

        # Bind resize event
        self.root.bind('<Configure>', self._on_window_resize)

        self._setup_ui()
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _on_window_resize(self, event):
        """Handle window resize events"""
        # Only handle resize for the root window
        if event.widget == self.root:
            # Update preview sizes based on window size
            new_width = self.root.winfo_width()
            if new_width < 1000:
                self.preview_size = (200, 200)
            elif new_width < 1200:
                self.preview_size = (240, 240)
            else:
                self.preview_size = (280, 280)

    def _setup_ui(self):
        # Main container with responsive padding
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_secondary'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Header section with modern design
        header_frame = tk.Frame(self.main_container, bg=self.colors['bg_secondary'])
        header_frame.pack(pady=(0, 15))
        
        # Title with SF Pro style
        available_fonts = tkfont.families()
        title_font = ("SF Pro Display", 36, "bold") if "SF Pro Display" in available_fonts else ("Segoe UI", 36, "bold")
        
        title_label = tk.Label(
            header_frame, 
            text="Plant Growth Analysis", 
            font=title_font,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        )
        title_label.pack()
        
        # Subtitle with lighter weight
        subtitle_label = tk.Label(
            header_frame,
            text="AI-Powered Plant Monitoring & Growth Tracking",
            font=("Segoe UI", 13),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        subtitle_label.pack(pady=(5, 0))

        # Content card with rounded appearance simulation
        self.content_card = tk.Frame(
            self.main_container, 
            bg=self.colors['bg_primary'],
            relief=tk.FLAT,
            bd=0
        )
        self.content_card.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Add padding inside card (responsive)
        self.card_inner = tk.Frame(self.content_card, bg=self.colors['bg_primary'])
        self.card_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Configure 2-column grid layout
        self.card_inner.grid_columnconfigure(0, weight=1, minsize=400)  # Left: Images
        self.card_inner.grid_columnconfigure(1, weight=1, minsize=400)  # Right: Results
        self.card_inner.grid_rowconfigure(0, weight=1)

        # LEFT COLUMN: Images and Controls
        left_frame = tk.Frame(self.card_inner, bg=self.colors['bg_primary'])
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Images Container
        images_frame = tk.Frame(left_frame, bg=self.colors['bg_primary'])
        images_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Configure responsive columns for images
        images_frame.grid_columnconfigure(0, weight=1, minsize=250)
        images_frame.grid_columnconfigure(1, weight=1, minsize=250)

        # Image 1 Section
        self.frame1, self.lbl1_preview, self.lbl1_path = self._create_image_section(
            images_frame, "Before", self.select_image1, column=0
        )

        # Image 2 Section
        self.frame2, self.lbl2_preview, self.lbl2_path = self._create_image_section(
            images_frame, "After", self.select_image2, column=1
        )

        # Button Frame with Apple-style spacing
        button_frame = tk.Frame(left_frame, bg=self.colors['bg_primary'])
        button_frame.pack(pady=15)
        
        # Compare Button - Apple style (flat with rounded simulation)
        self.compare_btn = tk.Button(
            button_frame,
            text="Analyze Growth",
            command=self.compare_images,
            bg=self.colors['accent'],
            fg="white",
            font=("Segoe UI", 13, "bold"),
            padx=35,
            pady=12,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=self.colors['accent_hover']
        )
        self.compare_btn.pack(side=tk.LEFT, padx=6)
        
        # Clear Button - Apple style secondary
        self.clear_btn = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_all,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=("Segoe UI", 13),
            padx=35,
            pady=12,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=self.colors['border']
        )
        self.clear_btn.pack(side=tk.LEFT, padx=6)
        
        # Bind hover effects - subtle Apple style
        self.compare_btn.bind("<Enter>", lambda e: self.compare_btn.config(bg=self.colors['accent_hover']))
        self.compare_btn.bind("<Leave>", lambda e: self.compare_btn.config(bg=self.colors['accent']))
        self.clear_btn.bind("<Enter>", lambda e: self.clear_btn.config(bg=self.colors['border']))
        self.clear_btn.bind("<Leave>", lambda e: self.clear_btn.config(bg=self.colors['bg_secondary']))

        # RIGHT COLUMN: Results Section
        right_frame = tk.Frame(self.card_inner, bg=self.colors['bg_primary'])
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        
        # Results Section - Apple card style with proper scrolling
        result_container = tk.Frame(right_frame, bg=self.colors['bg_primary'])
        result_container.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        result_header = tk.Frame(result_container, bg=self.colors['bg_primary'])
        result_header.pack(fill=tk.X, pady=(0, 12))
        
        result_title = tk.Label(
            result_header,
            text="Results",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        result_title.pack(side=tk.LEFT)
        
        # Export button - minimal Apple style
        self.export_btn = tk.Button(
            result_header,
            text="Export",
            command=self.export_results,
            bg=self.colors['accent'],
            fg="white",
            font=("Segoe UI", 10),
            padx=16,
            pady=6,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            state=tk.DISABLED,
            activebackground=self.colors['accent_hover']
        )
        self.export_btn.pack(side=tk.RIGHT)
        
        # Frame with subtle border for results - scrollable area
        self.result_frame = tk.Frame(
            result_container, 
            relief=tk.FLAT,
            bd=0,
            bg=self.colors['bg_card'],
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.result_frame.pack(fill=tk.BOTH, expand=True)
        self.result_frame.pack_propagate(True)  # Allow content to expand
        
        # Determine available fonts
        available_fonts = tkfont.families()
        mono_font = ("Consolas", 10) if "Consolas" in available_fonts else ("Courier New", 10)
        
        # Create Text widget with proper scrolling and visibility
        self.result_text = tk.Text(
            self.result_frame,
            font=("Segoe UI", 10),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            wrap=tk.WORD,
            padx=25,
            pady=20,
            relief=tk.FLAT,
            borderwidth=0,
            selectbackground=self.colors['accent'],
            selectforeground="white",
            insertbackground=self.colors['text_primary'],
            state=tk.NORMAL,
            spacing1=2,
            spacing2=1,
            spacing3=2
        )
        
        # Create vertical scrollbar with better styling
        scrollbar = tk.Scrollbar(
            self.result_frame,
            orient=tk.VERTICAL,
            command=self.result_text.yview,
            width=14,
            relief=tk.FLAT
        )
        
        # Configure text widget to use scrollbar
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets properly
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Enable mousewheel scrolling with better handling
        def on_mousewheel(event):
            try:
                self.result_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass
            return "break"
        
        # Bind to multiple widgets for better coverage
        self.result_text.bind("<MouseWheel>", on_mousewheel)
        self.result_frame.bind("<MouseWheel>", on_mousewheel)
        result_container.bind("<MouseWheel>", on_mousewheel)
        
        # Configure text tags with Apple typography and colors
        value_font = ("Consolas", 10, "bold") if "Consolas" in available_fonts else ("Courier New", 10, "bold")
        
        # Main headers
        self.result_text.tag_configure("title", font=("Segoe UI", 20, "bold"), foreground=self.colors['text_primary'], spacing1=5, spacing3=5)
        self.result_text.tag_configure("header", font=("Segoe UI", 14, "bold"), foreground=self.colors['text_primary'], spacing1=10, spacing3=5)
        self.result_text.tag_configure("subheader", font=("Segoe UI", 12, "bold"), foreground=self.colors['text_secondary'], spacing1=5, spacing3=3)
        
        # Values and data
        self.result_text.tag_configure("value", font=("Segoe UI", 11, "bold"), foreground=self.colors['accent'])
        self.result_text.tag_configure("number", font=("Segoe UI", 13, "bold"), foreground=self.colors['accent'])
        self.result_text.tag_configure("label", font=("Segoe UI", 10), foreground=self.colors['text_secondary'])
        
        # Status indicators
        self.result_text.tag_configure("success", font=("Segoe UI", 11, "bold"), foreground=self.colors['success'])
        self.result_text.tag_configure("warning", font=("Segoe UI", 11, "bold"), foreground=self.colors['danger'])
        self.result_text.tag_configure("neutral", font=("Segoe UI", 11, "bold"), foreground=self.colors['text_secondary'])
        
        # Content styles
        self.result_text.tag_configure("body", font=("Segoe UI", 10), foreground=self.colors['text_primary'], spacing1=2)
        self.result_text.tag_configure("emphasis", font=("Segoe UI", 10, "bold"), foreground=self.colors['text_primary'])
        self.result_text.tag_configure("quote", font=("Segoe UI", 10, "italic"), foreground=self.colors['text_secondary'])
        
        # Separators
        self.result_text.tag_configure("separator", foreground=self.colors['border'])
        self.result_text.tag_configure("timestamp", font=("Segoe UI", 9), foreground=self.colors['text_secondary'])
        
        # Initial message - Apple minimalist style with enhanced formatting
        welcome_msg = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           🌱  Plant Growth Analysis Tool  🌱                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Welcome! This tool helps you analyze and measure plant growth 
using advanced AI technology.


📋 Getting Started
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1️⃣  Select Before Image
     Choose the earlier photo of your plant

  2️⃣  Select After Image  
     Choose the recent photo of the same plant

  3️⃣  Click "Analyze Growth"
     Let AI process and compare the images

  4️⃣  Review Results
     View detailed growth measurements and insights


⚡ Powered by YOLOv8 AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Precise plant detection and measurement
  • Accurate area calculation in pixels
  • Growth percentage analysis
  • Professional reporting

Ready to begin? Select your images above! 🚀

"""
        self._update_result_text(welcome_msg)

    def _create_image_section(self, parent, btn_text, command, column):
        # Main frame with grid layout for responsiveness
        frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        frame.grid(row=0, column=column, padx=10, pady=5, sticky='nsew')

        # Section label - Apple style
        label = tk.Label(
            frame,
            text=btn_text,
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary']
        )
        label.pack(pady=(0, 12), anchor=tk.W)

        # Preview container - clean Apple card style (responsive)
        preview_container = tk.Frame(
            frame, 
            relief=tk.FLAT,
            bd=0,
            bg=self.colors['bg_secondary'],
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        preview_container.pack(pady=(0, 12), fill=tk.BOTH, expand=True)
        
        # Preview Label (responsive size)
        preview_lbl = tk.Label(
            preview_container,
            text="No image",
            relief=tk.FLAT,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            font=("Segoe UI", 10)
        )
        preview_lbl.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Select button - Apple style secondary button
        btn = tk.Button(
            frame, 
            text=f"Choose {btn_text} Image", 
            command=command,
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent'],
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=self.colors['border']
        )
        btn.pack()
        
        # Hover effects
        btn.bind("<Enter>", lambda e: btn.config(bg=self.colors['border']))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.colors['bg_secondary']))

        # Path Label - minimal (responsive wrapping)
        path_lbl = tk.Label(
            frame, 
            text="", 
            fg=self.colors['text_secondary'], 
            bg=self.colors['bg_primary'],
            wraplength=250, 
            font=("Segoe UI", 9),
            height=2,
            justify=tk.CENTER
        )
        path_lbl.pack(pady=(8, 0), fill=tk.X)

        return frame, preview_lbl, path_lbl

    def select_image1(self):
        path = self._select_image()
        if path:
            self.img1_path = path
            filename = os.path.basename(path)
            # Truncate long filenames
            if len(filename) > 35:
                filename = filename[:32] + "..."
            self.lbl1_path.config(text=filename, fg=self.colors['text_primary'])
            self._update_preview(path, self.lbl1_preview)
            logger.info(f"Selected Before Image: {path}")

    def select_image2(self):
        path = self._select_image()
        if path:
            self.img2_path = path
            filename = os.path.basename(path)
            # Truncate long filenames
            if len(filename) > 35:
                filename = filename[:32] + "..."
            self.lbl2_path.config(text=filename, fg=self.colors['text_primary'])
            self._update_preview(path, self.lbl2_preview)
            logger.info(f"Selected After Image: {path}")

    def _select_image(self):
        return filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )

    def _update_preview(self, image_path, label_widget):
        """Update image preview with responsive sizing"""
        try:
            img = Image.open(image_path)
            
            # Get current preview size based on window size
            img_copy = img.copy()
            img_copy.thumbnail(self.preview_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_copy)

            label_widget.config(
                image=photo, 
                text="", 
                bg=self.colors['bg_secondary']
            )
            label_widget.image = photo  # Keep reference
            label_widget.original_image = img  # Store original for resize
            label_widget.image_path = image_path  # Store path
            
        except Exception as e:
            logger.error(f"Error loading preview: {e}")
            label_widget.config(
                text="Unable to load image",
                fg=self.colors['danger'],
                bg=self.colors['bg_secondary'],
                image=""
            )
            label_widget.image = None
    
    def _refresh_previews(self):
        """Refresh preview images after window resize"""
        if self.img1_path and hasattr(self.lbl1_preview, 'image_path'):
            self._update_preview(self.img1_path, self.lbl1_preview)
        
        if self.img2_path and hasattr(self.lbl2_preview, 'image_path'):
            self._update_preview(self.img2_path, self.lbl2_preview)

    def _update_result_text(self, text, use_tags=False):
        """Helper method to update the result text widget with better visibility"""
        try:
            # Enable editing
            self.result_text.config(state=tk.NORMAL)
            
            # Clear existing content
            self.result_text.delete("1.0", tk.END)
            
            # Insert new text
            if use_tags and isinstance(text, list):
                # Insert with tags
                for item in text:
                    if isinstance(item, tuple):
                        content, tag = item
                        self.result_text.insert(tk.END, content, tag)
                    else:
                        self.result_text.insert(tk.END, item)
            else:
                self.result_text.insert("1.0", text)
            
            # Scroll to top
            self.result_text.see("1.0")
            
            # Mark the text as read-only but still scrollable
            self.result_text.config(state=tk.NORMAL)
            
            # Force UI updates
            self.result_text.update_idletasks()
            self.result_frame.update_idletasks()
            self.root.update_idletasks()
            
            logger.info(f"Result text updated: {len(str(text))} characters")
        except Exception as e:
            logger.error(f"Error updating result text: {e}")
    
    def clear_all(self):
        """Clear all selections and results"""
        self.img1_path = None
        self.img2_path = None
        
        # Reset previews
        self.lbl1_preview.config(
            image="",
            text="No image",
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        self.lbl1_preview.image = None
        self.lbl1_path.config(text="", fg=self.colors['text_secondary'])
        
        self.lbl2_preview.config(
            image="",
            text="No image",
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        self.lbl2_preview.image = None
        self.lbl2_path.config(text="", fg=self.colors['text_secondary'])
        
        # Reset results
        self._update_result_text("Welcome to Plant Growth Analysis\n\n"
                                "Get started:\n\n"
                                "1. Select your before and after images\n"
                                "2. Click Analyze Growth to process\n"
                                "3. View detailed results and insights\n\n"
                                "Powered by YOLOv8 AI technology for precise plant detection\n"
                                "and accurate growth measurement.")
        
        self.export_btn.config(state=tk.DISABLED)
        self.last_result = None
        logger.info("Cleared all selections and results")
    
    def export_results(self):
        """Export results to a text file"""
        if not hasattr(self, 'last_result') or self.last_result is None:
            messagebox.showwarning("No Results", "No results to export. Please run analysis first.")
            return
        
        from datetime import datetime
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"plant_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.last_result)
                messagebox.showinfo("Success", f"Results exported successfully to:\n{filename}")
                logger.info(f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")
                logger.error(f"Export error: {e}")

    def compare_images(self):
        if not self.img1_path or not self.img2_path:
            messagebox.showwarning("Missing Images", "⚠️ Please select both images first.")
            return

        try:
            # Disable buttons during processing
            self.compare_btn.config(state=tk.DISABLED, text="⏳ Processing...")
            self.clear_btn.config(state=tk.DISABLED)
            self.export_btn.config(state=tk.DISABLED)
            self.root.update_idletasks()
            
            logger.info("Starting comparison via GUI")
            self._update_result_text("Analyzing Images\n\n"
                                    "Processing your images with AI...\n\n"
                                    "This may take a few moments.")
            self.root.update_idletasks()
            
            results = self.analyzer.compare_images(self.img1_path, self.img2_path)

            # Extract results
            img1_data = results["image1"]
            img2_data = results["image2"]
            growth_data = results["growth"]

            # Format the results - Modern Apple style with tags
            from datetime import datetime
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            
            result_parts = [
                ("🌱 Plant Growth Analysis\n\n", "title"),
                (f"{timestamp}\n", "timestamp"),
                ("\n" + "━" * 65 + "\n\n", "separator"),
                
                # Before Section
                ("📸 BEFORE IMAGE\n", "header"),
                (f"{os.path.basename(self.img1_path)}\n", "label"),
                ("Plant Coverage: ", "body"),
                (f"{img1_data['plant_percentage']:.2f}%", "number"),
                ("\n\n", ""),
                
                # After Section
                ("📸 AFTER IMAGE\n", "header"),
                (f"{os.path.basename(self.img2_path)}\n", "label"),
                ("Plant Coverage: ", "body"),
                (f"{img2_data['plant_percentage']:.2f}%", "number"),
                ("\n\n", ""),
                
                # Divider
                ("━" * 65 + "\n\n", "separator"),
                
                # Growth Metrics
                ("📊 GROWTH METRICS\n\n", "header"),
                ("Absolute Change\n", "label"),
                (f"      {growth_data['absolute']:+.2f}%", "number"),
                ("\n\n", ""),
                ("Relative Change\n", "label"),
                (f"      {growth_data['relative']:+.1f}%", "number"),
                ("\n\n", ""),
                ("Growth Rate\n", "label"),
                (f"      {abs(growth_data['relative']):.1f}%", "number"),
                ("\n\n", "")
            ]
            
            # Add interpretation with color coding
            result_parts.extend([
                ("━" * 65 + "\n\n", "separator"),
                ("📋 SUMMARY\n\n", "header")
            ])
            
            if growth_data['absolute'] > 0:
                result_parts.extend([
                    ("Growth Status: ", "body"),
                    ("✓ Positive Growth\n\n", "success"),
                    (f"Your plant has grown by ", "body"),
                    (f"{abs(growth_data['absolute']):.2f}%", "success"),
                    (f" from {img1_data['plant_percentage']:.2f}% to {img2_data['plant_percentage']:.2f}% coverage.\n\n", "body")
                ])
                
                if growth_data['relative'] > 100:
                    assessment = "🌟 Exceptional growth detected. The plant has more than doubled in size."
                elif growth_data['relative'] > 50:
                    assessment = "🌟 Significant growth with strong development."
                elif growth_data['relative'] > 20:
                    assessment = "✓ Good growth showing healthy development."
                else:
                    assessment = "✓ Moderate but steady growth progress."
                
                result_parts.extend([
                    ("Assessment:\n", "subheader"),
                    (assessment, "body")
                ])
                    
            elif growth_data['absolute'] < 0:
                result_parts.extend([
                    ("Growth Status: ", "body"),
                    ("⚠ Negative Change\n\n", "warning"),
                    (f"Plant coverage decreased by ", "body"),
                    (f"{abs(growth_data['absolute']):.2f}%", "warning"),
                    (f" from {img1_data['plant_percentage']:.2f}% to {img2_data['plant_percentage']:.2f}%.\n\n", "body"),
                    ("Possible causes:\n", "subheader"),
                    ("  • Leaf loss or withering\n", "body"),
                    ("  • Different imaging conditions\n", "body"),
                    ("  • Recent pruning\n", "body"),
                    ("  • Environmental stress factors", "body")
                ])
            else:
                result_parts.extend([
                    ("Growth Status: ", "body"),
                    ("○ Stable\n\n", "neutral"),
                    ("No significant change in plant coverage detected.\n", "body"),
                    ("This indicates stable conditions with minimal growth.", "body")
                ])
            
            result_parts.extend([
                ("\n\n" + "━" * 65 + "\n", "separator"),
                ("\n⚡ Analysis powered by YOLOv8 AI model", "quote")
            ])

            # Store result for export (plain text)
            plain_text = "".join([item[0] if isinstance(item, tuple) else item for item in result_parts])
            self.last_result = plain_text
            
            # Update display with formatted tags
            self._update_result_text(result_parts, use_tags=True)
            
            # Re-enable buttons
            self.compare_btn.config(state=tk.NORMAL, text="Analyze Growth")
            self.clear_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)
            
            # Force UI update to show results
            self.result_text.see("1.0")
            self.result_frame.update()
            self.root.update_idletasks()
            
            # Show success message - minimal
            messagebox.showinfo("Analysis Complete", 
                              f"Growth: {growth_data['absolute']:+.2f}%\n"
                              f"Before: {img1_data['plant_percentage']:.2f}%\n"
                              f"After: {img2_data['plant_percentage']:.2f}%")
            
            logger.info("Analysis completed successfully")

        except Exception as e:
            logger.error(f"GUI Error: {e}", exc_info=True)
            self.compare_btn.config(state=tk.NORMAL, text="Analyze Growth")
            self.clear_btn.config(state=tk.NORMAL)
            
            error_text = "Analysis Error\n\n"
            error_text += f"{str(e)}\n\n"
            error_text += "━" * 65 + "\n\n"
            error_text += "Please verify:\n\n"
            error_text += "• Images are valid (JPG, PNG, BMP)\n"
            error_text += "• Images contain visible plants\n"
            error_text += "• Model file exists at Model/weights.pt\n"
            error_text += "• Sufficient disk space available\n"
            error_text += "• All dependencies are installed\n\n"
            error_text += "Check console for detailed logs."
            
            self._update_result_text(error_text)
            messagebox.showerror("Error", f"Analysis failed:\n\n{str(e)}")
