"""Rebuild pigment samples from the archived published data, without network access."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def pairs(path):
    result = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        try:
            x, y = map(float, line.split())
        except ValueError:
            continue
        result.append((x, y))
    return result


def prepare():
    with (DATA / 'sources/feret_2017_figure8_digitized.csv').open() as f:
        rows = list(csv.DictReader(f))
    curves = {key: [(float(r['wavelength_nm']), float(r['specific_absorption_cm2_per_ug']))
                    for r in rows if r['pigment'] == key]
              for key in ('anthocyanin', 'chlorophyll', 'carotenoids')}
    with (DATA / 'sources/indigo_cotton_kawahito_2009.csv').open() as f:
        indigo = [(float(r['wavelength']), float(r['reflectance_percent'])) for r in csv.DictReader(f)]
    pigments = []
    for key, raw, kind, source, url in [
        ('anthocyanin', curves['anthocyanin'], 'absorbance', 'Féret et al. (2017) · Fig. 8, digitized solid curve', 'https://doi.org/10.1016/j.rse.2017.03.004'),
        ('indigo', indigo, 'reflectance', 'Kawahito & Yasukawa (2009) · dyed cotton, Fig. 3a', 'https://doi.org/10.3390/ma2020661'),
        ('chlorophyll', curves['chlorophyll'], 'absorbance', 'Féret et al. (2017) · Fig. 8, digitized solid curve', 'https://doi.org/10.1016/j.rse.2017.03.004'),
        ('carotenoids', curves['carotenoids'], 'absorbance', 'Féret et al. (2017) · Fig. 8, digitized solid curve', 'https://doi.org/10.1016/j.rse.2017.03.004'),
    ]:
        # Keep the samples surrounding our domain, so interpolation needs no extrapolation.
        raw.sort()
        if raw[0][0] > 390:
            raw.insert(0, (390, raw[0][1]))  # Figures begin at 400 nm: assume a constant short-wave tail.
        if raw[-1][0] < 780:
            raw.append((780, raw[-1][1]))  # Hold the final endpoint (750 nm for Figure 8, 700 nm for cotton).
        lo = max(i for i, (nm, _) in enumerate(raw) if nm <= 390)
        hi = next(i for i, (nm, _) in enumerate(raw) if nm >= 780)
        selected = raw[lo:hi+1]
        if kind == 'absorbance':
            # Chosen common one-way peak optical density. This sets layer thickness,
            # not a claim about the concentration of the published sample.
            peak = max(v for _, v in selected)
            values = [max(0, v) / peak for _, v in selected]
        else:
            values = [v / 100 for _, v in selected]
        pigments.append(dict(id=key, kind=kind, wavelength=[nm for nm,_ in selected],
                             values=values, source=source, source_url=url))
    (DATA / 'pigments.json').write_text(json.dumps(pigments, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    prepare()
