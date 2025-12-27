
W, H       = 600, 400     # canvas size (pixels)
MAX_ITER   = 256          # base iteration cap (adaptive adds more as you zoom)

# A good default view for Burning Ship
INIT_CX    = -1.75        # initial center (real)
INIT_CY    = -0.03        # initial center (imag)
INIT_HX    = 3.5 / 2      # half-width of view in complex plane
INIT_HY    = 2.0 / 2      # half-height of view in complex plane

ZOOM_STEP  = 0.9          # mouse wheel notch: <1 zoom-in, >1 zoom-out
PAN_BTN    = 1            # left button


# ---------------------------
# Burning Ship math (OOP)
# ---------------------------
class BurningShipSet:
    """
    Pure Burning Ship math (no UI).
    Iteration:
        z_{n+1} = (|Re(z_n)| + i*|Im(z_n)|)^2 + c
    Starts from z0 = 0, where c is the pixel point in the complex plane.
    """

    def __init__(self, max_iter=MAX_ITER):
        self.max_iter = max_iter

    def iterations(self, c_re, c_im):
        """
        Escape-time iteration count for c = c_re + i*c_im.
        Points that do not escape within max_iter return max_iter.
        """
        zr = 0.0
        zi = 0.0
        it = 0
        # Escape radius 2 -> |z|^2 > 4
        while (zr * zr + zi * zi) <= 4.0 and it < self.max_iter:
            # Burning Ship: take absolute values before squaring
            ar = abs(zr)
            ai = abs(zi)
            zr, zi = ar * ar - ai * ai + c_re, 2.0 * ar * ai + c_im
            it += 1
        return it
