"""Tests for coordinate mapping functions."""

import math
import pytest
from fractalzoomer.ui.coordinates import screen_to_complex, DEFAULT_WIDTH, DEFAULT_HEIGHT

# Use default dimensions for tests
W, H = DEFAULT_WIDTH, DEFAULT_HEIGHT


class TestScreenToComplex:
    """Test suite for screen_to_complex function."""

    def test_top_left_corner(self):
        """Test that top-left screen corner maps to top-left of complex plane."""
        center_x, center_y = -0.5, 0.0
        half_width, half_height = 1.75, 1.0

        real, imag = screen_to_complex(
            0, 0, center_x, center_y, half_width, half_height, width=W, height=H
        )

        assert math.isclose(real, center_x - half_width)
        assert math.isclose(imag, center_y + half_height)

    def test_bottom_right_corner(self):
        """Test that bottom-right screen corner maps to bottom-right of complex plane."""
        center_x, center_y = -0.5, 0.0
        half_width, half_height = 1.75, 1.0

        real, imag = screen_to_complex(
            W, H, center_x, center_y, half_width, half_height, width=W, height=H
        )

        assert math.isclose(real, center_x + half_width)
        assert math.isclose(imag, center_y - half_height)

    def test_center(self):
        """Test that screen center maps to viewport center."""
        center_x, center_y = -0.5, 0.0
        half_width, half_height = 1.75, 1.0

        real, imag = screen_to_complex(
            W / 2, H / 2, center_x, center_y, half_width, half_height, width=W, height=H
        )

        assert math.isclose(real, center_x, rel_tol=1e-5)
        assert math.isclose(imag, center_y, rel_tol=1e-5)

    def test_custom_dimensions(self):
        """Test with custom screen dimensions."""
        center_x, center_y = 0.0, 0.0
        half_width, half_height = 2.0, 2.0
        custom_w, custom_h = 100, 100

        # Top-left should be (-2, 2)
        real, imag = screen_to_complex(
            0, 0, center_x, center_y, half_width, half_height,
            width=custom_w, height=custom_h
        )

        assert math.isclose(real, -2.0)
        assert math.isclose(imag, 2.0)