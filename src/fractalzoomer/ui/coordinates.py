"""
Coordinate transformation utilities.

This module provides functions for converting between screen coordinates
and complex plane coordinates, independent of the GUI framework.
"""

import numpy as np

# Display constants (defaults)
DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 400


def screen_to_complex(
    x: float,
    y: float,
    center_x: float,
    center_y: float,
    half_width: float,
    half_height: float,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT
) -> tuple[float, float]:
    """
    Convert screen coordinates to complex plane coordinates.
    
    Args:
        x: Screen x coordinate (pixels from left).
        y: Screen y coordinate (pixels from top).
        center_x: Real part of the viewport center.
        center_y: Imaginary part of the viewport center.
        half_width: Half-width of the viewport in complex plane units.
        half_height: Half-height of the viewport in complex plane units.
        width: Screen width in pixels.
        height: Screen height in pixels.
        
    Returns:
        Tuple of (real, imaginary) coordinates in the complex plane.
    """
    x_frac = x / width
    y_frac = y / height
    
    x_min = center_x - half_width
    y_max = center_y + half_height
    
    real = x_min + x_frac * (2 * half_width)
    imag = y_max - y_frac * (2 * half_height)
    
    return real, imag


def complex_to_screen(
    real: float,
    imag: float,
    center_x: float,
    center_y: float,
    half_width: float,
    half_height: float,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT
) -> tuple[float, float]:
    """
    Convert complex plane coordinates to screen coordinates.
    
    Args:
        real: Real part of the complex number.
        imag: Imaginary part of the complex number.
        center_x: Real part of the viewport center.
        center_y: Imaginary part of the viewport center.
        half_width: Half-width of the viewport in complex plane units.
        half_height: Half-height of the viewport in complex plane units.
        width: Screen width in pixels.
        height: Screen height in pixels.
        
    Returns:
        Tuple of (x, y) screen coordinates.
    """
    x_frac = (real - center_x + half_width) / (2 * half_width)
    y_frac = (center_y + half_height - imag) / (2 * half_height)
    
    x = x_frac * width
    y = y_frac * height
    
    return x, y


class Viewport:
    """Handles coordinate transformation between screen and complex plane."""
    
    def __init__(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
        """
        Initialize the viewport.
        
        Args:
            width: Screen width in pixels.
            height: Screen height in pixels.
        """
        self._width = width
        self._height = height
        self._size = np.array([width, height], dtype=float)
        self.viewport_center = self._size / 2

    @property
    def width(self) -> int:
        """Get viewport width."""
        return self._width

    @property
    def height(self) -> int:
        """Get viewport height."""
        return self._height

    def to_complex_plane(
        self,
        x: float,
        y: float,
        center_x: float,
        center_y: float,
        half_width: float,
        half_height: float
    ) -> np.complex64:
        """
        Convert screen coordinates to a complex number.
        
        Args:
            x: Screen x coordinate.
            y: Screen y coordinate.
            center_x: Viewport center real part.
            center_y: Viewport center imaginary part.
            half_width: Half-width in complex units.
            half_height: Half-height in complex units.
            
        Returns:
            Complex number representing the point in the complex plane.
        """
        real, imag = screen_to_complex(
            x, y, center_x, center_y, half_width, half_height,
            self._width, self._height
        )
        return np.complex64(real + 1j * imag)

    def to_viewport_plane(
        self,
        z: np.complex64,
        center_x: float,
        center_y: float,
        half_width: float,
        half_height: float
    ) -> np.ndarray:
        """
        Convert a complex number to screen coordinates.
        
        Args:
            z: Complex number in the complex plane.
            center_x: Viewport center real part.
            center_y: Viewport center imaginary part.
            half_width: Half-width in complex units.
            half_height: Half-height in complex units.
            
        Returns:
            Array [x, y] of screen coordinates.
        """
        x, y = complex_to_screen(
            z.real, z.imag, center_x, center_y, half_width, half_height,
            self._width, self._height
        )
        return np.array([x, y], dtype=float)