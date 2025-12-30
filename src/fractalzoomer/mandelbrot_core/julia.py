import numpy as np

JULIA_CR   = -0.4
JULIA_CI   = 0.6
class JuliaSet: #Pure Julia Set math function. We use the dendrite shape as default: (c = -0.4 + 0.6i)
    """Pure Julia-set math and helpers (no UI)."""

    def __init__(self, c_real, c_imag, max_iter=256):
        self.__c = np.complex64(c_real + 1j * c_imag)
        self.__max_iter = max_iter

    def compute(self, z: np.complex64) -> np.complex64:
        for _ in range(self.__max_iter):
            z = z * z + self.__c
        return z
    
    def compute_array(self, z0_array: np.ndarray) -> np.ndarray:
        z = z0_array.copy()
        for _ in range(self.__max_iter):
            z = z * z + self.__c
        return z