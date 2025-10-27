import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from artifact.mandelbrot_core.mandelbrot import Mandelbrot
from artifact.mandelbrot_core.julia import Julia
from artifact.mandelbrot_core.burning_ship import BurningShip

class FractalZoomerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fractal Zoomer - Mandelbrot/Julia/Burning Ship")
        self.root.geometry("1000x650")
        
        self.width = 800
        self.height = 600
        self.xmin, self.xmax = -2.0, 1.0
        self.ymin, self.ymax = -1.5, 1.5
        self.max_iter = 100
        
        # Pan tracking
        self.pan_last_x = None
        self.pan_last_y = None
        
        # Zoom box selection tracking
        self.zoom_start_x = None
        self.zoom_start_y = None
        self.zoom_rect = None

        # Fractal cores
        self.mandelbrot = Mandelbrot(max_iter=self.max_iter)
        self.julia = Julia(c_re=-0.7, c_im=0.27015, max_iter=self.max_iter)
        self.burning_ship = BurningShip(max_iter=self.max_iter)
        self.current_fractal = self.mandelbrot
        self.fractal_name = "mandelbrot"

        # Main layout
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        # Canvas
        self.canvas = tk.Canvas(main_frame, width=self.width, height=self.height, 
                                bg="black", cursor="cross")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Control panel
        control_frame = tk.Frame(main_frame, width=200, bg="#f0f0f0")
        control_frame.pack(side="right", fill="y", padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        self.setup_controls(control_frame)
        
        # Mouse bindings
        self.setup_mouse_bindings()
        
        # Initial draw
        self.draw_fractal()

    def setup_controls(self, frame):
        # Title
        title = tk.Label(frame, text="Fractal Controls", font=("Arial", 14, "bold"), 
                         bg="#f0f0f0")
        title.pack(pady=10)
        
        # Fractal selector
        tk.Label(frame, text="Fractal Type:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        self.fractal_var = tk.StringVar(value="mandelbrot")
        
        fractals = [
            ("Mandelbrot", "mandelbrot"),
            ("Julia Set", "julia"),
            ("Burning Ship", "burning_ship")
        ]
        
        for text, value in fractals:
            rb = tk.Radiobutton(frame, text=text, variable=self.fractal_var, 
                                value=value, command=self.change_fractal,
                                bg="#f0f0f0", font=("Arial", 9))
            rb.pack(anchor="w", padx=20)
        
        # Separator
        tk.Frame(frame, height=2, bg="#cccccc").pack(fill="x", pady=10)
        
        # Julia parameters (visible only for Julia)
        self.julia_frame = tk.Frame(frame, bg="#f0f0f0")
        self.julia_frame.pack(fill="x", pady=5)
        
        tk.Label(self.julia_frame, text="Julia C (real):", bg="#f0f0f0", 
                 font=("Arial", 9)).pack(anchor="w", padx=10)
        self.julia_c_real = tk.Entry(self.julia_frame, width=15)
        self.julia_c_real.insert(0, "-0.7")
        self.julia_c_real.pack(padx=10, pady=2)
        
        tk.Label(self.julia_frame, text="Julia C (imag):", bg="#f0f0f0", 
                 font=("Arial", 9)).pack(anchor="w", padx=10)
        self.julia_c_imag = tk.Entry(self.julia_frame, width=15)
        self.julia_c_imag.insert(0, "0.27015")
        self.julia_c_imag.pack(padx=10, pady=2)
        
        tk.Button(self.julia_frame, text="Update Julia", 
                  command=self.update_julia_params).pack(pady=5)
        
        self.julia_frame.pack_forget()  # Hide initially
        
        # Separator
        tk.Frame(frame, height=2, bg="#cccccc").pack(fill="x", pady=10)
        
        # Max iterations
        tk.Label(frame, text="Max Iterations:", bg="#f0f0f0", 
                 font=("Arial", 10, "bold")).pack(pady=(5, 2))
        self.iter_label = tk.Label(frame, text=str(self.max_iter), bg="#f0f0f0")
        self.iter_label.pack()
        
        self.iter_slider = tk.Scale(frame, from_=50, to=500, orient=tk.HORIZONTAL,
                                     command=self.update_iterations, bg="#f0f0f0")
        self.iter_slider.set(self.max_iter)
        self.iter_slider.pack(fill="x", padx=10)
        
        # Separator
        tk.Frame(frame, height=2, bg="#cccccc").pack(fill="x", pady=10)
        
        # Zoom buttons
        tk.Label(frame, text="Zoom Controls:", bg="#f0f0f0", 
                 font=("Arial", 10, "bold")).pack(pady=(5, 5))
        
        zoom_in_btn = tk.Button(frame, text="Zoom In (2x)", command=self.zoom_in,
                                bg="#4CAF50", fg="white", font=("Arial", 9, "bold"))
        zoom_in_btn.pack(fill="x", padx=10, pady=5)
        
        zoom_out_btn = tk.Button(frame, text="Zoom Out (2x)", command=self.zoom_out,
                                 bg="#FF9800", fg="white", font=("Arial", 9, "bold"))
        zoom_out_btn.pack(fill="x", padx=10, pady=5)
        
        reset_btn = tk.Button(frame, text="Reset View", command=self.reset_view,
                              bg="#2196F3", fg="white", font=("Arial", 9, "bold"))
        reset_btn.pack(fill="x", padx=10, pady=5)
        
        # Separator
        tk.Frame(frame, height=2, bg="#cccccc").pack(fill="x", pady=10)
        
        # Coordinates display
        tk.Label(frame, text="Current View:", bg="#f0f0f0", 
                 font=("Arial", 10, "bold")).pack(pady=(5, 5))
        
        self.coord_text = tk.Text(frame, height=6, width=18, font=("Courier", 8),
                                  bg="white", relief="sunken")
        self.coord_text.pack(padx=10, pady=5)
        self.update_coord_display()
        
        # Help text
        tk.Frame(frame, height=2, bg="#cccccc").pack(fill="x", pady=10)
        help_text = tk.Label(frame, text="Left-click drag:\nZoom box\n\nRight-click drag:\nPan view",
                            bg="#f0f0f0", font=("Arial", 8), justify="left")
        help_text.pack(pady=10)

    def setup_mouse_bindings(self):
        # Pan with left-click (existing behavior)
        self.canvas.bind("<ButtonPress-1>", self.on_left_press)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        
        # Pan with right-click
        self.canvas.bind("<ButtonPress-3>", self.pan_start)
        self.canvas.bind("<B3-Motion>", self.pan_move)
        
        # Keyboard shortcuts
        self.root.bind("<r>", lambda e: self.reset_view())
        self.root.bind("<Return>", lambda e: self.draw_fractal())
        self.root.bind("<plus>", lambda e: self.zoom_in())
        self.root.bind("<minus>", lambda e: self.zoom_out())

    def on_left_press(self, event):
        """Start zoom box selection"""
        self.zoom_start_x = event.x
        self.zoom_start_y = event.y

    def on_left_drag(self, event):
        """Draw zoom box"""
        if self.zoom_rect:
            self.canvas.delete(self.zoom_rect)
        
        self.zoom_rect = self.canvas.create_rectangle(
            self.zoom_start_x, self.zoom_start_y, 
            event.x, event.y,
            outline="red", width=2, dash=(5, 5)
        )

    def on_left_release(self, event):
        """Apply zoom from box selection"""
        if self.zoom_rect:
            self.canvas.delete(self.zoom_rect)
            self.zoom_rect = None
        
        # Only zoom if significant drag
        if (abs(event.x - self.zoom_start_x) > 10 and 
            abs(event.y - self.zoom_start_y) > 10):
            
            # Convert pixel coordinates to complex plane
            x1 = self.xmin + (self.zoom_start_x / self.width) * (self.xmax - self.xmin)
            y1 = self.ymin + (self.zoom_start_y / self.height) * (self.ymax - self.ymin)
            x2 = self.xmin + (event.x / self.width) * (self.xmax - self.xmin)
            y2 = self.ymin + (event.y / self.height) * (self.ymax - self.ymin)
            
            self.xmin, self.xmax = min(x1, x2), max(x1, x2)
            self.ymin, self.ymax = min(y1, y2), max(y1, y2)
            
            self.draw_fractal()
            self.update_coord_display()

    def change_fractal(self):
        """Switch between fractal types"""
        self.fractal_name = self.fractal_var.get()
        
        if self.fractal_name == "mandelbrot":
            self.current_fractal = self.mandelbrot
            self.julia_frame.pack_forget()
        elif self.fractal_name == "julia":
            self.current_fractal = self.julia
            self.julia_frame.pack(fill="x", pady=5)
        elif self.fractal_name == "burning_ship":
            self.current_fractal = self.burning_ship
            self.julia_frame.pack_forget()
        
        self.reset_view()

    def update_julia_params(self):
        """Update Julia set parameters"""
        try:
            c_re = float(self.julia_c_real.get())
            c_im = float(self.julia_c_imag.get())
            self.julia = Julia(c_re=c_re, c_im=c_im, max_iter=self.max_iter)
            self.current_fractal = self.julia
            self.draw_fractal()
        except ValueError:
            pass  # Invalid input, ignore

    def update_iterations(self, value):
        """Update max iterations"""
        self.max_iter = int(value)
        self.iter_label.config(text=str(self.max_iter))
        
        # Update all fractal objects
        self.mandelbrot.max_iter = self.max_iter
        self.julia.max_iter = self.max_iter
        self.burning_ship.max_iter = self.max_iter
        
        self.draw_fractal()

    def reset_view(self):
        """Reset to default view for current fractal"""
        if self.fractal_name == "julia":
            self.xmin, self.xmax = -2.0, 2.0
            self.ymin, self.ymax = -2.0, 2.0
        elif self.fractal_name == "burning_ship":
            self.xmin, self.xmax = -1.8, -1.7
            self.ymin, self.ymax = -0.08, 0.02
        else:  # mandelbrot
            self.xmin, self.xmax = -2.0, 1.0
            self.ymin, self.ymax = -1.5, 1.5
        
        self.draw_fractal()
        self.update_coord_display()

    def update_coord_display(self):
        """Update coordinate display"""
        self.coord_text.delete(1.0, tk.END)
        self.coord_text.insert(1.0, 
            f"X min: {self.xmin:.6f}\n"
            f"X max: {self.xmax:.6f}\n\n"
            f"Y min: {self.ymin:.6f}\n"
            f"Y max: {self.ymax:.6f}"
        )

    def pan_start(self, event):
        """Start panning"""
        self.pan_last_x = event.x
        self.pan_last_y = event.y

    def pan_move(self, event):
        """Pan the view"""
        if self.pan_last_x is None or self.pan_last_y is None:
            return
        
        dx = event.x - self.pan_last_x
        dy = event.y - self.pan_last_y
        
        x_scale = (self.xmax - self.xmin) / self.width
        y_scale = (self.ymax - self.ymin) / self.height
        
        self.xmin -= dx * x_scale
        self.xmax -= dx * x_scale
        self.ymin -= dy * y_scale
        self.ymax -= dy * y_scale
        
        self.pan_last_x = event.x
        self.pan_last_y = event.y
        
        self.draw_fractal()
        self.update_coord_display()

    def draw_fractal(self):
        """Optimized fractal drawing using PIL for better performance"""
        # Create numpy array for faster pixel manipulation
        img_array = np.zeros((self.height, self.width), dtype=np.uint8)
        
        for x in range(self.width):
            for y in range(self.height):
                cx = self.xmin + (x / self.width) * (self.xmax - self.xmin)
                cy = self.ymin + (y / self.height) * (self.ymax - self.ymin)
                iters = self.current_fractal.iterations(cx, cy)
                shade = 255 - int(iters * 255 / self.max_iter)
                img_array[y, x] = shade
        
        # Convert to PIL Image for faster display
        pil_img = Image.fromarray(img_array, mode='L')
        # Apply color mapping (optional: convert to RGB with color scheme)
        pil_img = pil_img.convert('RGB')
        
        self.photo_img = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo_img)

    def animate_zoom(self, target_xmin, target_xmax, target_ymin, target_ymax, 
                     frames=15, delay=20):
        """Smooth zoom animation"""
        start_xmin, start_xmax = self.xmin, self.xmax
        start_ymin, start_ymax = self.ymin, self.ymax

        def step(frame):
            t = frame / frames
            self.xmin = start_xmin + t * (target_xmin - start_xmin)
            self.xmax = start_xmax + t * (target_xmax - start_xmax)
            self.ymin = start_ymin + t * (target_ymin - start_ymin)
            self.ymax = start_ymax + t * (target_ymax - start_ymax)
            self.draw_fractal()
            self.update_coord_display()
            if frame < frames:
                self.root.after(delay, step, frame + 1)
        step(0)

    def zoom_in(self):
        """Zoom in by 2x"""
        x_range = (self.xmax - self.xmin) * 0.5
        y_range = (self.ymax - self.ymin) * 0.5
        x_center = (self.xmax + self.xmin) / 2
        y_center = (self.ymax + self.ymin) / 2
        
        target_xmin = x_center - x_range / 2
        target_xmax = x_center + x_range / 2
        target_ymin = y_center - y_range / 2
        target_ymax = y_center + y_range / 2
        
        self.animate_zoom(target_xmin, target_xmax, target_ymin, target_ymax)

    def zoom_out(self):
        """Zoom out by 2x"""
        x_range = (self.xmax - self.xmin) * 2
        y_range = (self.ymax - self.ymin) * 2
        x_center = (self.xmax + self.xmin) / 2
        y_center = (self.ymax + self.ymin) / 2
        
        target_xmin = x_center - x_range / 2
        target_xmax = x_center + x_range / 2
        target_ymin = y_center - y_range / 2
        target_ymax = y_center + y_range / 2
        
        self.animate_zoom(target_xmin, target_xmax, target_ymin, target_ymax)


def main():
    root = tk.Tk()
    app = FractalZoomerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
