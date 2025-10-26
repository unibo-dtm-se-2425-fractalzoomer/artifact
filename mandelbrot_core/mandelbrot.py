
W, H       = 600, 400     # canvas size (pixels)
MAX_ITER   = 256          # iteration cap
INIT_CX    = -0.5         # initial center (real)
INIT_CY    = 0.0          # initial center (imag)
INIT_HX    = 3.5 / 2      # initial half-width of view in complex plane
INIT_HY    = 2.0 / 2      # initial half-height of view in complex plane
ZOOM_STEP  = 0.9          # mouse wheel notch: <1 zoom-in, >1 zoom-out
PAN_BTN    = 1            # left button


class MandelbrotSet:

    def __init__(self, max_iter=MAX_ITER):
        self.max_iter = max_iter

    @staticmethod
    def inside_fast(re, im):
        """Quick interior tests: main cardioid and period-2 bulb."""
        # period-2 bulb (center -1, radius 1/4)
        xp1 = re + 1.0
        if xp1 * xp1 + im * im < 0.25 * 0.25:
            return True

        # main cardioid
        xm = re - 0.25
        q = xm * xm + im * im
        return q * (q + xm) < 0.25 * im * im

    def iterations(self, re, im):
        """Escape-time iteration count for c = re + i*im."""
        if self.inside_fast(re, im):
            return self.max_iter
        zr = 0.0
        zi = 0.0
        it = 0
        while (zr * zr + zi * zi) <= 4.0 and it < self.max_iter:
            zr, zi = zr * zr - zi * zi + re, 2.0 * zr * zi + im
            it += 1
        return it