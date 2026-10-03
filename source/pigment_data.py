"""Read one pigment per CSV; metadata is written as leading '# key: value' lines."""
import csv
import math
import re
from pathlib import Path
from urllib.parse import urlsplit

PIGMENT_DIRECTORY = Path(__file__).resolve().parents[1] / 'data/pigments'


def read_pigment(path):
    """Parse and validate a file, reporting its filename with any input error."""
    path = Path(path)
    try:
        metadata = {}
        with path.open(encoding='utf-8-sig', newline='') as file:
            # Only the leading block is metadata; the remaining lines are CSV.
            for line in file:
                if not line.strip():
                    continue
                if not line.lstrip().startswith('#'):
                    header = line
                    break
                key, separator, value = line.lstrip()[1:].partition(':')
                key, value = key.strip(), value.strip()
                if not separator or not key or not value:
                    raise ValueError('metadata must use # key: value with a nonempty value')
                if key in metadata:
                    raise ValueError(f'duplicate metadata key: {key}')
                metadata[key] = value
            else:
                raise ValueError('missing wavelength,value CSV header')
            required = {'id', 'name', 'kind', 'source', 'source_url'}
            missing = required - metadata.keys()
            if missing:
                raise ValueError(f"missing metadata: {', '.join(sorted(missing))}")
            if not re.fullmatch(r'[a-z0-9]+(?:[-_][a-z0-9]+)*', metadata['id']):
                raise ValueError('id must use lowercase letters, digits, hyphens or underscores')
            if metadata['kind'] not in ('absorbance', 'reflectance'):
                raise ValueError('kind must be absorbance or reflectance')
            url = urlsplit(metadata['source_url'])
            if url.scheme not in ('http', 'https') or not url.netloc:
                raise ValueError('source_url must be an absolute http(s) URL')
            reader = csv.reader([header, *file], strict=True)
            if next(reader) != ['wavelength', 'value']:
                raise ValueError('CSV columns must be wavelength,value')
            wavelengths, values = [], []
            for row in reader:
                if not row:
                    continue
                if len(row) != 2:
                    raise ValueError('each sample must have exactly two columns')
                wavelength, value = map(float, row)
                wavelengths.append(wavelength)
                values.append(value)
        if len(wavelengths) < 2:
            raise ValueError('at least two samples are required')
        if any(not math.isfinite(v) for v in wavelengths + values):
            raise ValueError('samples must be finite numbers')
        if any(b <= a for a, b in zip(wavelengths, wavelengths[1:])):
            raise ValueError('wavelengths must be strictly increasing')
        if wavelengths[0] > 390 or wavelengths[-1] < 780:
            raise ValueError('wavelengths must cover 390–780 nm')
        if min(values) < 0 or (metadata['kind'] == 'reflectance' and max(values) > 1):
            raise ValueError('reflectance must be in [0,1]; absorbance must be nonnegative')
        # Preserve additional metadata, but spectral arrays always come from CSV rows.
        return {**metadata, 'note': metadata.get('note', ''),
                'wavelength': wavelengths, 'values': values}
    except (ValueError, csv.Error, UnicodeError) as error:
        raise ValueError(f'{path}: {error}') from error


def load_pigments(directory=PIGMENT_DIRECTORY):
    """Discover all CSVs, including nested folders, in stable relative-path order."""
    directory = Path(directory)
    paths = sorted((p for p in directory.rglob('*') if p.is_file() and p.suffix.lower() == '.csv'),
                   key=lambda p: p.relative_to(directory).as_posix())
    if not paths:
        raise ValueError(f'{directory}: no pigment CSV files found')
    pigments, seen = [], {}
    for path in paths:
        pigment = read_pigment(path)
        if pigment['id'] in seen:
            raise ValueError(f"{path}: duplicate pigment id '{pigment['id']}' (also in {seen[pigment['id']]})")
        seen[pigment['id']] = path
        pigments.append(pigment)
    return pigments
