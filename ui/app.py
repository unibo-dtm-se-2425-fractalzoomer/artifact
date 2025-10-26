import tkinter as tk

class FractalZoomerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fractal Zoomer")
        self.root.geometry("800x600")
        self.width = 800
        self.height = 550
        # Initial Mandelbrot parameters
        self.xmin, self.xmax = -2.0, 1.0
        self.ymin, self.ymax = -1.5, 1.5
        self.max_iter = 50
        self.pan_last_x = None
        self.pan_last_y = None

        # Canvas for drawing
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Bind mouse events for panning
        self.canvas.bind("<ButtonPress-1>", self.pan_start)
        self.canvas.bind("<B1-Motion>", self.pan_move)

        # Button panel for zoom controls
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x")
        zoom_in_btn = tk.Button(button_frame, text="Zoom In", command=self.zoom_in)
        zoom_in_btn.pack(side="left", padx=10, pady=10)
        zoom_out_btn = tk.Button(button_frame, text="Zoom Out", command=self.zoom_out)
        zoom_out_btn.pack(side="left", padx=10, pady=10)

        # Draw the initial fractal
        self.draw_mandelbrot()

    def pan_start(self, event):
        self.pan_last_x = event.x
        self.pan_last_y = event.y

    def pan_move(self, event):
        if self.pan_last_x is None or self.pan_last_y is None:
            return

        dx = event.x - self.pan_last_x
        dy = event.y - self.pan_last_y

        x_scale = (self.xmax - self.xmin) / self.width
        y_scale = (self.ymax - self.ymin) / self.height

        # Invert direction for intuitive panning
        self.xmin -= dx * x_scale
        self.xmax -= dx * x_scale
        self.ymin -= dy * y_scale
        self.ymax -= dy * y_scale

        self.pan_last_x = event.x
        self.pan_last_y = event.y

        self.draw_mandelbrot()

    def draw_mandelbrot(self):
        img = tk.PhotoImage(width=self.width, height=self.height)
        for x in range(self.width):
            for y in range(self.height):
                cx = self.xmin + (x / self.width) * (self.xmax - self.xmin)
                cy = self.ymin + (y / self.height) * (self.ymax - self.ymin)
                c = complex(cx, cy)
                z = 0
                n = 0
                while abs(z) <= 2 and n < self.max_iter:
                    z = z * z + c
                    n += 1
                shade = 255 - int(n * 255 / self.max_iter)
                color = f'#{shade:02x}{shade:02x}{shade:02x}'
                img.put(color, (x, y))
        self.canvas.create_image((0, 0), anchor="nw", image=img)
        self.canvas.image = img  # prevent garbage collection

    def animate_zoom(self, target_xmin, target_xmax, target_ymin, target_ymax, frames=20, delay=20):
        start_xmin, start_xmax = self.xmin, self.xmax
        start_ymin, start_ymax = self.ymin, self.ymax

        def step(frame):
            t = frame / frames
            self.xmin = start_xmin + t * (target_xmin - start_xmin)
            self.xmax = start_xmax + t * (target_xmax - start_xmax)
            self.ymin = start_ymin + t * (target_ymin - start_ymin)
            self.ymax = start_ymax + t * (target_ymax - start_ymax)
            self.draw_mandelbrot()
            if frame < frames:
                self.root.after(delay, step, frame + 1)

        step(0)

    def zoom_in(self):
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
