import pytest
import numpy as np
import tempfile
from pathlib import Path
from PIL import Image

class TestFractalExporter:
    # Test suite for exporting fractal images

    @pytest.fixture
    def sample_fractal(self):
        # Create a sample fractal array for testing
        return np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    
    @pytest.fixture
    def exporter(self):
        # Instantiate the FractalExporter class
        from src.fractalzoomer.utils.exporter import FractalExporter
        return FractalExporter()
    
    def test_exporter_exists(self):
        # Test that the exporter class can be instantiated
        from fractalzoomer.utils.exporter import FractalExporter
        assert FractalExporter is not None
    
    def test_exporter_has_save_method(self, exporter):
        # Test that the exporter has a save_image method
        assert hasattr(exporter, 'save_image')
        assert callable(getattr(exporter, 'save_image'))
    
    def test_exporter_has_to_image_method(self, exporter):
        # Test that the exporter has a to_image method
        assert hasattr(exporter, 'to_image')
        assert callable(getattr(exporter, 'to_image'))
    
    def test_array_to_image_returns_pil_image(self, exporter, sample_fractal_data):
        # Test that the to_image method returns a PIL Image
        img = exporter.array_to_image(sample_fractal_data)
        assert isinstance(img, Image.Image)
    
    def test_array_to_image_preserves_dimensions(self, exporter, sample_fractal_data):
        # Test that the to_image method preserves the dimensions of the array
        img = exporter.array_to_image(sample_fractal_data)
        assert img.size == (sample_fractal_data.shape[1], sample_fractal_data.shape[0]) 
    
    def test_save_creates_png_file(self, exporter, sample_fractal_data):
        # Test that the save_image method creates a PNG file
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_fractal.png"
            img = exporter.array_to_image(sample_fractal_data)
            exporter.save(img, str(filepath))
            
            assert filepath.exists()
            loaded = Image.open(filepath)
            assert loaded.size == img.size
    
    def test_save_creates_jpeg_file(self, exporter, sample_fractal_data):
        # Test that the save_image method creates a JPEG file
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_fractal.jpg"
            img = exporter.array_to_image(sample_fractal_data)
            exporter.save(img, str(filepath))
            
            assert filepath.exists()
    
    def test_supported_formats(self, exporter):
        # Test that the exporter supports PNG and JPEG formats
        supported_formats = exporter.get_supported_formats()
        assert 'PNG' in supported_formats
        assert 'JPEG' in supported_formats
    