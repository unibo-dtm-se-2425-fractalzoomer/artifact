import pytest
import numpy as np
import tempfile
from pathlib import Path
from PIL import Image

from fractalzoomer.utils.exporter import FractalExporter


class TestFractalExporter:
    # Test suite for the FractalExporter class.

    @pytest.fixture
    def sample_fractal_data(self) -> np.ndarray:
        # Create sample fractal data as a 2D numpy array.
        return np.random.randint(0, 256, (100, 100), dtype=np.uint8)

    @pytest.fixture
    def exporter(self) -> FractalExporter:
        # Instantiate the FractalExporter class.
        return FractalExporter()

    def test_exporter_exists(self):
        # Test that the FractalExporter class can be instantiated.
        exporter = FractalExporter()
        assert exporter is not None

    def test_exporter_has_get_supported_formats_method(self, exporter):
        # Test that the exporter has a get_supported_formats method.
        assert hasattr(exporter, 'get_supported_formats')
        assert callable(getattr(exporter, 'get_supported_formats'))

    def test_exporter_has_array_to_image_method(self, exporter):
        # Test that the exporter has an array_to_image method.
        assert hasattr(exporter, 'array_to_image')
        assert callable(getattr(exporter, 'array_to_image'))

    def test_exporter_has_save_method(self, exporter):
        # Test that the exporter has a save method.
        assert hasattr(exporter, 'save')
        assert callable(getattr(exporter, 'save'))

    def test_exporter_has_export_fractal_method(self, exporter):
        # Test that the exporter has an export_fractal method.
        assert hasattr(exporter, 'export_fractal')
        assert callable(getattr(exporter, 'export_fractal'))

    def test_array_to_image_returns_pil_image(self, exporter, sample_fractal_data):
        # Test that the array_to_image method returns a PIL Image.
        img = exporter.array_to_image(sample_fractal_data)
        assert isinstance(img, Image.Image)

    def test_array_to_image_preserves_dimensions(self, exporter, sample_fractal_data):
        # Test that the array_to_image method preserves image dimensions.
        img = exporter.array_to_image(sample_fractal_data)
        # PIL Image.size returns (width, height), numpy shape is (height, width)
        assert img.size == (sample_fractal_data.shape[1], sample_fractal_data.shape[0])

    def test_array_to_image_grayscale_mode(self, exporter, sample_fractal_data):
        # Test that the array_to_image method creates a grayscale image when specified.
        img = exporter.array_to_image(sample_fractal_data, colormap='grayscale')
        assert img.mode == 'L'

    def test_array_to_image_invalid_colormap_raises(self, exporter, sample_fractal_data):
        # Test that an invalid colormap raises a ValueError.
        with pytest.raises(ValueError, match="Unsupported colormap"):
            exporter.array_to_image(sample_fractal_data, colormap='invalid')

    def test_save_creates_png_file(self, exporter, sample_fractal_data):
        # Test that the save method creates a PNG file.
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_fractal.png"
            img = exporter.array_to_image(sample_fractal_data)
            exporter.save(img, str(filepath))

            assert filepath.exists()
            loaded = Image.open(filepath)
            assert loaded.size == img.size

    def test_save_creates_jpeg_file(self, exporter, sample_fractal_data):
        # Test that the save method creates a JPEG file.
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_fractal.jpg"
            img = exporter.array_to_image(sample_fractal_data)
            exporter.save(img, str(filepath))

            assert filepath.exists()
            # Verify it's a valid image
            loaded = Image.open(filepath)
            assert loaded is not None

    def test_save_creates_bmp_file(self, exporter, sample_fractal_data):
        # Test that the save method creates a BMP file.
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_fractal.bmp"
            img = exporter.array_to_image(sample_fractal_data)
            exporter.save(img, str(filepath))

            assert filepath.exists()

    def test_supported_formats_returns_list(self, exporter):
        # Test that get_supported_formats returns a list.
        supported_formats = exporter.get_supported_formats()
        assert isinstance(supported_formats, list)

    def test_supported_formats_contains_png_and_jpeg(self, exporter):
        # Test that supported formats include PNG and JPEG.
        supported_formats = exporter.get_supported_formats()
        assert 'PNG' in supported_formats
        assert 'JPEG' in supported_formats

    def test_supported_formats_returns_copy(self, exporter):
        # Test that get_supported_formats returns a copy of the list.
        formats1 = exporter.get_supported_formats()
        formats2 = exporter.get_supported_formats()
        formats1.append('TEST')
        assert 'TEST' not in formats2

    def test_export_fractal_creates_file(self, exporter, sample_fractal_data):
        # Test that export_fractal creates an image file.
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "fractal_export.png"
            exporter.export_fractal(sample_fractal_data, str(filepath))

            assert filepath.exists()
            loaded = Image.open(filepath)
            assert loaded.size == (sample_fractal_data.shape[1], sample_fractal_data.shape[0])


class TestExportMetadata:
    # Test suite for exporting fractal images with metadata.

    @pytest.fixture
    def exporter(self) -> FractalExporter:
        # Instantiate the FractalExporter class.
        return FractalExporter()

    @pytest.fixture
    def sample_data(self) -> np.ndarray:
        # Create sample fractal data as a 2D numpy array.
        return np.zeros((50, 50), dtype=np.uint8)

    def test_export_with_metadata_png(self, exporter, sample_data):
        # Test exporting a PNG image with metadata.
        metadata = {
            'fractal_type': 'mandelbrot',
            'center_x': '-0.5',
            'center_y': '0.0',
            'zoom': '1.0',
            'max_iterations': '100'
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "fractal_with_metadata.png"
            img = exporter.array_to_image(sample_data)
            exporter.save(img, str(filepath), metadata=metadata)

            assert filepath.exists()
            # Verify metadata was saved
            loaded = Image.open(filepath)
            # PNG metadata is stored in info dict
            assert 'fractal_type' in loaded.info
            assert loaded.info['fractal_type'] == 'mandelbrot'

    def test_export_fractal_with_metadata(self, exporter, sample_data):
        # Test export_fractal convenience method with metadata.
        metadata = {
            'fractal_type': 'julia',
            'c_real': '-0.4',
            'c_imag': '0.6'
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "julia_fractal.png"
            exporter.export_fractal(
                sample_data,
                str(filepath),
                metadata=metadata
            )

            assert filepath.exists()
            loaded = Image.open(filepath)
            assert loaded.info['fractal_type'] == 'julia'

    def test_metadata_converts_values_to_string(self, exporter, sample_data):
        # Test that numeric metadata values are converted to strings.
        metadata = {
            'zoom': 2.5,  # float
            'iterations': 100,  # int
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_conversion.png"
            img = exporter.array_to_image(sample_data)
            exporter.save(img, str(filepath), metadata=metadata)

            loaded = Image.open(filepath)
            # Values should be stored as strings
            assert loaded.info['zoom'] == '2.5'
            assert loaded.info['iterations'] == '100'

    def test_jpeg_ignores_metadata(self, exporter, sample_data):
        # Test that JPEG files are saved without error even with metadata.
        metadata = {'fractal_type': 'mandelbrot'}
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.jpg"
            img = exporter.array_to_image(sample_data)
            # Should not raise an error
            exporter.save(img, str(filepath), metadata=metadata)
            assert filepath.exists()