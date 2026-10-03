// Bokeh supplies the named arguments below. The pure math module is prepended
// by the build so this same code works in a standalone, offline HTML file.
// CSV metadata is plain text, so escape it before placing it in Div HTML.
const escapeHTML = value => String(value).replace(/[&<>"']/g, character =>
    ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[character]));
const illuminant = reference.illuminants[light_selection.active];
const result = pigmentMath.calculate(pigments[selection.active], reference, illuminant.power);
// Each lamp gets an axis range suited to its peaks; pigment changes keep it fixed.
light_range.end = Math.max(...illuminant.power) * 1.05;
light_note.text = `<p>${escapeHTML(copy['light_' + illuminant.id + '_note'])}</p>`;
const fillColumns = {xs: spectrum.data?.xs, color: spectrum.data?.color};
const ys = result.light.map((y, i) => i < result.light.length - 1 ? [0, y, result.light[i + 1], 0] : []);
spectrum.data = {...fillColumns, ys, wavelength: reference.wavelength, reflectance: result.reflected,
                 light: result.light, daylight: illuminant.power};
responses.data = {cone: ['S', 'M', 'L'], value: result.responses,
                  label: result.responses.map(v => `${v.toFixed(1)}%`),
                  color: ['#789fdb', '#7caa75', '#df735f']};
const selected = pigments[selection.active];
swatch.text = `<div role="img" aria-label="${escapeHTML(copy.pigment_swatch_description)}"
    style="height:180px;border-radius:12px;background:rgb(${result.rgb.join(',')})"></div>
    <p style="text-align:center">RGB ${result.rgb.join(' · ')}</p>`;
readout.text = `<p role="status" aria-live="polite">${escapeHTML(selected.name)} · ${escapeHTML(copy['light_' + illuminant.id])} · ` +
    result.responses.map((value, i) => `${['S', 'M', 'L'][i]} ${value.toFixed(1)}%`).join(' · ') + '</p>';
note.text = `<p>${escapeHTML(selected.note)}</p><p><a href="${escapeHTML(selected.source_url)}"
    target="_blank" rel="noopener noreferrer">${escapeHTML(selected.source)}</a></p>`;
