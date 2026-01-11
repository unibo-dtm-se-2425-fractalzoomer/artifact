import pytest
import numpy as np
from fractalzoomer.core import JuliaSet, DEFAULT_JULIA_C_REAL, DEFAULT_JULIA_C_IMAG
class TestJuliaParameterValidation:
    """Tests for Julia parameter validation logic."""

    def test_c_real_accepts_valid_range(self):
        """c_real should accept values in reasonable range [-2, 2]."""
        julia = JuliaSet()
        
        # Test boundary values
        julia.set_parameters(c_real=-2.0)
        assert julia.c_real == -2.0
        
        julia.set_parameters(c_real=2.0)
        assert julia.c_real == 2.0
        
        julia.set_parameters(c_real=0.0)
        assert julia.c_real == 0.0

    def test_c_imag_accepts_valid_range(self):
        """c_imag should accept values in reasonable range [-2, 2]."""
        julia = JuliaSet()
        
        julia.set_parameters(c_imag=-2.0)
        assert julia.c_imag == -2.0
        
        julia.set_parameters(c_imag=2.0)
        assert julia.c_imag == 2.0

    def test_c_real_and_c_imag_update_together(self):
        """Setting both parameters should update the complex constant."""
        julia = JuliaSet()
        
        julia.set_parameters(c_real=-0.8, c_imag=0.156)
        
        assert julia.c_real == -0.8
        assert julia.c_imag == 0.156
        assert np.isclose(julia.c.real, -0.8)
        assert np.isclose(julia.c.imag, 0.156)

    def test_partial_parameter_update_preserves_other(self):
        """Updating one parameter should not affect the other."""
        julia = JuliaSet(c_real=-0.4, c_imag=0.6)
        
        julia.set_parameters(c_real=-0.8)
        
        assert julia.c_real == -0.8
        assert julia.c_imag == 0.6  # Should be unchanged

    def test_float_conversion(self):
        """Parameters should be converted to float."""
        julia = JuliaSet()
        
        # Pass as int
        julia.set_parameters(c_real=1, c_imag=-1)
        
        assert isinstance(julia.c_real, float)
        assert isinstance(julia.c_imag, float)
        assert julia.c_real == 1.0
        assert julia.c_imag == -1.0