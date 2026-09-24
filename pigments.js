// Pure numerical functions are shared by browser interactions and Node verification.
const pigmentMath = (() => {
  const integral = (x, y) => y.slice(1).reduce((sum, v, i) => sum + (x[i + 1] - x[i]) * (v + y[i]) / 2, 0);
  function reflectance(pigment, wavelengths) {
    let j = 0;
    const x = pigment.wavelength, a = pigment.values;
    return Array.from(wavelengths, nm => {
      while (j < x.length - 2 && nm > x[j + 1]) j++;
      const value = a[j] + (a[j + 1] - a[j]) * (nm - x[j]) / (x[j + 1] - x[j]);
      return pigment.kind === 'reflectance' ? value : 10 ** (-2 * value);
    });
  }
  function calculate(pigment, cones, color) {
    const x = color.wavelength;
    const reflected = reflectance(pigment, x);
    const light = reflected.map((r, i) => r * color.illuminant[i]);
    const values = ['S', 'M', 'L'].map(k => 100 * integral(x, light.map((e, i) => e * cones[k][i])) /
      integral(x, Array.from(cones[k], (c, i) => c * color.illuminant[i])));
    const whiteY = integral(x, color.y.map((y, i) => y * color.illuminant[i]));
    const xyz = ['x', 'y', 'z'].map(k => integral(x, light.map((e, i) => e * color[k][i])) / whiteY);
    const rgb = color.xyz_to_rgb.map(row => {
      const linear = Math.max(0, Math.min(1, row.reduce((sum, a, i) => sum + a * xyz[i], 0)));
      const encoded = linear <= .0031308 ? 12.92 * linear : 1.055 * linear ** (1 / 2.4) - .055;
      return Math.round(255 * encoded);
    });
    return {reflected, values, rgb};
  }
  return {integral, reflectance, calculate};
})();
if (typeof module !== 'undefined') module.exports = pigmentMath;
if (typeof window !== 'undefined') window.initPigments = doc => {
  const cones = doc.get_model_by_name('cone_sensitivities').data;
  const spectrum = doc.get_model_by_name('pixel_spectrum');
  const fill = doc.get_model_by_name('spectrum_fill');
  const responses = doc.get_model_by_name('cone_responses');
  function select(pigment) {
    const {reflected, values, rgb} = pigmentMath.calculate(pigment, cones, pigmentColorData);
    spectrum.data.total = reflected;
    spectrum.change.emit();
    fill.data.ys = reflected.slice(0, -1).map((v, i) => [0, v, reflected[i + 1], 0]);
    fill.change.emit();
    responses.data.value = values;
    responses.change.emit();
    document.getElementById('swatch').style.backgroundColor = `rgb(${rgb.join(',')})`;
    document.getElementById('rgb-readout').textContent = `RGB ${rgb.join(' · ')}`;
    document.querySelectorAll('[data-pigment]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.pigment === pigment.id)));
    document.getElementById('pigment-selection-note').dataset.i18n = pigment.id + '_note';
    const sourceLink = document.getElementById('pigment-source');
    sourceLink.textContent = pigment.source;
    sourceLink.href = pigment.source_url;
    window.spectrI18n.apply(doc);
  }
  document.querySelectorAll('[data-pigment]').forEach(button => button.addEventListener('click', () => select(pigmentSpectra.find(p => p.id === button.dataset.pigment))));
  select(pigmentSpectra[0]);
};
