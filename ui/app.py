import tkinter as tk

class FractalZoomerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fractal Zoomer")
        self.root.geometry("800x600")
        
        # Fractal parameters - store as instance variables for zoom feature
        self.width = 800
        self.height = 550
        self.xmin, self.xmax = -2.0, 1.0
        self.ymin, self.ymax = -1.5, 1.5
        self.max_iter = 50

        # Canvas for drawing
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Button panel
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x")
        
        # Zoom In button
        zoom_in_btn = tk.Button(button_frame, text="Zoom In", command=self.zoom_in)
        zoom_in_btn.pack(side="left", padx=10, pady=10)
        
        # Zoom Out button
        zoom_out_btn = tk.Button(button_frame, text="Zoom Out", command=self.zoom_out)
        zoom_out_btn.pack(side="left", padx=10, pady=10)
        
        # Draw Mandelbrot on startup
        self.draw_mandelbrot()
        
    def draw_mandelbrot(self):
        self.canvas.delete("all")
        for x in range(self.width):
            for y in range(self.height):
                cx = self.xmin + (x / self.width) * (self.xmax - self.xmin)
                cy = self.ymin + (y / self.height) * (self.ymax - self.ymin)
                c = complex(cx, cy)
                z = 0
                n = 0
                while abs(z) <= 2 and n < self.max_iter:
                    z = z*z + c
                    n += 1
                shade = 255 - int(n * 255 / self.max_iter)
                color = f'#{shade:02x}{shade:02x}{shade:02x}'
                self.canvas.create_line(x, y, x+1, y, fill=color)
                
    def zoom_in(self):
        # Shrink visible area to zoom in
        x_range = (self.xmax - self.xmin) * 0.5
        y_range = (self.ymax - self.ymin) * 0.5
        x_center = (self.xmax + self.xmin) / 2
        y_center = (self.ymax + self.ymin) / 2
        self.xmin = x_center - x_range / 2
        self.xmax = x_center + x_range / 2
        self.ymin = y_center - y_range / 2
        self.ymax = y_center + y_range / 2
        self.draw_mandelbrot()
        
    def zoom_out(self):
        # Expand visible area to zoom out
        x_range = (self.xmax - self.xmin) * 2
        y_range = (self.ymax - self.ymin) * 2
        x_center = (self.xmax + self.xmin) / 2
        y_center = (self.ymax + self.ymin) / 2
        self.xmin = x_center - x_range / 2
        self.xmax = x_center + x_range / 2
        self.ymin = y_center - y_range / 2
        self.ymax = y_center + y_range / 2
        self.draw_mandelbrot()

def main():
    root = tk.Tk()
    app = FractalZoomerUI(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
