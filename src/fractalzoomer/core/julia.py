import numpy as np
from .base import FractalSet


# Default Julia constant (dendrite shape)
DEFAULT_JULIA_C_REAL = -0.4
DEFAULT_JULIA_C_IMAG = 0.6

# Julia Set fractal computation
class JuliaSet(FractalSet):
    def __init__(
        self,
        c_real: float = DEFAULT_JULIA_C_REAL,
        c_imag: float = DEFAULT_JULIA_C_IMAG,
        max_iter: int = 256
    ):
        super().__init__(max_iter)
        self._c_real = float(c_real)
        self._c_imag = float(c_imag)
        self._c = np.complex64(c_real + 1j * c_imag)

    @property
    #Get the ral part of c
    def c_real(self) -> float:
        return self._c_real

    @property
    # Get the imaginary part of c
    def c_imag(self) -> float:
        return self._c_imag

    @property
    # Get the complex
    def c(self) -> np.complex64:
        return self._c
#Compute Julia iteration for a single starting point
    def compute(self, z: np.complex64) -> np.complex64:
        for _ in range(self._max_iter):
            z = z * z + self._c
        return z
# COmpute Jlia iteration for an array of starting point
    def compute_array(self, z0_array: np.ndarray) -> np.ndarray:
        z = z0_array.copy().astype(np.complex64)
        for _ in range(self._max_iter):
            z = z * z + self._c
        return z

    def get_parameters(self) -> dict:
        return {
            "c_real": self._c_real,
            "c_imag": self._c_imag,
            "max_iter": self._max_iter
        }

    def set_parameters(self, **kwargs) -> None:
        if "c_real" in kwargs:
            self._c_real = float(kwargs["c_real"])
        if "c_imag" in kwargs:
            self._c_imag = float(kwargs["c_imag"])
        if "max_iter" in kwargs:
            max_iter = kwargs["max_iter"]
            if max_iter <= 0:
                raise ValueError("max_iter must be a positive integer")
            self._max_iter = max_iter
        
        # Update the complex constant
        self._c = np.complex64(self._c_real + 1j * self._c_imag)