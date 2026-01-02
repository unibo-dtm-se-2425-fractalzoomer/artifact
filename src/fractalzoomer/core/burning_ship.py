import numpy as np
from .base import FractalSet

#Burning Ship fractal set computation
class BurningShipSet(FractalSet):
    def __init__(self, max_iter: int = 256):
        super().__init__(max_iter)
# COmpute Burning Ship iteration for a single point
    def compute(self, c: np.complex64) -> np.complex64:
        z = np.complex64(0.0 + 0.0j)
        for _ in range(self._max_iter):
            zx = abs(z.real)
            zy = abs(z.imag)
            z_real_new = zx * zx - zy * zy + c.real
            z_imag_new = 2.0 * zx * zy + c.imag
            z = np.complex64(z_real_new + 1j * z_imag_new)
        return z
# Compute Burning Ship iteration for an array of points
    def compute_array(self, c_array: np.ndarray) -> np.ndarray:
        z = np.zeros_like(c_array, dtype=np.complex64)
        for _ in range(self._max_iter):
            # Take absolute values element-wise
            zx = np.abs(z.real)
            zy = np.abs(z.imag)
            # Compute new values
            z = (zx * zx - zy * zy + c_array.real) + 1j * (2.0 * zx * zy + c_array.imag)
        return z.astype(np.complex64)

    def get_parameters(self) -> dict:
        return {"max_iter": self._max_iter}

    def set_parameters(self, **kwargs) -> None:
        if "max_iter" in kwargs:
            max_iter = kwargs["max_iter"]
            if max_iter <= 0:
                raise ValueError("max_iter must be a positive integer")
            self._max_iter = max_iter