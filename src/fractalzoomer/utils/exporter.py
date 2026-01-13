from typing import Dict, Any, Optional, List 
from pathlib import Path
import numpy as np
from PIL import Image, PngImagePlugin

class FractalExporter:
    # Handles exporting fractal images in various formats as image files
    def __init__self(self):
        # Initialize fractal exporter
        pass

    @property
    def supported_formats(self) -> List[str]:
        # Return a list of supported image formats
        return self.supported_formats.copy()
    
    def array_to_image(self, data: np.ndarray, colormap: str = "grayscale") -> Image.Image:
        # Convert a 2D numpy array to a PIL Image using the specified colormap
        if colormap == "grayscale":
            img = Image.fromarray(data, mode='L')
        else:
            raise ValueError(f"Unsupported colormap: {colormap}")
        return img
    
    def save(self, image: Image.Image, filepath: str, format: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        # Save the PIL Image to the specified filepath with optional format and metadata
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

        def export_fractal(self, data: np.ndarray, filepath: str,colormap: str = 'grayscale', format: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
            # Convenience method to convert and save fractal data in one step. It converts the data to an image and saves it.
            image = self.array_to_image(data, colormap)
            self.save(image, filepath, format, metadata)