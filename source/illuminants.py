"""Educational incident-light spectra on the shared wavelength grid."""
import math
import csv
from pathlib import Path


def make_illuminants(wavelength, daylight, observer_y):
    # Planck's wavelength law, B_lambda ∝ lambda^-5 / (exp(hc/lambda kT)-1).
    # The common prefactor cancels when normalizing; lambda is in meters.
    def blackbody(nm, temperature=2856):
        meters = nm * 1e-9
        return meters**-5 / math.expm1(0.01438776877 / (meters * temperature))

    # CIE FL2 contains the phosphor emission AND mercury lines of a fluorescent
    # tube. Use the published spectrum rather than adding arbitrary broad bands.
    path = Path(__file__).resolve().parents[1] / 'data/spectra/fl2_emission_cie_2018.csv'
    with path.open() as file:
        rows = list(csv.DictReader(file))
    if [float(row['wavelength']) for row in rows] != list(wavelength):
        raise ValueError('FL2 spectrum must match the common wavelength grid')
    tube = [float(row['power']) for row in rows]
    if any(not math.isfinite(v) or v < 0 for v in tube) or not any(tube):
        raise ValueError('FL2 spectrum must contain finite nonnegative power')
    spectra = [dict(id='white', power=[1.0]*len(wavelength)),
               dict(id='d65', power=daylight),
               dict(id='tube', power=tube),
               dict(id='incandescent', power=[blackbody(nm) for nm in wavelength])]

    def white_y(power):
        weighted = [e*y for e, y in zip(power, observer_y)]
        return sum((b-a)*(u+v)/2 for a, b, u, v in
                   zip(wavelength, wavelength[1:], weighted, weighted[1:]))

    # Match white-reflector luminance across sources, not their peak or wattage.
    # This isolates color differences caused by spectral shape.
    target = white_y(daylight)
    for spectrum in spectra:
        scale = target / white_y(spectrum['power'])
        spectrum['power'] = [e*scale for e in spectrum['power']]
    return spectra
