"""Test the actual browser math with physical invariants and callback updates."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from source.pigments import load_data
from source.pigment_data import load_pigments, read_pigment

ROOT = Path(__file__).resolve().parents[1]


class PigmentTests(unittest.TestCase):
    def test_browser_math_and_callbacks(self):
        pigments, reference = load_data()
        script = r'''
const assert = require('node:assert/strict');
const fs = require('node:fs');
const math = require('./source/pigment_math.js');
const {pigments, reference, copy} = JSON.parse(fs.readFileSync(0, 'utf8'));
const close = (a, b) => assert.ok(Math.abs(a - b) < 1e-9, `${a} != ${b}`);
close(math.integrate([0, 1, 3], [0, 1, 3]), 4.5);
function sample(kind, values) { return {kind, wavelength: [390, 780], values}; }
for (const r of [0, .1, .5, 1]) {
    const actual = math.calculate(sample('reflectance', [r, r]), reference);
    actual.responses.forEach(v => close(v, 100*r));
    assert.ok(Math.max(...actual.rgb) - Math.min(...actual.rgb) <= 1);
    if (r === 0) assert.deepEqual(actual.rgb, [0, 0, 0]);
    if (r === 1) assert.deepEqual(actual.rgb, [255, 255, 255]);
    if (r === .5) actual.rgb.forEach(v => assert.ok(Math.abs(v-188) <= 1));
}
math.calculate(sample('absorbance', [1, 1]), reference).responses.forEach(v => close(v, 1));
close(math.reflectance(sample('absorbance', [0, 2]), [585])[0], .01);
const results = pigments.map(p => math.calculate(p, reference));
assert.equal(new Set(results.map(r => r.rgb.join())).size, pigments.length);
results.forEach(r => {
    assert.ok(r.reflected.every(v => v >= 0 && v <= 1));
    assert.ok(r.responses.every(v => v >= 0 && v <= 100));
});
assert.ok(Math.max(...results[pigments.findIndex(p => p.id === 'indigo')].reflected) < .1);
// Execute the exact CustomJS callback with simple model stand-ins, in both
// selection directions. This catches wrong fields and stale output updates.
const callback = new Function('pigments', 'reference', 'selection', 'spectrum',
    'responses', 'swatch', 'note', 'readout', 'copy', 'light_selection', 'light_note', 'light_range',
    fs.readFileSync('source/pigment_math.js', 'utf8') + '\n' +
    fs.readFileSync('source/pigment_callback.js', 'utf8'));
const spectrum = {}, responses = {}, swatch = {}, note = {}, readout = {};
for (const active of [...pigments.keys(), 0]) {
    callback(pigments, reference, {active}, spectrum, responses, swatch, note, readout, copy, {active: 1}, {}, {});
    assert.deepEqual(responses.data.value, results[active].responses);
    assert.deepEqual(spectrum.data.light, results[active].light);
    assert.ok(swatch.text.includes(results[active].rgb.join(',')));
    assert.ok(note.text.includes(pigments[active].source_url));
    assert.ok(readout.text.includes(pigments[active].name));
}
// A contributed pigment has no translation key and can contain literal markup.
const custom = {...pigments[0], id: 'custom', name: '<Custom & pigment>',
    note: '<script>example</script>', source: 'A & B', source_url: 'https://example.org/?a=1&b=2'};
callback([custom], reference, {active: 0}, spectrum, responses, swatch, note, readout, copy, {active: 1}, {}, {});
assert.ok(readout.text.includes('&lt;Custom &amp; pigment&gt;'));
assert.ok(note.text.includes('&lt;script&gt;example&lt;/script&gt;'));
assert.ok(note.text.includes('https://example.org/?a=1&amp;b=2'));
// Every pigment/light combination updates the spectrum and outputs together.
for (const [lampIndex, lamp] of reference.illuminants.entries()) {
    const white = math.calculate(sample('reflectance', [1, 1]), reference, lamp.power);
    close(white.xyz[1], 1);
    white.responses.forEach(v => close(v, 100));
    math.calculate(sample('reflectance', [.5, .5]), reference, lamp.power)
        .responses.forEach(v => close(v, 50));
    assert.ok(lamp.power.every(v => Number.isFinite(v) && v >= 0));
    const area = math.integrate(reference.wavelength, lamp.power.map((v,i) => v*reference.observer.y[i]));
    const d65Area = math.integrate(reference.wavelength, reference.daylight.map((v,i) => v*reference.observer.y[i]));
    close(area, d65Area);
    for (const active of pigments.keys()) {
        const lightNote = {}, range = {};
        callback(pigments, reference, {active}, spectrum, responses, swatch, note, readout,
                 copy, {active: lampIndex}, lightNote, range);
        const expected = math.calculate(pigments[active], reference, lamp.power);
        assert.deepEqual(responses.data.value, expected.responses);
        assert.deepEqual(spectrum.data.daylight, lamp.power);
        assert.deepEqual(spectrum.data.light, expected.light);
        assert.ok(swatch.text.includes(expected.rgb.join(',')));
        assert.ok(range.end > Math.max(...lamp.power));
        assert.ok(lightNote.text.length > 10);
    }
}
const dark = pigments.find(p => p.id === 'indigo');
const pale = pigments.find(p => p.id === 'indigo_light');
pale.values.forEach((v,i) => close(v, 5*dark.values[i]));
for (const lamp of reference.illuminants) {
    const a = math.calculate(dark, reference, lamp.power);
    const b = math.calculate(pale, reference, lamp.power);
    b.xyz.forEach((v,i) => close(v, 5*a.xyz[i]));
    b.responses.forEach((v,i) => close(v, 5*a.responses[i]));
}
const tube = reference.illuminants.find(p => p.id === 'tube');
assert.ok(tube);
assert.ok(!reference.illuminants.some(p => p.id === 'mercury'));
// Phosphor emission between Hg lines, as well as a strong blue mercury peak.
assert.ok(tube.power[500-390] > 0.01*Math.max(...tube.power));
assert.ok(tube.power[436-390] > tube.power[450-390]);
close(tube.power[500-390]/tube.power[450-390], 7.28/6.63);
const bulb = reference.illuminants.find(p => p.id === 'incandescent');
assert.ok(bulb.power.at(-1) > bulb.power[0]);
const warm = math.calculate(sample('reflectance', [1,1]), reference, bulb.power).rgb;
assert.ok(warm[0] > warm[2]);
console.log('Physical invariants and all pigment callback updates passed.');
'''
        result = subprocess.run(['node', '-e', script], cwd=ROOT, text=True,
                                input=json.dumps(dict(pigments=pigments, reference=reference,
                                    copy=json.loads((ROOT/'translations/en.json').read_text()))),
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)


    def test_csv_discovery_and_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            nested = directory / 'nested'
            nested.mkdir()
            example = (ROOT/'data/pigments/indigo.csv').read_text()
            (nested/'custom.CSV').write_text(example.replace('# id: indigo', '# id: custom')
                .replace('# name: Indigo', '# name: Custom pigment') + '\n')
            (directory/'a.csv').write_text(example)
            (directory/'ignored.txt').write_text('not a CSV')
            pigments = load_pigments(directory)
            self.assertEqual([p['id'] for p in pigments], ['indigo', 'custom'])
            self.assertEqual(pigments[1]['name'], 'Custom pigment')
            (directory/'duplicate.csv').write_text(example)
            with self.assertRaisesRegex(ValueError, 'duplicate.csv: duplicate pigment id'):
                load_pigments(directory)

    def test_csv_errors_identify_file(self):
        header = ('# id: sample\n# name: Sample\n# kind: reflectance\n'
                  '# source: My measurements\n# source_url: https://example.org/data\n')
        valid = header + 'wavelength,value\n390,0.1\n780,0.2\n'
        cases = [
            valid.replace('# name: Sample\n', ''),
            valid.replace('# id: sample', '# id: bad id'),
            valid.replace('# kind: reflectance', '# kind: unknown'),
            valid.replace('https://example.org/data', 'javascript:alert(1)'),
            valid.replace('wavelength,value', 'wavelength,power'),
            valid.replace('390,0.1', '390,nan'),
            valid.replace('390,0.1', '390,-0.1'),
            valid.replace('780,0.2', '780,1.2'),
            valid.replace('780,0.2', '390,0.2'),
            valid.replace('390,0.1', '400,0.1'),
            valid.replace('780,0.2', '780,0.2,extra'),
            valid.replace('780,0.2\n', ''),
            '# id: twice\n' + valid,
            '# malformed\n' + valid,
            '',
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'bad.csv'
            with self.assertRaisesRegex(ValueError, 'no pigment CSV'):
                load_pigments(folder)
            for content in cases:
                with self.subTest(content=content):
                    path.write_text(content)
                    with self.assertRaisesRegex(ValueError, 'bad.csv:'):
                        read_pigment(path)
            # Optional note and extra metadata; UTF-8 BOM and blank lines are supported.
            path.write_text('\ufeff# solvent: water\n\n' + valid)
            pigment = read_pigment(path)
            self.assertEqual(pigment['solvent'], 'water')
            self.assertEqual(pigment['note'], '')

    def test_standalone_build_wiring(self):
        from bokeh.models import CustomJS
        from bokeh.models import Div
        from source.pigments import build_panels
        text = json.loads((ROOT/'translations/en.json').read_text())
        panels = build_panels([Div(), Div(), Div()], text)
        callbacks = list(panels['pigments_1'].select(dict(type=CustomJS)))
        self.assertEqual(len(callbacks), 1)
        selection = callbacks[0].args['selection']
        self.assertIn('document_ready', selection.js_event_callbacks)
        self.assertIn('change:active', selection.js_property_callbacks)
        light_selection = callbacks[0].args['light_selection']
        self.assertEqual(len(light_selection.labels), 4)
        self.assertIn('change:active', light_selection.js_property_callbacks)
        children = panels['pigments_1'].children
        self.assertIs(children[3], light_selection)
        self.assertIs(children[8], selection)
        html = (ROOT/'index.html').read_text()
        self.assertNotIn('<script src=', html)
        self.assertNotIn('fetch(', callbacks[0].code)
        self.assertIn('href="#pigments"', html)


if __name__ == '__main__':
    unittest.main()
