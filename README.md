# Spectr-eye-scopy

A small, static Bokeh website for exploring light and the eye. The pigments view includes five interactive pigments and four incident-light choices, spectral plots, cone responses,
and a calculated sRGB preview. The RGB screen view restores the legacy RGB and luminosity sliders, live swatch, illustrative emission spectrum, cone sensitivity curves, and white-normalized Hunt–Pointer–Estevez responses.

## Structure

```text
LICENSE
README.md
requirements.txt
make_html.py
index.html                         Generated website
translations/
    en.json                        Shared website text in English
data/
    receptors/
        cone_fundamentals.csv      Cone sensitivity reference table
    spectra/
        d65_emission_colour_science_0.4.6.csv
    images/                        Icons, molecules, and other graphics
source/
    interface.html                 Shared page shell
    interface.css                  Legacy interface styling
    navigation.js                  Switching between the two views
```

The existing `.gitignore` also remains at the root. `legacy/` is a local,
ignored archive, and is not required to build or use the new website.

Spectrum filenames follow `<pigment-or-light-source>_<type>_<source>.csv`,
where type can be `emission`, `transmission`, `reflection`, or another
appropriate quantity. Use descriptive column names and document units and
provenance when adding data.

## Build locally

Python builds the HTML; visitors only need a browser. From the project root,
reuse the existing environment without downloading anything:

```sh
legacy/venv/bin/python make_html.py
```

On a fresh checkout, use a Python environment with the dependencies installed:

```sh
python -m pip install -r requirements.txt
python make_html.py
```

Open `index.html` in a browser. Bokeh's JavaScript and CSS are embedded, so
there is no CDN dependency or Python server. The generated file is larger
than the source; edit the files in `source/`, `make_html.py`, or `translations/en.json`, then rebuild
instead of editing the HTML directly. The build works from any working directory.

Pigment interactions use Bokeh `CustomJS` callbacks in `source/`. All reference
data and JavaScript are embedded during the build. There are no runtime data
fetches, external scripts, Python callbacks, or server requirements.

Both views live in one HTML file: `index.html#screen` and
`index.html#pigments`. Navigation uses ordinary hash links, including browser
Back/Forward and direct links. No route rewrites or second HTML file are needed.
The shell uses HTML/CSS, with Bokeh widgets and plots in the pigment workspace. English is the only language available.

## GitHub Pages

Commit the new source files and generated `index.html`. In the repository's
Pages settings, deploy from the desired branch and its root directory.
Rebuild and commit `index.html` after source changes; GitHub Pages serves the
finished file and does not run Python. No build workflow is included.

The old tracked paths currently appear as deletions because their files were
moved into `legacy/`. Include those deletions in the fresh-start commit.
Ignoring `legacy/` keeps it out of future commits; it does not erase earlier
versions from Git history.

## Starter data provenance

Both CSV files were copied unchanged from `legacy/data/`, without downloads
or numerical transformations. Provenance below is retained from the legacy
documentation.

- `data/receptors/cone_fundamentals.csv`: Stockman–Sharpe 2° cone fundamentals,
  energy basis, sampled from 390 to 780 nm at 1 nm intervals. Columns are
  `wavelength` (nm), `L`, `M`, and `S` (relative sensitivity). Extracted from
  Colour Science v0.4.6, attributed to Stockman & Sharpe (2000) via CVRL.
  These are reference sensitivities, not measurements of a particular eye.
- `data/spectra/d65_emission_colour_science_0.4.6.csv`: CIE D65 relative
  spectral power from Colour Science v0.4.6. Columns are `wavelength` (nm)
  and `power` (relative units), sampled at 5 nm intervals over 390–780 nm.
  This is a reference daylight illuminant, not an absolute irradiance measurement.

The project retains its original MIT license in `LICENSE`.


## Pigments: where the code lives

- `source/pigment_math.js`: the numerical model, independent of the interface.
  Start here to understand the math. `interpolate` joins sampled points;
  `reflectance` converts absorbance to reflection when needed; `integrate`
  adds trapezoidal areas; `calculate` computes outgoing light, cone responses,
  XYZ and RGB; `encodeSRGB` converts linear intensity to an 8-bit display value.
- `source/pigment_callback.js`: calls the model when a pigment is selected,
  then updates plots, bars, color preview, accessible readout and attribution.
- `source/pigment_data.py`: recursively discovers pigment CSVs, reads metadata
  comments and validates spectra with filename-specific errors.
- `source/pigments.py`: loads reference data, resamples D65, creates Bokeh
  plots and controls, and connects the callback to selection and document load.
  Python runs only when building the file.
- `make_html.py`: combines both workspaces and embeds Bokeh and the models
  into the generated `index.html`.
- `source/interface.html` and `source/interface.css`: layout and responsive
  styling. `source/eye.svg` is the original legacy eye illustration.
- `translations/en.json`: shared interface labels and the on-page
  “Follow the calculation” explanation.
- `data/pigments/*.csv`: one pigment per file, with `# key: value` metadata
  (id, name, kind, source, source_url, optional note) and `wavelength,value` rows.
  Add a CSV anywhere under this folder and rebuild; no code or translation
  edits are needed. See `data/README.md` for a copyable example.
  `data/colorimetry/cie_xyz_1931_2deg.csv`: XYZ observer functions.
  See `data/README.md` for provenance and assumptions.

### The math, in order

For every wavelength λ from 390 to 780 nm:

1. Interpolate the reference samples onto the same 1 nm grid.
2. Find reflectance R(λ). Indigo supplies this directly; lighter indigo uses an
   explicit fivefold reflectance scaling. The absorption-based pigments
   supply one-way absorbance A: transmission is 10^(-A), so two passes through
   a layer over perfect white backing give R = 10^(-2A).
3. Multiply the selected incident light E by R to get outgoing light L = E × R.
4. For each S/M/L sensitivity C, compute
   `100 × integral(E × R × C) / integral(E × C)`.
   The denominator is a fixed perfect-white reference for that cone.
   A 50% reflector therefore gives 50% in all three cones. Plot sensitivities
   are peak-normalized for illustration; calculations use the original tables.
5. Independently integrate L against the CIE x/y/z functions. Divide all three
   by `integral(E × y)` so white has Y = 1. Multiply XYZ by the sRGB matrix,
   clip to the display gamut, and apply the sRGB encoding curve.
   The cone bars are not used as RGB channels.

Every integral uses trapezoids: add
`(next wavelength - wavelength) × (current height + next height) / 2`.
The reflectance plot and outgoing-light plot are distinct: the second includes
the selected lamp’s wavelength dependence. Its vertical axis adjusts to each
lamp’s peaks, staying fixed when only the pigment changes. Reflectance stays 0–1.
All lamps are normalized to equal white-reflector luminance. No chromatic
adaptation is applied to the preview, so warm light retains a warm cast.

### Verify

```sh
legacy/venv/bin/python make_html.py
legacy/venv/bin/python -m unittest discover -s tests -v
```

On a fresh checkout use your installed Python environment instead. Tests require
Node.js to execute the exact JavaScript model and selection callback. They check
black/white/gray reflectors, two-pass absorption, irregular-grid integration,
all pigment selections and standalone callback wiring. Browser layout should
also be checked at desktop and mobile widths, including direct `#pigments`
loading and navigation from the screen view.


Incident spectra are generated in `source/illuminants.py`: equal-energy white,
tabulated D65, the CIE FL2 fluorescent-tube reference, and a 2856 K Planck
blackbody for incandescent light. The same callback handles both selectors.
`data/pigments/indigo_light.csv` adds the modeled lighter fabric; its header
records the multiplication factor (5), with no added white component. The page includes a jeans explanation and sources.
