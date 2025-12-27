W, H       = 600, 400     # canvas size (pixels)
MAX_ITER   = 256          # base iteration cap (adaptive adds more as you zoom)
INIT_CX    = 0.0          # initial center (real)
INIT_CY    = 0.0          # initial center (imag)
INIT_HX    = 3.5 / 2      # initial half-width of view in complex plane
INIT_HY    = 2.0 / 2      # initial half-height of view in complex plane
ZOOM_STEP  = 0.9          # mouse wheel notch: <1 zoom-in, >1 zoom-out
PAN_BTN    = 1            # left button

# Fixed Julia parameter c = cr + i*ci (classic pretty choice)
JULIA_CR   = -0.8
JULIA_CI   = 0.156

class JuliaSet:
    """Pure Julia-set math and helpers (no UI)."""

    def __init__(self, cr, ci, max_iter=MAX_ITER):
        self.cr = cr
        self.ci = ci
        self.max_iter = max_iter

    def iterations(self, zr, zi):
        """
        Escape-time iteration count for Julia set:
            z_{n+1} = z_n^2 + c, with fixed c.
        Starts from z0 = zr + i*zi (the pixel point).
        """
        it = 0
        while (zr * zr + zi * zi) <= 4.0 and it < self.max_iter:
            zr, zi = zr * zr - zi * zi + self.cr, 2.0 * zr * zi + self.ci
            it += 1
        return it
