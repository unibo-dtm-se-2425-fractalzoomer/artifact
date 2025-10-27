class Mandelbrot:
    def __init__(self, max_iter=100):
        self.max_iter = max_iter
    
    def iterations(self, cx, cy):
        z = complex(0, 0)
        c = complex(cx, cy)
        for i in range(self.max_iter):
            if abs(z) > 2:
                return i
            z = z * z + c
        return self.max_iter
