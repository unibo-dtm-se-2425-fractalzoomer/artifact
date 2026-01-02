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
        DEFAULT_JULIA_C_IMAG
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
        DEFAULT_JULIA_C_IMAG
    )

# Display constants
W, H = 600, 400
MAX_ITER = 128


def screen_to_complex(
    x: float,
    y: float,
    center_x: float,
    center_y: float,
    half_width: float,
    half_height: float,
    width: int = W,
    height: int = H
) -> tuple[float, float]:
    """
    Convert screen coordinates to complex plane coordinates.
    
    Args:
        x: Screen x coordinate (pixels from left).
        y: Screen y coordinate (pixels from top).
        center_x: Real part of the viewport center.
        center_y: Imaginary part of the viewport center.
        half_width: Half-width of the viewport in complex plane units.
        half_height: Half-height of the viewport in complex plane units.
        width: Screen width in pixels.
        height: Screen height in pixels.
        
    Returns:
        Tuple of (real, imaginary) coordinates in the complex plane.
    """
    x_frac = x / width
    y_frac = y / height
    
    x_min = center_x - half_width
    y_max = center_y + half_height
    
    real = x_min + x_frac * (2 * half_width)
    imag = y_max - y_frac * (2 * half_height)
    
    return real, imag


# Handles coordinate transformation between screen and complex plane.
class Viewport:
    
    def __init__(self, width: int, height: int):
        """
        Initialize the viewport.
        
        Args:
            width: Screen width in pixels.
            height: Screen height in pixels.
        """
        self._size = np.array([width, height], dtype=float)
        self._zoom = 1.0 / max(width, height)
        self.viewport_center = self._size / 2

    def to_complex_plane(
        self,
        x: float,
        y: float,
        center_x: float,
        center_y: float,
        half_width: float,
        half_height: float
    ) -> np.complex64:
        """
        Convert screen coordinates to a complex number.
        
        Args:
            x: Screen x coordinate.
            y: Screen y coordinate.
            center_x: Viewport center real part.
            center_y: Viewport center imaginary part.
            half_width: Half-width in complex units.
            half_height: Half-height in complex units.
            
        Returns:
            Complex number representing the point in the complex plane.
        """
        real, imag = screen_to_complex(
            x, y, center_x, center_y, half_width, half_height,
            int(self._size[0]), int(self._size[1])
        )
        return np.complex64(real + 1j * imag)

    def to_viewport_plane(
        self,
        z: np.complex64,
        center_x: float,
        center_y: float,
        half_width: float,
        half_height: float
    ) -> np.ndarray:
        """
        Convert a complex number to screen coordinates.
        
        Args:
            z: Complex number in the complex plane.
            center_x: Viewport center real part.
            center_y: Viewport center imaginary part.
            half_width: Half-width in complex units.
            half_height: Half-height in complex units.
            
        Returns:
            Array [x, y] of screen coordinates.
        """
        real = z.real
        imag = z.imag
        # Inverse mapping from complex plane to normalized coordinates
        x_frac = (real - center_x + half_width) / (2 * half_width)
        y_frac = (center_y + half_height - imag) / (2 * half_height)
        # Convert to screen pixel coordinates
        x = x_frac * self._size[0]
        y = y_frac * self._size[1]
        return np.array([x, y], dtype=float)


# Main application window
class FractalZoomerUI:
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the Fractal Zoomer UI.
        
        Args:
            root: The Tkinter root window.
        """
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
            c_real = DEFAULT_JULIA_C_REAL,
            c_imag = DEFAULT_JULIA_C_IMAG,
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
# Zoom in effect on left click
    def _zoom_in(self, event: tk.Event) -> None:
        click_complex = self.viewport.to_complex_plane(
            event.x, event.y,
            self.center_x, self.center_y,
            self.half_width, self.half_height
        )
        
        zoom_factor = 0.9
        self.center_x = click_complex.real
        self.center_y = click_complex.imag
        self.half_width *= zoom_factor
        self.half_height *= zoom_factor
    
        self.render_fractal()
# Zoom out on right click
    def _zoom_out(self, event: tk.Event) -> None:
        click_complex = self.viewport.to_complex_plane(
            event.x, event.y,
            self.center_x, self.center_y,
            self.half_width, self.half_height
        )
        
        zoom_factor = 1.0 / 0.9
        self.center_x = click_complex.real
        self.center_y = click_complex.imag
        self.half_width *= zoom_factor
        self.half_height *= zoom_factor
    
        self.render_fractal()
#Starts panning operations
    def _start_pan(self, event: tk.Event) -> None:
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.pan_start_center_x = self.center_x
        self.pan_start_center_y = self.center_y
        self.pan_start_half_width = self.half_width
        self.pan_start_half_height = self.half_height
# Update pan movements
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
        self.is_panning = False

    def _update_iterations(self, value: str) -> None:
        self.max_iter = int(value)
        self.mandelbrot.set_parameters(max_iter=self.max_iter)
        self.julia.set_parameters(max_iter=self.max_iter)
        self.burning_ship.set_parameters(max_iter=self.max_iter)
        self.render_fractal()
# Fractal displayed selection
    def _change_fractal(self) -> None:
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