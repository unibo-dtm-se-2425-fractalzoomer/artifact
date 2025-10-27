class Julia:
    def __init__(self, c_re=-0.7, c_im=0.27015, max_iter=100):
        self.c = complex(c_re, c_im)
        self.max_iter = max_iter
    
    def iterations(self, cx, cy):
        z = complex(cx, cy)
        for i in range(self.max_iter):
            if abs(z) > 2:
                return i
            z = z * z + self.c
        return self.max_iter
