import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import sys
import os

# Handle imports for both direct execution and module import
try:
    from fractalzoomer.core import (
        MandelbrotSet,
        JuliaSet,
        BurningShipSet,
        DEFAULT_JULIA_C_REAL,
        DEFAULT_JULIA_C_IMAG,
    )
    from fractalzoomer.ui.coordinates import (
        screen_to_complex,
        Viewport,
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
    )
except ModuleNotFoundError:
    # When running directly (python app.py), add src to path
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _src_dir = os.path.dirname(os.path.dirname(_current_dir))
    if _src_dir not in sys.path:
        sys.path.insert(0, _src_dir)
    
    from fractalzoomer.core import (
        MandelbrotSet,
        JuliaSet,
        BurningShipSet,
        DEFAULT_JULIA_C_REAL,
        DEFAULT_JULIA_C_IMAG,
    )
    from fractalzoomer.ui.coordinates import (
        screen_to_complex,
        Viewport,
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
    )

# Display constants
W, H = DEFAULT_WIDTH, DEFAULT_HEIGHT
MAX_ITER = 128


class FractalZoomerUI:
    #Application window for fractal viewing and interaction
    
    def __init__(self, root: tk.Tk):
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
        self.julia = JuliaSet(
            c_real=DEFAULT_JULIA_C_REAL,
            c_imag=DEFAULT_JULIA_C_IMAG,
            max_iter=self.max_iter
        )
        self.burning_ship = BurningShipSet(max_iter=self.max_iter)
        self.viewport = Viewport(W, H)
        
        # Panning state
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_start_center_x = 0.0
        self.pan_start_center_y = 0.0
        self.pan_start_half_width = 0.0
        self.pan_start_half_height = 0.0

        # Setup UI
        self._setup_ui()
        self.render_fractal()

    def _setup_ui(self) -> None:
        # Canvas for fractal display
        self.canvas = tk.Canvas(self.root, width=W, height=H, bg='black')
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._zoom_in)
        self.canvas.bind("<Button-3>", self._zoom_out)

        # Canvas panning
        self.canvas.bind("<Button-2>", self._start_pan)
        self.canvas.bind("<B2-Motion>", self._pan_move)
        self.canvas.bind("<ButtonRelease-2>", self._end_pan)
        
        # Control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Iteration slider
        tk.Label(control_frame, text="Max Iterations:").grid(
            row=0, column=0, padx=5, sticky='e'
        )
        self.iter_slider = tk.Scale(
            control_frame,
            from_=50,
            to=500,
            orient=tk.HORIZONTAL,
            length=300,
            command=self._update_iterations
        )
        self.iter_slider.set(self.max_iter)
        self.iter_slider.grid(row=0, column=1, padx=5)
        
        # Fractal type selection
        tk.Label(control_frame, text="Fractal Type:").grid(
            row=1, column=0, padx=5, sticky='e'
        )
        self.fractal_var = tk.StringVar(value="mandelbrot")
        
        fractal_frame = tk.Frame(control_frame)
        fractal_frame.grid(row=1, column=1, padx=5, sticky='w')
        
        tk.Radiobutton(
            fractal_frame,
            text="Mandelbrot",
            variable=self.fractal_var,
            value="mandelbrot",
            command=self._change_fractal
        ).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(
            fractal_frame,
            text="Julia",
            variable=self.fractal_var,
            value="julia",
            command=self._change_fractal
        ).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(
            fractal_frame,
            text="Burning Ship",
            variable=self.fractal_var,
            value="burning_ship",
            command=self._change_fractal
        ).pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = tk.Label(self.root, text="", font=('Arial', 9))
        self.info_label.pack()
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Left: zoom in • Right: zoom out • Middle: pan",
            font=('Arial', 10, 'italic'),
            fg='gray'
        )
        instructions.pack(pady=5)

    def render_fractal(self) -> None:
        # Render the current fractal view
        # Calculate bounds
        x_min = self.center_x - self.half_width
        x_max = self.center_x + self.half_width
        y_min = self.center_y - self.half_height
        y_max = self.center_y + self.half_height
    
        # Create coordinate arrays
        x_coords = np.linspace(x_min, x_max, W, dtype=np.float32)
        y_coords = np.linspace(y_max, y_min, H, dtype=np.float32)
    
        # Create meshgrid - vectorized coordinate creation
        X, Y = np.meshgrid(x_coords, y_coords)
        C = (X + 1j * Y).astype(np.complex64)
    
        # Select fractal and compute ALL points at once
        if self.fractal_type == "mandelbrot":
            Z_final = self.mandelbrot.compute_array(C)
        elif self.fractal_type == "julia":
            Z_final = self.julia.compute_array(C)
        else:
            Z_final = self.burning_ship.compute_array(C)
    
        # Convert to image - vectorized operations
        magnitude = np.abs(Z_final)
        img_array = np.clip(magnitude * 50, 0, 255).astype(np.uint8)

        # Create and display image
        img = Image.fromarray(img_array, mode='L')
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
    
        # Update info label
        zoom_level = 3.5 / (2 * self.half_width)
        self.info_label.config(
            text=f"Center: ({self.center_x:.6f}, {self.center_y:.6f}) | "
                 f"Zoom: {zoom_level:.2f}x | Iterations: {self.max_iter}"
        )

    def _zoom_in(self, event: tk.Event) -> None:
        """Handle zoom in on left click."""
        click_complex = self.viewport.to_complex_plane(
            event.x, event.y,
            self.center_x, self.center_y,
            self.half_width, self.half_height
        )
        
        zoom_factor = 0.9
        self.center_x = float(click_complex.real)
        self.center_y = float(click_complex.imag)
        self.half_width *= zoom_factor
        self.half_height *= zoom_factor
    
        self.render_fractal()

    def _zoom_out(self, event: tk.Event) -> None:
        click_complex = self.viewport.to_complex_plane(
            event.x, event.y,
            self.center_x, self.center_y,
            self.half_width, self.half_height
        )
        
        zoom_factor = 1.0 / 0.9
        self.center_x = float(click_complex.real)
        self.center_y = float(click_complex.imag)
        self.half_width *= zoom_factor
        self.half_height *= zoom_factor
    
        self.render_fractal()

    def _start_pan(self, event: tk.Event) -> None:
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.pan_start_center_x = self.center_x
        self.pan_start_center_y = self.center_y
        self.pan_start_half_width = self.half_width
        self.pan_start_half_height = self.half_height

    def _pan_move(self, event: tk.Event) -> None:
        if not self.is_panning:
            return
    
        # Calculate pixel displacement
        dx_pixels = event.x - self.pan_start_x
        dy_pixels = event.y - self.pan_start_y
    
        # Convert pixel displacement to complex plane displacement
        dx_complex = -dx_pixels * (2 * self.pan_start_half_width) / W
        dy_complex = dy_pixels * (2 * self.pan_start_half_height) / H
    
        # Update center
        self.center_x = self.pan_start_center_x + dx_complex
        self.center_y = self.pan_start_center_y + dy_complex
    
        # Keep zoom level locked
        self.half_width = self.pan_start_half_width
        self.half_height = self.pan_start_half_height
    
        self.render_fractal()

    def _end_pan(self, event: tk.Event) -> None:
        # End panning
        self.is_panning = False

    def _update_iterations(self, value: str) -> None:
        # Update iteration count from slider
        self.max_iter = int(value)
        self.mandelbrot.set_parameters(max_iter=self.max_iter)
        self.julia.set_parameters(max_iter=self.max_iter)
        self.burning_ship.set_parameters(max_iter=self.max_iter)
        self.render_fractal()

    def _change_fractal(self) -> None:
        # Change fractal type based on selection
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


def main() -> None:
    root = tk.Tk()
    app = FractalZoomerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()