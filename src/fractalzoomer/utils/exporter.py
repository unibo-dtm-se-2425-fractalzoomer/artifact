from typing import Dict, Any, Optional, List
from pathlib import Path
import numpy as np
from PIL import Image, PngImagePlugin


class FractalExporter:
    # Exporter class for fractal images. It handles conversion from numpy arrays to images

    # Class-level list of supported formats
    SUPPORTED_FORMATS: List[str] = ['PNG', 'JPEG', 'BMP', 'TIFF', 'GIF']

    def __init__(self) -> None:
        # Initialize any necessary attributes here
        pass

    def get_supported_formats(self) -> List[str]:
        # Return the list of supported image formats, which aims to be extensible in the future.
        return self.SUPPORTED_FORMATS.copy()

    def array_to_image(self, data: np.ndarray, colormap: str = "grayscale") -> Image.Image:
        # Convert a 2D numpy array to a PIL Image using the specified colormap.
        if colormap == "grayscale":
            # Ensure data is uint8 for grayscale
            if data.dtype != np.uint8:
                data = np.clip(data, 0, 255).astype(np.uint8)
            img = Image.fromarray(data, mode='L')
        else:
            raise ValueError(f"Unsupported colormap: {colormap}")
        return img

    def save(
        self,
        image: Image.Image,
        filepath: str,
        format: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        # It saves the given PIL Image to the specified filepath in the desired format, handling metadata if provided.
        path = Path(filepath)
        
        if format is None:
            ext = path.suffix.lower()
            format_map = {
                '.png': 'PNG',
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG',
                '.bmp': 'BMP',
                '.tiff': 'TIFF',
                '.tif': 'TIFF',
                '.gif': 'GIF',
            }
            format = format_map.get(ext, 'PNG')

        # Handle metadata for PNG format
        if format == 'PNG' and metadata:
            pnginfo = PngImagePlugin.PngInfo()
            for key, value in metadata.items():
                pnginfo.add_text(key, str(value))
            image.save(filepath, format=format, pnginfo=pnginfo)
        else:
            # For JPEG, need to convert L mode to RGB
            if format == 'JPEG' and image.mode == 'L':
                image = image.convert('RGB')
            image.save(filepath, format=format)

    def export_fractal(
        self,
        data: np.ndarray,
        filepath: str,
        colormap: str = 'grayscale',
        format: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        # Main method to export a fractal image from a numpy array to a file.
        image = self.array_to_image(data, colormap)
        self.save(image, filepath, format, metadata)