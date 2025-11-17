import math
import sys
from pathlib import Path


def _find_source_root(test_file: Path) -> Path:
    """Return the nearest ancestor directory that contains the ``ui`` package."""

    for candidate in (test_file.parent,) + tuple(test_file.parents):
        if (candidate / "ui").is_dir():
            return candidate
    return test_file.parent


PROJECT_ROOT = _find_source_root(Path(__file__).resolve())
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.app import screen_to_complex, W, H


def test_screen_to_complex_top_left():
    center_x, center_y = -0.5, 0.0
    half_width, half_height = 1.75, 1.0

    real, imag = screen_to_complex(0, 0, center_x, center_y, half_width, half_height,
                                   width=W, height=H)

    assert math.isclose(real, center_x - half_width)
    assert math.isclose(imag, center_y + half_height)


def test_screen_to_complex_bottom_right():
    center_x, center_y = -0.5, 0.0
    half_width, half_height = 1.75, 1.0

    real, imag = screen_to_complex(W, H, center_x, center_y, half_width, half_height,
                                   width=W, height=H)

    assert math.isclose(real, center_x + half_width)
    assert math.isclose(imag, center_y - half_height)