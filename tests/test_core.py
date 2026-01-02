import pytest
import numpy as np
from fractalzoomer.core import (
    FractalSet,
    MandelbrotSet,
    JuliaSet,
    BurningShipSet,
    DEFAULT_JULIA_C_REAL,
    DEFAULT_JULIA_C_IMAG,
)

# Tests whether all classes implement the FractalSet module
class TestFractalSetInterface:

    @pytest.fixture
    def fractal_classes(self):
        return [MandelbrotSet, JuliaSet, BurningShipSet]
# Verify inheritence for all sets
    def test_all_inherit_from_fractal_set(self, fractal_classes):
        for cls in fractal_classes:
            instance = cls() if cls != JuliaSet else cls(-0.4, 0.6)
            assert isinstance(instance, FractalSet)
# Verifies that all sets are computed
    def test_all_have_compute_method(self, fractal_classes):
        for cls in fractal_classes:
            instance = cls() if cls != JuliaSet else cls(-0.4, 0.6)
            assert hasattr(instance, 'compute')
            assert callable(instance.compute)

    def test_all_have_compute_array_method(self, fractal_classes):
        for cls in fractal_classes:
            instance = cls() if cls != JuliaSet else cls(-0.4, 0.6)
            assert hasattr(instance, 'compute_array')
            assert callable(instance.compute_array)

    def test_all_have_get_parameters_method(self, fractal_classes):
        for cls in fractal_classes:
            instance = cls() if cls != JuliaSet else cls(-0.4, 0.6)
            assert hasattr(instance, 'get_parameters')
            params = instance.get_parameters()
            assert isinstance(params, dict)
            assert 'max_iter' in params

    def test_all_have_set_parameters_method(self, fractal_classes):
        for cls in fractal_classes:
            instance = cls() if cls != JuliaSet else cls(-0.4, 0.6)
            assert hasattr(instance, 'set_parameters')
            instance.set_parameters(max_iter=100)
            assert instance.max_iter == 100

# Test suite for MandelbrotSet class. 
class TestMandelbrotSet:
    def test_initialization_default(self):
        m = MandelbrotSet()
        assert m.max_iter == 256
        # Default max_iter should be 256

    def test_initialization_custom_max_iter(self):
        m = MandelbrotSet(max_iter=100)
        assert m.max_iter == 100
        # Custom max_iter should be set correctly

    def test_initialization_invalid_max_iter(self):
        with pytest.raises(ValueError):
            MandelbrotSet(max_iter=0)
        with pytest.raises(ValueError):
            MandelbrotSet(max_iter=-10)
            # Invalid max_iter should raise ValueError

    def test_compute_origin(self):
        m = MandelbrotSet(max_iter=100)
        result = m.compute(np.complex64(0.0 + 0.0j))
        assert np.isfinite(result)
        assert np.abs(result) < 1e10
        # Origin should remain bounded

    def test_compute_escapes(self):
        m = MandelbrotSet(max_iter=100)
        result = m.compute(np.complex64(2.0 + 2.0j))
        # Point outside set should have large magnitude
        assert np.abs(result) > 2.0 or not np.isfinite(result)
        # Point outside the set should escape

    def test_compute_array_shape(self):
        m = MandelbrotSet(max_iter=50)
        input_array = np.array([
            [0.0 + 0.0j, 0.5 + 0.5j],
            [-0.5 + 0.0j, 1.0 + 1.0j]
        ], dtype=np.complex64)
        
        result = m.compute_array(input_array)
        
        assert result.shape == input_array.shape
        # compute_array should preserve input shape

    def test_compute_array_dtype(self):
        m = MandelbrotSet(max_iter=10)
        input_array = np.array([0.0j, 0.5j], dtype=np.complex64)
        result = m.compute_array(input_array)
        assert result.dtype == np.complex64
        # Result dtype should be complex64

    def test_get_parameters(self):
        m = MandelbrotSet(max_iter=200)
        params = m.get_parameters()
        assert params == {"max_iter": 200}
        # get_parameters should return correct dict

    def test_set_parameters(self):
        m = MandelbrotSet(max_iter=100)
        m.set_parameters(max_iter=200)
        assert m.max_iter == 200
        # set_parameters should update max_iter

    def test_set_parameters_invalid(self):
        m = MandelbrotSet()
        with pytest.raises(ValueError):
            m.set_parameters(max_iter=0)
            # Invalid max_iter should raise ValueError

# Test suite for JuliaSet class.
class TestJuliaSet:

    def test_initialization_default(self):
        # Test default initialization
        j = JuliaSet()
        assert j.max_iter == 256
        assert j.c_real == DEFAULT_JULIA_C_REAL
        assert j.c_imag == DEFAULT_JULIA_C_IMAG

    def test_initialization_custom(self):
        # Test custom initialization
        j = JuliaSet(c_real=-0.8, c_imag=0.156, max_iter=100)
        assert j.c_real == -0.8
        assert j.c_imag == 0.156
        assert j.max_iter == 100

    def test_c_property(self):
        # Test that c property returns correct complex value
        j = JuliaSet(c_real=-0.4, c_imag=0.6)
        expected = np.complex64(-0.4 + 0.6j)
        assert np.isclose(j.c.real, expected.real)
        assert np.isclose(j.c.imag, expected.imag)

    def test_compute_origin(self):
        # Test computation at origin
        j = JuliaSet(c_real=0.0, c_imag=0.0, max_iter=100)
        result = j.compute(np.complex64(0.0 + 0.0j))
        assert np.isfinite(result)

    def test_compute_array_shape(self):
        # Test that compute_array preserves input shape
        j = JuliaSet(c_real=-0.4, c_imag=0.6, max_iter=50)
        input_array = np.array([
            [0.0 + 0.0j, 0.5 + 0.5j],
            [-0.5 + 0.0j, 1.0 + 1.0j]
        ], dtype=np.complex64)
        
        result = j.compute_array(input_array)
        
        assert result.shape == input_array.shape

    def test_get_parameters(self):
        # Test get_parameters returns correct dict
        j = JuliaSet(c_real=-0.8, c_imag=0.156, max_iter=200)
        params = j.get_parameters()
        assert params["c_real"] == -0.8
        assert params["c_imag"] == 0.156
        assert params["max_iter"] == 200

    def test_set_parameters_c_values(self):
        # Test setting c_real and c_imag parameters
        j = JuliaSet(c_real=-0.4, c_imag=0.6)
        j.set_parameters(c_real=-0.8, c_imag=0.156)
        assert j.c_real == -0.8
        assert j.c_imag == 0.156
        # Verify internal complex value updated
        assert np.isclose(j.c.real, -0.8)
        assert np.isclose(j.c.imag, 0.156)

    def test_set_parameters_partial(self):
        # Test setting only one parameter
        j = JuliaSet(c_real=-0.4, c_imag=0.6, max_iter=100)
        j.set_parameters(c_real=-0.8)
        assert j.c_real == -0.8
        assert j.c_imag == 0.6  # Unchanged
        assert j.max_iter == 100  # Unchanged

# Test suite for BurningShipSet class.
class TestBurningShipSet:

    def test_initialization_default(self):
        # Test default initialization
        b = BurningShipSet()
        assert b.max_iter == 256

    def test_initialization_custom_max_iter(self):
        # Test initialization with custom max_iter
        b = BurningShipSet(max_iter=100)
        assert b.max_iter == 100

    def test_compute_origin(self):
        # Test computation at origin
        b = BurningShipSet(max_iter=100)
        result = b.compute(np.complex64(0.0 + 0.0j))
        # Origin stays at origin for burning ship
        assert np.isclose(result, 0.0)

    def test_compute_uses_absolute_values(self):
        # Test that compute uses absolute values correctly
        b = BurningShipSet(max_iter=1)
        # After 1 iteration: z = (|0| + i|0|)^2 + c = c
        result = b.compute(np.complex64(0.5 + 0.5j))
        assert np.isclose(result.real, 0.5)
        assert np.isclose(result.imag, 0.5)

    def test_compute_array_shape(self):
        # Test that compute_array preserves input shape
        b = BurningShipSet(max_iter=50)
        input_array = np.array([
            [0.0 + 0.0j, 0.5 + 0.5j],
            [-0.5 + 0.0j, 1.0 + 1.0j]
        ], dtype=np.complex64)
        
        result = b.compute_array(input_array)
        
        assert result.shape == input_array.shape

    def test_get_parameters(self):
        # Test get_parameters returns correct dict
        b = BurningShipSet(max_iter=200)
        params = b.get_parameters()
        assert params == {"max_iter": 200}

    def test_set_parameters(self):
        # Test set_parameters updates max_iter
        b = BurningShipSet(max_iter=100)
        b.set_parameters(max_iter=200)
        assert b.max_iter == 200


class TestFractalComputationConsistency:
    # Test that single point computation matches array computation

    @pytest.mark.parametrize("fractal_cls,args", [
        (MandelbrotSet, {}),
        (JuliaSet, {"c_real": -0.4, "c_imag": 0.6}),
        (BurningShipSet, {}),
    ])
    def test_single_vs_array_computation(self, fractal_cls, args):
        # Initialize fractal instance
        fractal = fractal_cls(max_iter=50, **args)
        
        test_points = [
            np.complex64(0.0 + 0.0j),
            np.complex64(0.5 + 0.5j),
            np.complex64(-0.5 - 0.5j),
        ]
        
        # Compute individually
        single_results = [fractal.compute(p) for p in test_points]
        
        # Compute as array
        array_input = np.array(test_points, dtype=np.complex64)
        array_results = fractal.compute_array(array_input)
        
        # Compare results (with tolerance for floating point)
        for single, array_val in zip(single_results, array_results):
            if np.isfinite(single) and np.isfinite(array_val):
                assert np.isclose(single, array_val, rtol=1e-5)