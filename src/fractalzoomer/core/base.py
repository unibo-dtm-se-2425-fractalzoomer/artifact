from abc import ABC, abstractmethod
import numpy as np

#Abstract base class for fractal sets computation 
class FractalSet(ABC):

    def __init__(self, max_iter: int = 256):
        if max_iter <= 0:
            raise ValueError("max_iter must be a positive integer")
        self._max_iter = max_iter

    @property
    def max_iter(self) -> int:
        """Get the maximum iteration count."""
        return self._max_iter
#Compute fractal for a single point
    @abstractmethod
    def compute(self, point: np.complex64) -> np.complex64:
        pass
#Compute the fractal iteration for an array of complex points
    @abstractmethod
    def compute_array(self, points: np.ndarray) -> np.ndarray:
        pass
#Get current parameters of the fractal
    @abstractmethod
    def get_parameters(self) -> dict:
        pass
#Set parameters of the fractal
    @abstractmethod
    def set_parameters(self, **kwargs) -> None:
        pass