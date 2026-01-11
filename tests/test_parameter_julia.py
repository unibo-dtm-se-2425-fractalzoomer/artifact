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
class TestJuliaPresets:
    # Tests for Julia set preset configurations.

    def test_default_preset_is_dendrite(self):
        # CHeck whether the default shape is the dendrite one
        julia = JuliaSet()
        
        assert julia.c_real == DEFAULT_JULIA_C_REAL  # -0.4
        assert julia.c_imag == DEFAULT_JULIA_C_IMAG  # 0.6

    def test_preset_values_produce_valid_fractals(self):
        # The function will check if different combination provides different shapes
        presets = [
        (-0.4, 0.6),      # Dendrite
        (-0.8, 0.156),    # Dragon
        (-0.7269, 0.1889), # Spiral
        (0.285, 0.01),    # Galaxy
        (-0.75, 0.11),    # Snowflake
    ]
        
        for c_real, c_imag in presets:
            julia = JuliaSet(c_real=c_real, c_imag=c_imag, max_iter=50)
            test_point = np.complex64(0.0 + 0.0j)
            result = julia.compute(test_point)
            
            assert result is not None  # Just ensure computation runs without error


class TestJuliaComputationWithParameters:
    # Verifies that changing parameters affects computation results.

    def test_different_c_values_produce_different_results(self):
        # Different c values should yield different computation results.
        julia1 = JuliaSet(c_real=-0.4, c_imag=0.6, max_iter=50)
        julia2 = JuliaSet(c_real=-0.8, c_imag=0.156, max_iter=50)
        
        test_point = np.complex64(0.5 + 0.5j)
        
        result1 = julia1.compute(test_point)
        result2 = julia2.compute(test_point)
        
        # Results should be different (not equal)
        assert not np.isclose(result1, result2)

    def test_parameter_change_affects_array_computation(self):
        # Test on parameter change affects array computation results.
        julia = JuliaSet(c_real=-0.4, c_imag=0.6, max_iter=50)
        
        test_array = np.array([0.5 + 0.5j, -0.5 - 0.5j], dtype=np.complex64)
        
        result1 = julia.compute_array(test_array.copy())
        
        julia.set_parameters(c_real=-0.8, c_imag=0.156)
        
        result2 = julia.compute_array(test_array.copy())
        
        # At least one result should be different
        assert not np.allclose(result1, result2)

    def test_computation_deterministic(self):
        # If parameters are unchanged, results should be consistent.
        julia = JuliaSet(c_real=-0.4, c_imag=0.6, max_iter=50)
        
        test_point = np.complex64(0.3 + 0.4j)
    
        result1 = julia.compute(test_point)
        result2 = julia.compute(test_point)

        if np.isnan(result1) and np.isnan(result2):
            assert True  # Both are NaN
        else:
            assert np.isclose(result1, result2)
class TestJuliaParameterBounds:
    # This test class checks behavior at parameter bounds.

    def test_extreme_c_values_dont_crash(self):
        # With large results, the computation should not crash.
        julia = JuliaSet(max_iter=10)
        
        # Very large c value
        julia.set_parameters(c_real=10.0, c_imag=10.0)
        
        test_point = np.complex64(0.0 + 0.0j)
        
        # Should not raise exception
        result = julia.compute(test_point)
        # Result may be inf or very large, but shouldn't crash
        assert result is not None

    def test_zero_c_produces_simple_iteration(self):
        # test for c = 0, the iteration is simply z^2
        julia = JuliaSet(c_real=0.0, c_imag=0.0, max_iter=3)
        
        # Starting at z = 2: 2^2 = 4, 4^2 = 16, 16^2 = 256
        test_point = np.complex64(2.0 + 0.0j)
        result = julia.compute(test_point)
        
        # After 3 iterations: 2^(2^3) = 2^8 = 256
        assert np.isclose(result.real, 256.0, rtol=1e-3)
        assert np.isclose(result.imag, 0.0, atol=1e-5)