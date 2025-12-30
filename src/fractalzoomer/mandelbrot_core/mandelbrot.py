import numpy as np

class MandelbrotSet: #Pure Mandelbrot math function


    def __init__(self, max_iter=256):
        self.__max_iter = max_iter

    def compute(self, c: np.complex64) -> np.complex64:
        z = np.complex64(0.0, 0.0)
        for _ in range(self.__max_iter):
            z = z * z + c
        return z
    
    def compute_array(self, c_array: np.ndarray) -> np.ndarray:
        z = np.zeros_like(c_array, dtype=np.complex64)
        for _ in range(self.__max_iter):
            z = z * z + c_array
        return z