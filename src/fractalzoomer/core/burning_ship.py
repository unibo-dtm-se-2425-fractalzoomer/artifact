import numpy as np
class BurningShipSet: #Pure Burning Ship math function
    def __init__(self, max_iter=256):
        self.__max_iter = max_iter

    def compute(self, c: np.complex64) -> np.complex64:
        z = np.complex64(0.0 + 0.0j)
        for _ in range(self.__max_iter):
            zx = abs(z.real)
            zy = abs(z.imag)
            z_real_new = zx * zx - zy * zy + c.real
            z_imag_new = 2.0 * zx * zy + c.imag
            z = np.complex64(z_real_new + 1j * z_imag_new)
        return z
    
    def compute_array(self, c_array: np.ndarray) -> np.ndarray:
        z = np.zeros_like(c_array, dtype=np.complex64)
        for _ in range(self.__max_iter):
            # Take absolute values element-wise
            zx = np.abs(z.real)
            zy = np.abs(z.imag)
            # Compute new values
            z = (zx * zx - zy * zy + c_array.real) + 1j * (2.0 * zx * zy + c_array.imag)
        return z