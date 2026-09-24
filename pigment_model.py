"""Reflected spectra, numerical cone integrals, and CIE XYZ → sRGB under D65."""
import csv
import json
import math
from pathlib import Path
from color_model import linear_to_srgb
from spectral_model import cone_sensitivities, WAVELENGTHS

DATA = Path(__file__).resolve().parent / 'data'
# Standard D65 XYZ to linear sRGB (W3C CSS Color 4).
XYZ_TO_RGB = ((3.2409699419, -1.5373831776, -0.4986107603),
              (-0.9692436363, 1.8759675015, 0.0415550574),
              (0.0556300797, -0.2039769589, 1.0569715142))


def validate_pigment(pigment):
    x, y = pigment['wavelength'], pigment['values']
    kind = pigment['kind']
    if (kind not in ('absorbance', 'reflectance') or len(x) != len(y) or len(x) < 2
            or any(not math.isfinite(v) for v in x + y)
            or x[0] > 390 or x[-1] < 780
            or any(b <= a for a, b in zip(x, x[1:])) or min(y) < 0
            or (kind == 'reflectance' and max(y) > 1)):
        raise ValueError(f"Invalid spectrum: {pigment.get('id', 'unnamed')}")


def load_pigments():
    pigments = json.loads((DATA / 'pigments.json').read_text())
    if not pigments:
        raise ValueError('At least one pigment is required')
    for pigment in pigments:
        validate_pigment(pigment)
    if len({p['id'] for p in pigments}) != len(pigments):
        raise ValueError('Duplicate pigment id')
    return pigments


def interpolate(x, y, target):
    j = 0
    result = []
    for nm in target:
        while j < len(x)-2 and nm > x[j+1]:
            j += 1
        result.append(y[j] + (y[j+1]-y[j])*(nm-x[j])/(x[j+1]-x[j]))
    return result


def integrate(x, y):
    return sum((b-a)*(u+v)/2 for a,b,u,v in zip(x,x[1:],y,y[1:]))


def color_matching_data():
    with (DATA / 'cie_xyz_1931_2deg.csv').open() as f:
        rows = list(csv.DictReader(f))
    result = {key: [float(r[key]) for r in rows] for key in ('wavelength','x','y','z')}
    with (DATA / 'cie_d65.csv').open() as f:
        rows = list(csv.DictReader(f))
    result['illuminant'] = interpolate([float(r['wavelength']) for r in rows],
                                      [float(r['power']) for r in rows], result['wavelength'])
    return result


def pigment_reflectance(pigment):
    validate_pigment(pigment)
    samples = interpolate(pigment['wavelength'], pigment['values'], WAVELENGTHS)
    # Absorbing layer over a perfect white backing, two passes; no scattering.
    return [10 ** (-2 * a) for a in samples] if pigment['kind'] == 'absorbance' else samples


def pigment_signal(pigment):
    cones = cone_sensitivities()
    illuminant = color_matching_data()['illuminant']
    reflectance = pigment_reflectance(pigment)
    values = []
    for k in ('S','M','L'):
        reference = [e*c for e,c in zip(illuminant, cones[k])]
        values.append(integrate(WAVELENGTHS, [r*v for r,v in zip(reflectance, reference)])
                      / integrate(WAVELENGTHS, reference))
    return reflectance, values


def spectrum_rgb(reflectance):
    if len(reflectance) != len(WAVELENGTHS) or any(not math.isfinite(r) or not 0 <= r <= 1 for r in reflectance):
        raise ValueError('Reflectance must cover the 390–780 nm grid and lie in [0,1]')
    data = color_matching_data()
    light = [e*r for e,r in zip(data['illuminant'], reflectance)]
    white_y = integrate(WAVELENGTHS, [e*y for e,y in zip(data['illuminant'],data['y'])])
    xyz = [integrate(WAVELENGTHS, [e*c for e,c in zip(light, data[k])])/white_y for k in ('x','y','z')]
    linear = [sum(a*b for a,b in zip(row,xyz)) for row in XYZ_TO_RGB]
    # Fixed white normalization; clip only at the display gamut boundary.
    return tuple(math.floor(255*linear_to_srgb(min(1,max(0,v)))+.5) for v in linear)
