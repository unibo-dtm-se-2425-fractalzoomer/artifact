import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mandelbrot_core.mandelbrot import MandelbrotSet
from mandelbrot_core.julia import JuliaSet, JULIA_CR, JULIA_CI
from mandelbrot_core.burning_ship import BurningShipSet

# Constants
W, H = 600, 400
MAX_ITER = 128

class Viewport:
    def __init__(self, width, height):
        self.__size = np.array([width, height], dtype=float)
        self.__zoom = 1.0 / max(width, height)
        self.viewport_center = self.__size / 2

    def to_complex_plane(self, x, y, center_x, center_y, half_width, half_height) -> np.complex64:
        # Map to normalized viewport coordinates
        x_frac = x / self.__size[0]
        y_frac = y / self.__size[1]
        
        # Map to complex plane
        x_min = center_x - half_width
        y_max = center_y + half_height
        
        real = x_min + x_frac * (2 * half_width)
        imag = y_max - y_frac * (2 * half_height)
        
        return np.complex64(real + 1j * imag)
    
    def to_viewport_plane(self, z: np.complex64, center_x, center_y, half_width, half_height) -> np.ndarray:
        real = z.real
        imag = z.imag
        # Inverse mapping from complex plane to normalized coordinates
        x_frac = (real - center_x + half_width) / (2 * half_width)
        y_frac = (center_y + half_height - imag) / (2 * half_height)
        # Convert to screen pixel coordinates
        x = x_frac * self.__size[0]
        y = y_frac * self.__size[1]
        return np.array([x, y], dtype=float)


class FractalZoomerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fractal Zoomer")
        
        # View parameters
        self.center_x = -0.5
        self.center_y = 0.0
        self.half_width = 1.75
        self.half_height = 1.0
        
        # Current fractal type
        self.fractal_type = "mandelbrot"
        self.max_iter = MAX_ITER
        
        # Create fractal objects
        self.mandelbrot = MandelbrotSet(max_iter=self.max_iter)
        self.julia = JuliaSet(JULIA_CR, JULIA_CI, max_iter=self.max_iter)
        self.burning_ship = BurningShipSet(max_iter=self.max_iter)
        self.viewport = Viewport(W, H)
        
        #Panning 
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_start_center_x = 0
        self.pan_start_center_y = 0
        self.pan_start_half_width = 0
        self.pan_start_half_height = 0
        
        # Setup UI
        self.setup_ui()
        self.render_fractal()
    
    def setup_ui(self):
        # Canvas for fractal display
        self.canvas = tk.Canvas(self.root, width=W, height=H, bg='black')
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.zoom_in)
        self.canvas.bind("<Button-3>", self.zoom_out)
        
        # Control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Iteration slider
        tk.Label(control_frame, text="Max Iterations:").grid(row=0, column=0, padx=5, sticky='e')
        self.iter_slider = tk.Scale(control_frame, from_=50, to=500, orient=tk.HORIZONTAL, 
                                      length=300, command=self.update_iterations)
        self.iter_slider.set(self.max_iter)
        self.iter_slider.grid(row=0, column=1, padx=5)
        
        # Fractal type selection
        tk.Label(control_frame, text="Fractal Type:").grid(row=1, column=0, padx=5, sticky='e')
        self.fractal_var = tk.StringVar(value="mandelbrot")
        
        fractal_frame = tk.Frame(control_frame)
        fractal_frame.grid(row=1, column=1, padx=5, sticky='w')
        
        tk.Radiobutton(fractal_frame, text="Mandelbrot", variable=self.fractal_var, 
                       value="mandelbrot", command=self.change_fractal).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(fractal_frame, text="Julia", variable=self.fractal_var, 
                       value="julia", command=self.change_fractal).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(fractal_frame, text="Burning Ship", variable=self.fractal_var, 
                       value="burning_ship", command=self.change_fractal).pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = tk.Label(self.root, text="", font=('Arial', 9))
        self.info_label.pack()
        
        # Instructions
        instructions = tk.Label(self.root, 
                                text="Left-click to zoom in • Right-click to zoom out",
                                font=('Arial', 10, 'italic'), fg='gray')
        instructions.pack(pady=5)
    
    def render_fractal(self):
        # Calculate bounds
        x_min = self.center_x - self.half_width
        x_max = self.center_x + self.half_width
        y_min = self.center_y - self.half_height
        y_max = self.center_y + self.half_height
        
        # Create coordinate arrays
        x_coords = np.linspace(x_min, x_max, W)
        y_coords = np.linspace(y_max, y_min, H)
        
        # Create image array
        img_array = np.zeros((H, W), dtype=np.uint8)
        
        # Select fractal
        if self.fractal_type == "mandelbrot":
            fractal = self.mandelbrot
        elif self.fractal_type == "julia":
            fractal = self.julia
        else:
            fractal = self.burning_ship
        
        # Calculate fractal
        for i in range(H):
            for j in range(W):
                iterations = fractal.iterations(x_coords[j], y_coords[i])
                img_array[i, j] = int(255 * iterations / self.max_iter)
        
        # Create and display image
        img = Image.fromarray(img_array, mode='L')
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Update info label
        zoom_level = 3.5 / (2 * self.half_width)
        self.info_label.config(
            text=f"Center: ({self.center_x:.6f}, {self.center_y:.6f}) | "
                 f"Zoom: {zoom_level:.2f}x | Iterations: {self.max_iter}"
        )
    
    def zoom_in(self, event):
        click_x, click_y = screen_to_complex(
            event.x, event.y,
            self.center_x, self.center_y,
            self.half_width, self.half_height
        )
        
        zoom_factor = 0.9
        self.center_x = click_x
        self.center_y = click_y
        self.half_width *= zoom_factor
        self.half_height *= zoom_factor
        
        self.render_fractal()
    
    def zoom_out(self, event):
        click_x, click_y = screen_to_complex(
            event.x, event.y,
            self.center_x, self.center_y,
            self.half_width, self.half_height
        )
        
        zoom_factor = 1.0 / 0.9
        self.center_x = click_x
        self.center_y = click_y
        self.half_width *= zoom_factor
        self.half_height *= zoom_factor
        
        self.render_fractal()
    
    def update_iterations(self, value):
        self.max_iter = int(value)
        self.mandelbrot.max_iter = self.max_iter
        self.julia.max_iter = self.max_iter
        self.burning_ship.max_iter = self.max_iter
        self.render_fractal()
    
    def change_fractal(self):
        self.fractal_type = self.fractal_var.get()
        
        # Reset view to appropriate defaults
        if self.fractal_type == "mandelbrot":
            self.center_x = -0.5
            self.center_y = 0.0
        elif self.fractal_type == "julia":
            self.center_x = 0.0
            self.center_y = 0.0
        else:  # burning_ship
            self.center_x = -1.75
            self.center_y = -0.03
        
        self.half_width = 1.75
        self.half_height = 1.0
        self.render_fractal()


def main():
    root = tk.Tk()
    app = FractalZoomerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

