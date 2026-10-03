"""An educational, white-normalized Hunt–Pointer–Estevez cone model.

Inputs are encoded sRGB (0–255) and a linear-light intensity multiplier (0–1).
Responses are relative excitations, not firing rates or spectral measurements.
"""
import math

SRGB_TO_XYZ = (
    (0.4124564, 0.3575761, 0.1804375),
    (0.2126729, 0.7151522, 0.0721750),
    (0.0193339, 0.1191920, 0.9503041),
)
XYZ_TO_LMS = (
    (0.38971, 0.68898, -0.07868),
    (-0.22981, 1.18340, 0.04641),
    (0.0, 0.0, 1.0),
)
# Compose and normalize each row against full-intensity sRGB D65 white.
_RAW = tuple(tuple(sum(row[k] * SRGB_TO_XYZ[k][j] for k in range(3))
                   for j in range(3)) for row in XYZ_TO_LMS)
RGB_TO_LMS = tuple(tuple(value / sum(row) for value in row) for row in _RAW)


def _validate(red, green, blue, luminosity):
    for value, maximum in zip((red, green, blue, luminosity), (255, 255, 255, 1)):
        if not math.isfinite(value) or not 0 <= value <= maximum:
            raise ValueError('RGB must be finite and in [0, 255]; luminosity in [0, 1].')


def srgb_to_linear(value):
    """Decode a normalized sRGB channel."""
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def linear_to_srgb(value):
    """Encode a normalized linear-light channel."""
    return 12.92 * value if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055


def cone_activation(red, green, blue, luminosity=1.0):
    """Return relative S, M, L responses in [0, 1], white = (1, 1, 1)."""
    _validate(red, green, blue, luminosity)
    linear = [srgb_to_linear(v / 255) * luminosity for v in (red, green, blue)]
    lms = [sum(a * b for a, b in zip(row, linear)) for row in RGB_TO_LMS]
    return tuple(reversed(lms))


def display_rgb(red, green, blue, luminosity=1.0):
    """Return the displayed sRGB after scaling intensity in linear light."""
    _validate(red, green, blue, luminosity)
    return tuple(math.floor(255 * linear_to_srgb(srgb_to_linear(v / 255) * luminosity) + 0.5)
                 for v in (red, green, blue))
