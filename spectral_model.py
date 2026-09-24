"""Illustrative pixel spectra; not a calibrated reconstruction from sRGB."""
import csv
import math
from pathlib import Path
from color_model import _validate, srgb_to_linear

WAVELENGTHS = tuple(range(390, 781))
# Deliberately simple hypothetical RGB emitters: center and standard deviation, nm.
PIXEL_PEAKS = ((625, 18), (535, 22), (460, 16))
PIXEL_BASIS = tuple(tuple(math.exp(-0.5 * ((nm - center) / sigma) ** 2)
                          for nm in WAVELENGTHS) for center, sigma in PIXEL_PEAKS)


def pixel_spectrum(red, green, blue, luminosity=1):
    """Three relative emission components and their sum, on a fixed scale."""
    _validate(red, green, blue, luminosity)
    weights = [srgb_to_linear(v / 255) * luminosity for v in (red, green, blue)]
    components = [[weight * y for y in basis] for weight, basis in zip(weights, PIXEL_BASIS)]
    return dict(wavelength=list(WAVELENGTHS), red=components[0], green=components[1],
                blue=components[2], total=[sum(ys) for ys in zip(*components)])


def cone_sensitivities():
    """Stockman–Sharpe 2° energy fundamentals, each normalized to peak 1."""
    with (Path(__file__).resolve().parent / 'data/cone_fundamentals.csv').open() as f:
        rows = list(csv.DictReader(f))
    result = {'wavelength': [float(row['wavelength']) for row in rows]}
    for cone in ('S', 'M', 'L'):
        values = [float(row[cone]) for row in rows]
        peak = max(values)
        result[cone] = [value / peak for value in values]
    return result
