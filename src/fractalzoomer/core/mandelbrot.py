import numpy as np
from .base import FractalSet

# Mandelbrot set fractal computation. The Mandelbrot set has no additional parameters beyond max_iter as the constant c varies across the complex plane (each pixel is a different c)
class MandelbrotSet(FractalSet):

    def __init__(self, max_iter: int = 256):
        super().__init__(max_iter)
# Compute Mandelbrot iteration for a single point
    def compute(self, c: np.complex64) -> np.complex64:
        z = np.complex64(0.0 + 0.0j)
        for _ in range(self._max_iter):
            z = z * z + c
        return z
# Compute Mandelbrot iteration for an array of points
    def compute_array(self, c_array: np.ndarray) -> np.ndarray:
        z = np.zeros_like(c_array, dtype=np.complex64)
        for _ in range(self._max_iter):
            z = z * z + c_array
        return z

    def get_parameters(self) -> dict:
        return {"max_iter": self._max_iter}

    def set_parameters(self, **kwargs) -> None:
        if "max_iter" in kwargs:
            max_iter = kwargs["max_iter"]
            if max_iter <= 0:
                raise ValueError("max_iter must be a positive integer")
            self._max_iter = max_iter