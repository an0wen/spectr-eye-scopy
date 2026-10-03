const decode = v => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
const encode = v => v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055;
const rgb = [red.value, green.value, blue.value];
const linear = rgb.map(v => decode(v / 255) * luminosity.value / 100);
const components = pixel_basis.map((basis, i) => basis.map(y => y * linear[i]));
['red', 'green', 'blue'].forEach((channel, i) => { spectrum_source.data[channel] = components[i]; });
spectrum_source.data.total = components[0].map((_, j) => components.reduce((sum, ys) => sum + ys[j], 0));
spectrum_source.change.emit();
const total = spectrum_source.data.total;
spectrum_fill.data.ys = total.slice(0, -1).map((y, i) => [0, y, total[i + 1], 0]);
spectrum_fill.change.emit();
const values = matrix.map(row => 100 * row.reduce((sum, a, i) => sum + a * linear[i], 0)).reverse();
source.data.value = values;
source.data.label = values.map(v => `${v.toFixed(1)}%`);
source.change.emit();
const displayed = linear.map(v => Math.round(255 * encode(v)));
swatch.text = `<div role="img" aria-label="Color controlled by the four sliders"
    style="height:180px;border-radius:12px;background:rgb(${displayed.join(',')})"></div>
    <p style="text-align:center">RGB ${displayed.join(' · ')}</p>`;
readout.text = `Cone responses: S ${values[0].toFixed(1)}%, M ${values[1].toFixed(1)}%, L ${values[2].toFixed(1)}%.`;
