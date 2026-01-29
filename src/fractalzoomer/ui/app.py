import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageOps
import numpy as np

from fractalzoomer.core import (
    MandelbrotSet,
    JuliaSet,
    BurningShipSet,
    DEFAULT_JULIA_C_REAL,
    DEFAULT_JULIA_C_IMAG,
)
from fractalzoomer.ui.coordinates import Viewport
from fractalzoomer.utils.exporter import FractalExporter

# Constants
W, H = 600, 400
MAX_ITER = 128

# Julia presets: name -> (c_real, c_imag)
JULIA_PRESETS = {
    "Dendrite": (-0.4, 0.6),
    "Dragon": (-0.8, 0.156),
    "Spiral": (-0.7269, 0.1889),
    "Galaxy": (0.285, 0.01),
    "Snowflake": (-0.75, 0.11),
    "Lightning": (-0.5251993, -0.5251993),
    "Starfish": (-0.5, 0.563),
    "Custom": None,  # Indicates manual slider values
}


class FractalZoomerUI:
    # Main application class for the Fractal Zoomer UI.

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

        # Julia parameters
        self.julia_c_real = DEFAULT_JULIA_C_REAL
        self.julia_c_imag = DEFAULT_JULIA_C_IMAG

        # Create fractal objects
        self.mandelbrot = MandelbrotSet(max_iter=self.max_iter)
        self.julia = JuliaSet(
            c_real=self.julia_c_real,
            c_imag=self.julia_c_imag,
            max_iter=self.max_iter
        )
        self.burning_ship = BurningShipSet(max_iter=self.max_iter)
        self.viewport = Viewport(W, H)
        self.exporter = FractalExporter()
        self.current_img_array = None  # Store current fractal data for export

        # Panning state
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
        self.canvas.bind("<Button-2>", self.zoom_out)
        self.canvas.bind("<Option-Button-1>", self.zoom_out)

        # Canvas Panning
        # Existing middle mouse pan (keep these)
        self.canvas.bind("<Control-Button-1>", self.start_pan)
        self.canvas.bind("<Control-B1-Motion>", self.pan_move)
        self.canvas.bind("<Control-ButtonRelease-1>", self.end_pan)
        
        

        # Control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Iteration slider
        tk.Label(control_frame, text="Max Iterations:").grid(row=0, column=0, padx=5, sticky='e')
        self.iter_slider = tk.Scale(
            control_frame, from_=50, to=500, orient=tk.HORIZONTAL,
            length=300, command=self.update_iterations
        )
        self.iter_slider.set(self.max_iter)
        self.iter_slider.grid(row=0, column=1, padx=5)

        # Fractal type selection
        tk.Label(control_frame, text="Fractal Type:").grid(row=1, column=0, padx=5, sticky='e')
        self.fractal_var = tk.StringVar(value="mandelbrot")

        fractal_frame = tk.Frame(control_frame)
        fractal_frame.grid(row=1, column=1, padx=5, sticky='w')

        tk.Radiobutton(
            fractal_frame, text="Mandelbrot", variable=self.fractal_var,
            value="mandelbrot", command=self.change_fractal
        ).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(
            fractal_frame, text="Julia", variable=self.fractal_var,
            value="julia", command=self.change_fractal
        ).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(
            fractal_frame, text="Burning Ship", variable=self.fractal_var,
            value="burning_ship", command=self.change_fractal
        ).pack(side=tk.LEFT, padx=5)

        # === Julia Parameter Controls ===
        self.julia_frame = tk.LabelFrame(self.root, text="Julia Set Parameters", padx=10, pady=5)
        self.julia_frame.pack(pady=10, fill='x', padx=20)

        # Preset dropdown
        preset_frame = tk.Frame(self.julia_frame)
        preset_frame.pack(fill='x', pady=5)

        tk.Label(preset_frame, text="Preset:").pack(side=tk.LEFT, padx=5)
        self.preset_var = tk.StringVar(value="Dendrite")
        self.preset_dropdown = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=list(JULIA_PRESETS.keys()),
            state="readonly",
            width=15
        )
        self.preset_dropdown.pack(side=tk.LEFT, padx=5)
        self.preset_dropdown.bind("<<ComboboxSelected>>", self.on_preset_selected)

        # c_real slider
        c_real_frame = tk.Frame(self.julia_frame)
        c_real_frame.pack(fill='x', pady=2)

        tk.Label(c_real_frame, text="c (real):").pack(side=tk.LEFT, padx=5)
        self.c_real_var = tk.DoubleVar(value=self.julia_c_real)
        self.c_real_slider = tk.Scale(
            c_real_frame,
            from_=-2.0, to=2.0,
            resolution=0.001,
            orient=tk.HORIZONTAL,
            length=250,
            variable=self.c_real_var,
            command=self.on_julia_param_change
        )
        self.c_real_slider.pack(side=tk.LEFT, padx=5, fill='x', expand=True)

        # c_real entry for precise input
        self.c_real_entry = tk.Entry(c_real_frame, width=10)
        self.c_real_entry.pack(side=tk.LEFT, padx=5)
        self.c_real_entry.insert(0, str(self.julia_c_real))
        self.c_real_entry.bind("<Return>", self.on_c_real_entry)

        # c_imag slider
        c_imag_frame = tk.Frame(self.julia_frame)
        c_imag_frame.pack(fill='x', pady=2)

        tk.Label(c_imag_frame, text="c (imag):").pack(side=tk.LEFT, padx=5)
        self.c_imag_var = tk.DoubleVar(value=self.julia_c_imag)
        self.c_imag_slider = tk.Scale(
            c_imag_frame,
            from_=-2.0, to=2.0,
            resolution=0.001,
            orient=tk.HORIZONTAL,
            length=250,
            variable=self.c_imag_var,
            command=self.on_julia_param_change
        )
        self.c_imag_slider.pack(side=tk.LEFT, padx=5, fill='x', expand=True)

        # c_imag entry for precise input
        self.c_imag_entry = tk.Entry(c_imag_frame, width=10)
        self.c_imag_entry.pack(side=tk.LEFT, padx=5)
        self.c_imag_entry.insert(0, str(self.julia_c_imag))
        self.c_imag_entry.bind("<Return>", self.on_c_imag_entry)

        # Current c value display
        self.c_display_label = tk.Label(
            self.julia_frame,
            text=f"c = {self.julia_c_real:.4f} + {self.julia_c_imag:.4f}i",
            font=('Courier', 10)
        )
        self.c_display_label.pack(pady=5)

        # Initially hide Julia controls (shown when Julia fractal selected)
        self.julia_frame.pack_forget()

        # Info label
        self.info_label = tk.Label(self.root, text="", font=('Arial', 9))
        self.info_label.pack()
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        # Save Image button
        self.save_button = tk.Button(
            button_frame,
            text="💾 Save Image",
            command=self.export_image,
            font=('Arial', 10),
            padx=15,
            pady=5
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Reset View button
        self.reset_button = tk.Button(
            button_frame,
            text="🔄 Reset View",
            command=self.reset_view,
            font=('Arial', 10),
            padx=15,
            pady=5
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Instructions
        instructions = tk.Label(
            self.root,
            text="Left-click: zoom in • Right-click: zoom out • Middle-click or Ctrl+drag: pan",
            font=('Arial', 10, 'italic'), fg='gray'
        )
        instructions.pack(pady=5)

    def on_preset_selected(self, event=None):
        # Handle Julia preset selection change.
        preset_name = self.preset_var.get()
        preset_values = JULIA_PRESETS.get(preset_name)

        if preset_values is not None:
            c_real, c_imag = preset_values
            self.julia_c_real = c_real
            self.julia_c_imag = c_imag

            # Update sliders
            self.c_real_var.set(c_real)
            self.c_imag_var.set(c_imag)

            # Update entries
            self.c_real_entry.delete(0, tk.END)
            self.c_real_entry.insert(0, str(c_real))
            self.c_imag_entry.delete(0, tk.END)
            self.c_imag_entry.insert(0, str(c_imag))

            # Update Julia set and render
            self.julia.set_parameters(c_real=c_real, c_imag=c_imag)
            self.update_c_display()

            if self.fractal_type == "julia":
                self.render_fractal()

    def on_julia_param_change(self, value=None):
        # Handle slider changes for Julia parameters.
        new_c_real = self.c_real_var.get()
        new_c_imag = self.c_imag_var.get()

        # Check if values changed
        if (new_c_real != self.julia_c_real or new_c_imag != self.julia_c_imag):
            self.julia_c_real = new_c_real
            self.julia_c_imag = new_c_imag

            # Update entries to match sliders
            self.c_real_entry.delete(0, tk.END)
            self.c_real_entry.insert(0, f"{new_c_real:.4f}")
            self.c_imag_entry.delete(0, tk.END)
            self.c_imag_entry.insert(0, f"{new_c_imag:.4f}")

            # Set preset to "Custom" if it doesn't match any preset
            self._check_if_custom_preset()

            # Update Julia set
            self.julia.set_parameters(c_real=new_c_real, c_imag=new_c_imag)
            self.update_c_display()

            if self.fractal_type == "julia":
                self.render_fractal()

    def on_c_real_entry(self, event=None):
        # Handle Enter key in c_real entry field.
        try:
            value = float(self.c_real_entry.get())
            value = max(-2.0, min(2.0, value))  # Clamp to range
            self.c_real_var.set(value)
            self.on_julia_param_change()
        except ValueError:
            # Reset to current value if invalid
            self.c_real_entry.delete(0, tk.END)
            self.c_real_entry.insert(0, f"{self.julia_c_real:.4f}")

    def on_c_imag_entry(self, event=None):
        # Handle Enter key in c_imag entry field.
        try:
            value = float(self.c_imag_entry.get())
            value = max(-2.0, min(2.0, value))  # Clamp to range
            self.c_imag_var.set(value)
            self.on_julia_param_change()
        except ValueError:
            # Reset to current value if invalid
            self.c_imag_entry.delete(0, tk.END)
            self.c_imag_entry.insert(0, f"{self.julia_c_imag:.4f}")

    def _check_if_custom_preset(self):
        # Check if current values match any preset, set to Custom if not.
        for name, values in JULIA_PRESETS.items():
            if values is not None:
                c_real, c_imag = values
                if (abs(self.julia_c_real - c_real) < 0.0001 and
                        abs(self.julia_c_imag - c_imag) < 0.0001):
                    self.preset_var.set(name)
                    return
        self.preset_var.set("Custom")

    def update_c_display(self):
        # Update the c value display label.
        sign = "+" if self.julia_c_imag >= 0 else "-"
        self.c_display_label.config(
            text=f"c = {self.julia_c_real:.4f} {sign} {abs(self.julia_c_imag):.4f}i"
        )

    def render_fractal(self):
        # Render the current fractal to the canvas.
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
        C = X + 1j * Y
        C = C.astype(np.complex64)

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
        self.current_img_array = img_array  # Store for potential export

        # Create and display image
        img = Image.fromarray(img_array, mode='L')
        img = ImageOps.colorize(img, black="black", mid = "purple", white="yellow")
        img = ImageOps.autocontrast(img, cutoff=1)
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Update info label
        zoom_level = 3.5 / (2 * self.half_width)
        self.info_label.config(
            text=f"Center: ({self.center_x:.6f}, {self.center_y:.6f}) | "
                 f"Zoom: {zoom_level:.2f}x | Iterations: {self.max_iter}"
        )

    def zoom_in(self, event):
        # Zoom in centered on click position.
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

    def zoom_out(self, event):
        # Zoom out centered on click position.
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

    def start_pan(self, event):
        # Start panning operation.
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.pan_start_center_x = self.center_x
        self.pan_start_center_y = self.center_y
        self.pan_start_half_width = self.half_width
        self.pan_start_half_height = self.half_height

    def pan_move(self, event):
        # Update view during panning.
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

    def end_pan(self, event):
        # End panning operation.
        self.is_panning = False

    def update_iterations(self, value):
        # Update max iterations for all fractals.
        self.max_iter = int(value)
        self.mandelbrot = MandelbrotSet(max_iter=self.max_iter)
        self.julia = JuliaSet(
            c_real=self.julia_c_real,
            c_imag=self.julia_c_imag,
            max_iter=self.max_iter
        )
        self.burning_ship = BurningShipSet(max_iter=self.max_iter)
        self.render_fractal()

    def change_fractal(self):
        # Handle fractal type selection change.
        self.fractal_type = self.fractal_var.get()

        # Show/hide Julia parameter controls
        if self.fractal_type == "julia":
            self.julia_frame.pack(pady=10, fill='x', padx=20, after=self.canvas.master.winfo_children()[1])
        else:
            self.julia_frame.pack_forget()

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

    def export_image(self):
        # Export the current fractal image with metadata.
        if self.current_img_array is None:
            messagebox.showwarning("Missing image", "No fractal image to export.")
            return

        filetypes = [
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg;*.jpeg"),
            ("BMP Image", "*.bmp"),
            ("All files", "*.*")
        ]

        default_name = f"{self.fractal_type}_fractal.png"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=filetypes,
            initialfile=default_name,
            title="Save Fractal Image"
        )

        if filepath:
            try:
                # Prepare metadata
                metadata = {
                    'fractal_type': self.fractal_type,
                    'center_x': str(self.center_x),
                    'center_y': str(self.center_y),
                    'zoom': str(3.5 / (2 * self.half_width)),
                    'max_iterations': str(self.max_iter)
                }
                if self.fractal_type == "julia":
                    metadata['julia_c_real'] = str(self.julia_c_real)
                    metadata['julia_c_imag'] = str(self.julia_c_imag)

                # Export using FractalExporter
                self.exporter.export_fractal(
                    self.current_img_array,
                    filepath,
                    metadata=metadata
                )

                messagebox.showinfo("Success", f"Image saved to:\n{filepath}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")

    def reset_view(self):
        # Reset view to default parameters.
        self.change_fractal()


def main():
    # Main entry point for the application.
    root = tk.Tk()
    app = FractalZoomerUI(root)  # noqa: F841
    root.mainloop()


if __name__ == "__main__":
    main()