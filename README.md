# spectr-eye-scopy

An interactive Bokeh outreach experiment: mix RGB light, vary its intensity, and
compare approximate S, M and L cone responses. Includes a responsive layout,
original SVG eye illustration, color presets, and an explanation of the model.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
python -m http.server 8000 --directory dist
```

Open http://localhost:8000. `dist/index.html` is self-contained (including Bokeh
JavaScript); it can also be opened directly. Callbacks run in the browser and do
not require a Bokeh server. Presets restore luminosity to 100%.

## Deploy to Render

Create a **Static Site** from this repository, with:

- Build command: `pip install -r requirements.txt && python app.py`
- Publish directory: `dist`

Alternatively, use the included `render.yaml` Blueprint. No deployment has been
performed by this project setup.

## Color model

`color_model.py` provides `cone_activation(red, green, blue, luminosity=1)`
(return order **S, M, L**) and `display_rgb(...)`. RGB inputs are encoded sRGB
values from 0 to 255; luminosity is a linear-light multiplier from 0 to 1.

1. Decode the sRGB transfer function.
2. Multiply linear RGB by luminosity.
3. Transform linear sRGB to CIE XYZ (D65), then Hunt–Pointer–Estevez LMS.
4. Normalize each response against its own full-intensity sRGB white response.
5. Reverse LMS to SML for the displayed bars. Re-encode the dimmed linear RGB
   for the displayed square.

The normalized matrix is passed from Python into `callbacks.js`, keeping the
browser and Python model coefficients identical. Normalization is fixed, never
relative to the current maximum, so reducing light reduces every bar.

This is an educational estimate of relative cone excitation, not a spectral
reconstruction or a physiological firing-rate model. RGB cannot determine a
unique spectrum. Screen calibration, adaptation, rods and observer differences
are outside the model. The luminosity control is relative intensity, not an
absolute photometric measurement. Bar colors identify cone types, not separate
red/green/blue receptors.

Sources: [W3C sRGB conversions](https://www.w3.org/TR/css-color-4/#color-conversion-code)
and [Hunt–Pointer–Estevez matrix](https://www.colour-science.org/api/0.3.4/html/_modules/colour/appearance/hunt.html).

## Edit and verify

- `templates/index.html`: page layout, styling and eye illustration.
- `app.py`: Bokeh sliders, plot and standalone build.
- `callbacks.js`: live color and response updates.
- `color_model.py`: reusable conversion functions.

```sh
python -m unittest discover -s tests -v
python app.py
```

## Spectral panels

The left panel shows a **hypothetical** RGB pixel spectrum, with Gaussian bands
centered at 625, 535 and 460 nm (standard deviations 18, 22 and 16 nm).
`pixel_spectrum` in `spectral_model.py` scales these bands by decoded linear RGB
and luminosity; it does not renormalize on slider changes. Zero light gives a
flat zero spectrum. Real display emission spectra depend on the display; these
curves are not calibrated to reproduce the exact sRGB primaries.

The right panel shows published Stockman–Sharpe 2° cone sensitivity data, each
normalized to its own peak. See `data/README.md` for provenance. The new plots
are teaching illustrations; response bars still use the original HPE matrix,
not an integral of the hypothetical emission and Stockman–Sharpe curves.

## Manage translations

The language selector below the header supports English, French, and Spanish.
English is the default; a visitor's selection is saved in their browser when
local storage is available. Switching languages preserves the current light
settings. The brand name and “An experiment in seeing” stay in English.

Edit the plain-text values in these UTF-8 JSON files:

- `translations/en.json`: English and the reference list of translation keys.
- `translations/fr.json`: French.
- `translations/es.json`: Spanish.

For example, change `"heading"` to edit the main headline, `"intro"` for the
introduction, and `"model_*"` entries for the model explanation. Keep keys the
same across every file. Keep `{s}`, `{m}`, and `{l}` in `response_readout`:
the app substitutes the current cone percentages. Use plain text, not HTML.
Scientific symbols and names (S/M/L, sRGB, nm, Stockman–Sharpe) remain unchanged.

Rebuild after editing:

```sh
python app.py
```

Refresh the local preview, or redeploy the rebuilt `dist/index.html`. All
translations are embedded in that standalone file; no translation API or
network request is needed. The build rejects missing/extra keys and empty values.

To add a language, copy `translations/en.json` to a language-code file such as
`translations/de.json`, translate every value, and add an option to the
`#language` selector in `templates/index.html`, for example
`<option value="de" lang="de">Deutsch</option>`. Rebuild and check the page,
charts, controls, and model explanation in that language.

For new UI text, add the same key to every catalog and use
`data-i18n="your_key"` on its text element (with an English Jinja fallback like
`{{ copy["your_key"] | e }}`). Use `data-i18n-aria` for accessible labels.
`localization.js` handles switching, number formatting, and Bokeh labels;
`callbacks.js` refreshes localized readouts when light settings change.
