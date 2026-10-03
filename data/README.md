# Cone sensitivity data

`receptors/cone_fundamentals.csv` contains the 390–780 nm subset of the Stockman & Sharpe
2 Degree Cone Fundamentals (1 nm sampling, energy basis), in wavelength/L/M/S
column order. Plotting normalizes each curve to its own peak.

Source: Colour Science v0.4.6, `DATA_CMFS_LMS`, downloaded from
https://raw.githubusercontent.com/colour-science/colour/v0.4.6/colour/colorimetry/datasets/cmfs.py
which attributes these data to Stockman & Sharpe (2000), via CVRL:
http://www.cvrl.org/cones.htm .

Reference: Stockman, A. & Sharpe, L. T. (2000), “The spectral sensitivities of the
middle- and long-wavelength-sensitive cones derived from measurements in
observers of known genotype”, Vision Research 40, 1711–1737.

These are reference sensitivity data, not measurements of the user's eyes.

## Pigment spectra and provenance

Each CSV in `pigments/` contains one pigment: metadata comments followed by
`wavelength,value` samples. The bundled numerical values are unchanged from the legacy archive. Historical
digitization inputs mentioned below remain in the local ignored `legacy/data/sources/`
archive; they are not required for this build or distributed with the new page.

- **Indigo:** indigo-dyed cotton, Awa natural indigo / fermentation, sample No. 1
  (open circles) in Figure 3a of Kawahito, M. & Yasukawa, R. (2009),
  *Characteristics of Color Produced by Awa Natural Indigo and Synthetic Indigo*,
  Materials 2, 661–673. [Paper](https://doi.org/10.3390/ma2020661),
  [open-access text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5445713/),
  [figure](https://cdn.ncbi.nlm.nih.gov/pmc/blobs/0335/5445713/a2c5cad64c40/materials-02-00661-g003.jpg).
  **Approximately digitized, not an original numerical data export.**
  `sources/indigo_cotton_kawahito_2009.csv` records manual readings of the open-circle
  curve at 10 nm intervals, 400–700 nm, rounded to 0.1 percentage point.
  The reference figure is archived alongside it (CC BY 3.0, authors, 2009).
  Axis calibration in the 740×424 image: 400 nm ≈ x59, 700 nm ≈ x344;
  0% ≈ y312 and 9% ≈ y10. Read the open-circle centers, not the filled-circle
  or square series. Digitization precision is roughly 0.1–0.2 percentage point.
  Divide percentages by 100; do not normalize the maximum or brighten the color.
  Hold the 400/700 nm endpoints to 390/780 nm respectively because the figure
  does not cover those tails. This is a dark blue dyed-cotton example, not a
  specific brand of jeans, a universal denim shade or isolated-molecule reflectance.
- **Anthocyanin, chlorophyll and carotenoids:** solid PROSPECT-D specific
  absorption curves in Figure 8 of Féret, J.-B., Gitelson, A. A., Noble, S. D.
  & Jacquemoud, S. (2017), *PROSPECT-D: Towards modeling leaf optical properties
  through a complete lifecycle*, Remote Sensing of Environment 193, 204–215.
  [Paper](https://doi.org/10.1016/j.rse.2017.03.004).
  **Approximately manually digitized from the user-supplied figure, not original
  numerical model coefficients or new laboratory measurements.** The supplied
  image is archived as `sources/feret_2017_figure8.png`. The CSV
  `sources/feret_2017_figure8_digitized.csv` retains wavelength, traced pixel
  coordinates, and specific absorption in cm²/µg before any normalization.
  In the 1096×834 image, x=145/1014 maps to 400/750 nm and y=710/62 to
  0/0.3 cm²/µg. Trace the solid-line center at 10 nm intervals with extra
  points around sharp features, excluding dashed comparisons and shaded bands.
  Absorption = (710 − y) × 0.3/648; one vertical pixel is about 0.000463 cm²/µg.
  Readings are approximate to a few pixels; stored decimals are not measurement
  precision. Curves indistinguishable from the baseline are recorded as zero.
  The 400 nm values are held to 390 nm and the zero 750 nm values to 780 nm;
  these unplotted tails are assumptions. Chlorophyll represents the figure's
  chlorophyll pool, not the previous isolated chlorophyll-a solvent sample.
  The legacy data preparation divided each curve by its own maximum to obtain the chosen peak
  one-way absorbance of 1. This uses the absorption shape, not the absolute
  coefficient as dimensionless absorbance, and does not implement PROSPECT-D
  leaf radiative transfer or assume equal pigment mass across the three curves.

Previous Peters–Noble, PhotochemCAD, CHSOS and PROSPECT-D source files are
retained as historical inputs and are not read by the preparation script.
Source attribution and digitization notes are also shown beside the buttons.

### From absorption to reflection

For absorbance inputs, assume an absorbing, non-scattering layer over a perfect
white backing, with no interface losses. Light passes through the layer twice:
`R(λ) = 10^(-2 A(λ))`. Peak one-way absorbance 1 is an explicit chosen layer
strength, not the concentration of the original measurements. Reflection is
therefore **modeled** for anthocyanin, chlorophyll and carotenoids, **digitized from measured reflectance** for indigo.
This does not simulate full paint scattering, leaf structure, fluorescence or
pH-dependent transformations. Do not interpret absorption as `1 - reflectance`.

### Adding or updating a pigment

Add a UTF-8 `.csv` file anywhere under `data/pigments/`, including a nested
folder. `python make_html.py` discovers every CSV recursively at build time
(case-insensitive extension), in alphabetical relative-path order. The first
file is the initially selected pigment. Filenames are otherwise unrestricted.
There is no registry to update and no code or translation edits are required.

Use this format (the values below are an illustrative gray reflector):

```csv
# id: my_pigment
# name: My pigment
# kind: reflectance
# source: My measurements, sample 1
# source_url: https://example.org/my-measurements
# note: Measured on a white backing; wavelengths in nm.
wavelength,value
390,0.5
780,0.5
```

Replace the example source and values with your own. Required metadata:

| Key | Meaning |
| --- | --- |
| `id` | Unique across all CSV files; lowercase letters, digits, hyphens or underscores |
| `name` | Display name used by the selector and response readout |
| `kind` | `reflectance` or `absorbance` |
| `source` | Plain-text attribution shown below the selector |
| `source_url` | Absolute HTTP or HTTPS link to the source |

`note` is optional and displayed below the selector. Additional metadata such
as `solvent`, `concentration` or `license` is preserved in the embedded pigment
record but not displayed automatically. Add information visitors need to `note`.
Metadata values are plain text, one line each; colons and commas within values
are allowed. Duplicate keys and empty metadata values are errors. Keep all
`# key: value` lines before the CSV header. Blank lines are allowed. Standard
CSV quoting is supported for sample fields.

The columns must be exactly `wavelength,value`. Supply at least two finite
samples with strictly increasing wavelengths spanning 390–780 nm. Wavelengths
are in nanometers; values are dimensionless. Reflectance is a fraction in [0,1],
not a percentage. Absorbance is nonnegative base-10, one-way absorbance. There
is no automatic peak normalization: supply the intended layer strength.
Values are linearly interpolated before absorbance is converted to reflection.
Document measurement conditions, any endpoint extensions, and transformations.

Invalid files and duplicate IDs stop the build with a filename in the error.
An empty pigments folder is also an error. Rebuild and commit `index.html` to
update GitHub Pages; CSV discovery happens in Python, while the published page
uses embedded data and needs no directory listing, fetch, or server.

## Spectrum to screen color

`colorimetry/cie_xyz_1931_2deg.csv` contains the 390–780 nm CIE 1931 2° XYZ color-matching
functions at 1 nm. `spectra/d65_emission_colour_science_0.4.6.csv` contains D65 at 5 nm, linearly interpolated to
1 nm during the build. Both were extracted from the literal tables in Colour
Science **v0.4.6**:
[observer data](https://raw.githubusercontent.com/colour-science/colour/v0.4.6/colour/colorimetry/datasets/cmfs.py),
[illuminant data](https://raw.githubusercontent.com/colour-science/colour/v0.4.6/colour/colorimetry/datasets/illuminants/sds.py).
Official CIE dataset descriptions:
[1931 observer](https://www.cie.co.at/datatable/cie-1931-colour-matching-functions-2-degree-observer),
[D65](https://www.cie.co.at/datatable/cie-standard-illuminant-d65).

For each selection, form reflected spectral power `E(λ) R(λ)` with the selected illuminant `E`.
Trapezoidal integrals against XYZ matching functions are normalized by
`∫ E(λ) ȳ(λ) dλ` (perfect white Y=1). Convert XYZ to linear sRGB using the
[W3C matrix](https://www.w3.org/TR/css-color-4/#color-conversion-code), clip to
[0,1], and apply the sRGB transfer function. No per-pigment brightness or maximum
normalization is applied. Out-of-gamut colors are clipped; 390–780 nm truncation
can shift neutral gray by about one 8-bit code value.

Cone bars independently integrate `E R C` for each Stockman–Sharpe cone `C`,
divided by `∫ E C dλ`. Thus a perfect white reflector is 100% in every cone.
The cone basis and CIE 1931 XYZ observer are separate published approximations;
the square is not synthesized by treating the S/M/L bars as RGB channels.


## Incident-light choices

`source/illuminants.py` constructs four spectra on the 1 nm grid:

- **Full white:** constant power per nanometer (equal-energy illuminant).
- **D65:** the bundled CIE daylight reference, unchanged in spectral shape.
- **Tube light (FL2):** `spectra/fl2_emission_cie_2018.csv` contains the CIE FL2
  fluorescent reference, including phosphor emission and mercury lines. Extracted
  column FL2 (third column) and wavelengths 390–780 nm from
  [CIE 2018 fluorescent spectra, 1 nm](https://doi.org/10.25039/CIE.DS.54hy6srn).
  Original download: https://files.cie.co.at/Publications-datasets/CIE_illum_FLs_1nm.csv
  (MD5 verified: `77df774b47c2de724211d5f26592759e`). Values are unchanged in the
  CSV; the build scales them to equal white-reflector luminance. This reference
  represents a typical fluorescent tube, not every tube or a particular product.
  Attribution: International Commission on Illumination (CIE), Vienna, 2018,
  CIE 015:2018 tables 10.1–10.3. This extracted dataset is licensed under
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), as is the
  embedded normalized FL2 data; it is not covered by the project's code license.
- **Incandescent bulb:** a 2856 K blackbody approximation using
  `B_lambda ∝ lambda^-5 / (exp(0.01438776877 / (lambda*T)) - 1)` with lambda in
  meters. It does not model wavelength-dependent tungsten emissivity.

Each spectrum is multiplied by a constant so its integral against the CIE y
function equals that of the original D65 reference. Thus sources have equal
white-reflector luminance over 390–780 nm, not equal electrical power. Cone
percentages use white under the currently selected source. XYZ uses that same
source's white-Y denominator; conversion to the sRGB display does not adapt the
white point, so the lamp's color cast remains visible. Display clipping can
limit saturated colors.

## Lighter indigo example

`pigments/indigo_light.csv` uses multiplicative reflectance scaling:
`R_light(lambda) = 5 × R_indigo(lambda)`, with no added white component.
The original spectrum is untouched. The scaled reflectance spans 0.125–0.4,
so no clipping is needed. Scaling preserves spectral shape and XYZ chromaticity
before display gamut clipping; outgoing light, cone responses and XYZ all grow
fivefold under a fixed lamp. Encoded sRGB channel values do not grow fivefold
because of the nonlinear transfer curve. This is an illustrative brightness
change, not an independently measured fabric or a dye-concentration model.

Denim commonly includes dyed warp and undyed filling yarns, while ring dyeing
leaves pale cores. Abrasion and finishing reveal more pale cotton. See
[CottonWorks denim basics](https://cottonworks.com/learning-hub/denim/denim-basics/)
and [finishing](https://cottonworks.com/learning-hub/denim/denim-finishing/).
