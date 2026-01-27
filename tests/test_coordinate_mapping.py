import math
import pytest
import numpy as np
from fractalzoomer.ui.coordinates import (
    screen_to_complex,
    complex_to_screen,
    Viewport,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
)

# Use default dimensions for tests
W, H = DEFAULT_WIDTH, DEFAULT_HEIGHT


class TestScreenToComplex:
    # Test suite for screen_to_complex function.

    def test_top_left_corner(self):
        # Test that the top-left corner of the screen maps correctly to the complex plane.
        center_x, center_y = -0.5, 0.0
        half_width, half_height = 1.75, 1.0

        real, imag = screen_to_complex(
            0, 0, center_x, center_y, half_width, half_height, width=W, height=H
        )

        assert math.isclose(real, center_x - half_width)
        assert math.isclose(imag, center_y + half_height)

    def test_bottom_right_corner(self):
        # Test that the bottom-right corner of the screen maps correctly to the complex plane.
        center_x, center_y = -0.5, 0.0
        half_width, half_height = 1.75, 1.0

        real, imag = screen_to_complex(
            W, H, center_x, center_y, half_width, half_height, width=W, height=H
        )

        assert math.isclose(real, center_x + half_width)
        assert math.isclose(imag, center_y - half_height)

    def test_center(self):
        # Test that the center of the screen maps to the center of the complex plane.
        center_x, center_y = -0.5, 0.0
        half_width, half_height = 1.75, 1.0

        real, imag = screen_to_complex(
            W / 2, H / 2, center_x, center_y, half_width, half_height, width=W, height=H
        )

        assert math.isclose(real, center_x, rel_tol=1e-5)
        assert math.isclose(imag, center_y, rel_tol=1e-5)

    def test_custom_dimensions(self):
        # Test with custom screen dimensions.
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

    def test_uses_default_dimensions(self):
        # Test that default dimensions are used when not specified.
        center_x, center_y = 0.0, 0.0
        half_width, half_height = 1.0, 1.0

        # Should use DEFAULT_WIDTH and DEFAULT_HEIGHT
        real, imag = screen_to_complex(
            DEFAULT_WIDTH / 2, DEFAULT_HEIGHT / 2,
            center_x, center_y, half_width, half_height
        )

        assert math.isclose(real, 0.0, abs_tol=1e-10)
        assert math.isclose(imag, 0.0, abs_tol=1e-10)


class TestComplexToScreen:
    # Test suite for complex_to_screen function.

    def test_center_maps_to_screen_center(self):
        center_x, center_y = -0.5, 0.0
        half_width, half_height = 1.75, 1.0

        x, y = complex_to_screen(
            center_x, center_y, center_x, center_y, half_width, half_height,
            width=W, height=H
        )

        assert math.isclose(x, W / 2)
        assert math.isclose(y, H / 2)

    def test_top_left_complex_to_screen(self):
        # Test that complex point (-2, 2) maps to screen (0, 0).
        center_x, center_y = 0.0, 0.0
        half_width, half_height = 2.0, 2.0

        # Complex point (-2, 2) should map to screen (0, 0)
        x, y = complex_to_screen(
            -2.0, 2.0, center_x, center_y, half_width, half_height,
            width=100, height=100
        )

        assert math.isclose(x, 0.0)
        assert math.isclose(y, 0.0)

    def test_bottom_right_complex_to_screen(self):
        # Test that complex point (2, -2) maps to screen (100, 100).
        center_x, center_y = 0.0, 0.0
        half_width, half_height = 2.0, 2.0

        # Complex point (2, -2) should map to screen (100, 100)
        x, y = complex_to_screen(
            2.0, -2.0, center_x, center_y, half_width, half_height,
            width=100, height=100
        )

        assert math.isclose(x, 100.0)
        assert math.isclose(y, 100.0)

    def test_uses_default_dimensions(self):
        # Test that default dimensions are used when not specified.
        center_x, center_y = 0.0, 0.0
        half_width, half_height = 1.0, 1.0

        x, y = complex_to_screen(
            0.0, 0.0, center_x, center_y, half_width, half_height
        )

        assert math.isclose(x, DEFAULT_WIDTH / 2)
        assert math.isclose(y, DEFAULT_HEIGHT / 2)

    def test_inverse_of_screen_to_complex(self):
        # Test that complex_to_screen is the inverse of screen_to_complex.
        center_x, center_y = -0.5, 0.25
        half_width, half_height = 1.5, 1.0
        original_x, original_y = 150, 200

        # Convert screen to complex
        real, imag = screen_to_complex(
            original_x, original_y, center_x, center_y, half_width, half_height,
            width=W, height=H
        )

        # Convert back to screen
        x, y = complex_to_screen(
            real, imag, center_x, center_y, half_width, half_height,
            width=W, height=H
        )

        assert math.isclose(x, original_x, rel_tol=1e-5)
        assert math.isclose(y, original_y, rel_tol=1e-5)


class TestViewport:
    # Test suite for Viewport class.

    def test_initialization_default(self):
        # Test default initialization.
        viewport = Viewport()
        assert viewport.width == DEFAULT_WIDTH
        assert viewport.height == DEFAULT_HEIGHT

    def test_initialization_custom(self):
        # Test custom initialization.
        viewport = Viewport(width=800, height=600)
        assert viewport.width == 800
        assert viewport.height == 600

    def test_viewport_center_calculated(self):
        # Test that viewport_center is calculated correctly.
        viewport = Viewport(width=100, height=200)
        assert viewport.viewport_center[0] == 50.0
        assert viewport.viewport_center[1] == 100.0

    def test_to_complex_plane(self):
        # Test conversion from screen to complex plane.
        viewport = Viewport(width=100, height=100)
        center_x, center_y = 0.0, 0.0
        half_width, half_height = 2.0, 2.0

        # Screen center should map to complex origin
        result = viewport.to_complex_plane(
            50, 50, center_x, center_y, half_width, half_height
        )

        assert isinstance(result, np.complex64)
        assert math.isclose(result.real, 0.0, abs_tol=1e-5)
        assert math.isclose(result.imag, 0.0, abs_tol=1e-5)

    def test_to_complex_plane_corner(self):
        # Test conversion of corner from screen to complex plane.
        viewport = Viewport(width=100, height=100)
        center_x, center_y = 0.0, 0.0
        half_width, half_height = 2.0, 2.0

        # Top-left (0, 0) should map to (-2, 2)
        result = viewport.to_complex_plane(
            0, 0, center_x, center_y, half_width, half_height
        )

        assert math.isclose(result.real, -2.0, rel_tol=1e-5)
        assert math.isclose(result.imag, 2.0, rel_tol=1e-5)

    def test_to_viewport_plane(self):
        # Test conversion from complex plane to screen.
        viewport = Viewport(width=100, height=100)
        center_x, center_y = 0.0, 0.0
        half_width, half_height = 2.0, 2.0

        # Complex origin should map to screen center
        z = np.complex64(0.0 + 0.0j)
        result = viewport.to_viewport_plane(
            z, center_x, center_y, half_width, half_height
        )

        assert isinstance(result, np.ndarray)
        assert math.isclose(result[0], 50.0, rel_tol=1e-5)
        assert math.isclose(result[1], 50.0, rel_tol=1e-5)

    def test_to_viewport_plane_corner(self):
        # Test conversion of corner from complex to screen coordinates.
        viewport = Viewport(width=100, height=100)
        center_x, center_y = 0.0, 0.0
        half_width, half_height = 2.0, 2.0

        # Complex (-2, 2) should map to top-left (0, 0)
        z = np.complex64(-2.0 + 2.0j)
        result = viewport.to_viewport_plane(
            z, center_x, center_y, half_width, half_height
        )

        assert math.isclose(result[0], 0.0, abs_tol=1e-5)
        assert math.isclose(result[1], 0.0, abs_tol=1e-5)

    def test_roundtrip_conversion(self):
        # Test that converting to complex and back gives original coordinates.
        viewport = Viewport(width=W, height=H)
        center_x, center_y = -0.5, 0.0
        half_width, half_height = 1.75, 1.0

        original_x, original_y = 300, 150

        # Screen -> Complex
        z = viewport.to_complex_plane(
            original_x, original_y, center_x, center_y, half_width, half_height
        )

        # Complex -> Screen
        result = viewport.to_viewport_plane(
            z, center_x, center_y, half_width, half_height
        )

        assert math.isclose(result[0], original_x, rel_tol=1e-5)
        assert math.isclose(result[1], original_y, rel_tol=1e-5)

    def test_width_property(self):
        # Test width property returns correct value.
        viewport = Viewport(width=640, height=480)
        assert viewport.width == 640

    def test_height_property(self):
        # Test height property returns correct value.
        viewport = Viewport(width=640, height=480)
        assert viewport.height == 480