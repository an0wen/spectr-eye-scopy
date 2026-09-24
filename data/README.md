# Cone sensitivity data

`cone_fundamentals.csv` contains the 390–780 nm subset of the Stockman & Sharpe
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

The Gaussian starter spectra have been replaced. `pigments.json` contains
sampled `values`, `wavelength` in nm, a `kind` (`reflectance` or `absorbance`),
and source metadata. Archived input data is in `sources/`.

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
  The build divides each curve by its own maximum to obtain the chosen peak
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

Use finite, strictly increasing wavelengths covering 390–780 nm, with equally
sized finite sample arrays. Reflectance must lie in [0,1]; absorbance is
nonnegative. Values are linearly interpolated before conversion to reflectance.
For measured reflectance, supply `kind: "reflectance"` to bypass the layer model.
Add an `id` and `id_note` entry in each translation catalog, plus `source` and
`source_url` in the data. Record measurement conditions and all transformations.
Buttons are generated automatically; RGB and S/M/L are calculated on selection.

`python scripts/prepare_pigments.py` reproduces the four bundled entries from
archived inputs, without downloading anything. Then `python app.py` builds both
pages. Future custom entries can be added directly to `pigments.json`; the
preparation script intentionally reconstructs only the four bundled entries.

## Spectrum to screen color

`cie_xyz_1931_2deg.csv` contains the 390–780 nm CIE 1931 2° XYZ color-matching
functions at 1 nm. `cie_d65.csv` contains D65 at 5 nm, linearly interpolated to
1 nm during the build. Both were extracted from the literal tables in Colour
Science **v0.4.6**:
[observer data](https://raw.githubusercontent.com/colour-science/colour/v0.4.6/colour/colorimetry/datasets/cmfs.py),
[illuminant data](https://raw.githubusercontent.com/colour-science/colour/v0.4.6/colour/colorimetry/datasets/illuminants/sds.py).
Official CIE dataset descriptions:
[1931 observer](https://www.cie.co.at/datatable/cie-1931-colour-matching-functions-2-degree-observer),
[D65](https://www.cie.co.at/datatable/cie-standard-illuminant-d65).

For each selection, form reflected spectral power `E(λ) R(λ)` with D65 `E`.
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
