from .base import FractalSet
from .mandelbrot import MandelbrotSet
from .julia import JuliaSet, DEFAULT_JULIA_C_REAL, DEFAULT_JULIA_C_IMAG
from .burning_ship import BurningShipSet

# Backward-compatible aliases
JULIA_CR = DEFAULT_JULIA_C_REAL
JULIA_CI = DEFAULT_JULIA_C_IMAG

__all__ = [
    "FractalSet",
    "MandelbrotSet",
    "JuliaSet",
    "BurningShipSet",
    "DEFAULT_JULIA_C_REAL",
    "DEFAULT_JULIA_C_IMAG",
    "JULIA_CR",
    "JULIA_CI",
]