class BurningShip:
    def __init__(self, max_iter=100):
        self.max_iter = max_iter
    
    def iterations(self, cx, cy):
        zx, zy = 0.0, 0.0
        for i in range(self.max_iter):
            if zx * zx + zy * zy > 4:
                return i
            xtemp = zx * zx - zy * zy + cx
            zy = abs(2 * zx * zy) + cy
            zx = abs(xtemp)
        return self.max_iter
