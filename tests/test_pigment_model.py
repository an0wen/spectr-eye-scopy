import json
import shutil
import subprocess
import unittest
from pathlib import Path
from pigment_model import (integrate, load_pigments, pigment_signal, pigment_reflectance,
                           spectrum_rgb, color_matching_data, XYZ_TO_RGB, validate_pigment)
from spectral_model import cone_sensitivities


def sample(kind, values):
    return dict(id='test', kind=kind, wavelength=[390, 780], values=values)


class PigmentModelTests(unittest.TestCase):
    def test_irregular_trapezoids(self):
        self.assertAlmostEqual(integrate([0, 1, 3], [0, 1, 3]), 4.5)

    def test_neutral_reflectors(self):
        for reflectance in (0, .1, .5, 1):
            reflected, responses = pigment_signal(sample('reflectance', [reflectance]*2))
            for response in responses:
                self.assertAlmostEqual(response, reflectance)
            rgb = spectrum_rgb(reflected)
            self.assertLessEqual(max(rgb)-min(rgb), 1)
        self.assertEqual(spectrum_rgb([0]*391), (0,0,0))
        self.assertEqual(spectrum_rgb([1]*391), (255,255,255))
        # Truncating the observer to 390–780 nm leaves a sub-code-value white error.
        self.assertTrue(all(abs(v-188) <= 1 for v in spectrum_rgb([.5]*391)))

    def test_two_pass_absorption_and_interpolation(self):
        reflected, responses = pigment_signal(sample('absorbance', [1,1]))
        for response in responses:
            self.assertAlmostEqual(response, .01)
        ramp = pigment_reflectance(sample('absorbance', [0,2]))
        self.assertAlmostEqual(ramp[195], .01)

    def test_measured_reflectance_is_not_peak_normalized(self):
        pigment = next(p for p in load_pigments() if p['id']=='indigo')
        self.assertEqual(pigment['kind'], 'reflectance')
        self.assertLess(max(pigment_reflectance(pigment)), .5)

    def test_invalid_spectra(self):
        for pigment in [sample('reflectance', [-.1,1]), sample('reflectance', [0,1.1]),
                        sample('absorbance', [0,float('nan')]), sample('unknown',[0,1]),
                        dict(id='test',kind='reflectance', wavelength=[500,400],values=[0,1])]:
            with self.assertRaises(ValueError):
                validate_pigment(pigment)

    def test_reference_grid_and_pigments(self):
        data = color_matching_data()
        self.assertEqual(data['wavelength'],cone_sensitivities()['wavelength'])
        self.assertEqual(len(data['illuminant']),391)
        colors=[]
        for pigment in load_pigments():
            r, signals = pigment_signal(pigment)
            self.assertTrue(all(0 <= v <= 1 for v in signals+r))
            colors.append(spectrum_rgb(r))
        self.assertEqual(len(set(colors)),4)

    @unittest.skipUnless(shutil.which('node'), 'Node required for browser calculation parity')
    def test_browser_python_parity(self):
        pigments = load_pigments() + [sample('reflectance',[0,0]),sample('reflectance',[1,1]),sample('absorbance',[0,2])]
        payload=dict(pigments=pigments,cones=cone_sensitivities(),color=dict(color_matching_data(),xyz_to_rgb=XYZ_TO_RGB))
        script = "const m=require('./pigments.js');const p=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(p.pigments.map(s=>m.calculate(s,p.cones,p.color))));"
        result=subprocess.run(['node','-e',script],input=json.dumps(payload),text=True,capture_output=True,check=True,cwd=Path(__file__).resolve().parents[1])
        for pigment,actual in zip(pigments,json.loads(result.stdout)):
            reflected, responses=pigment_signal(pigment)
            self.assertEqual(list(spectrum_rgb(reflected)),actual['rgb'])
            for expected, value in zip(responses,actual['values']):
                self.assertAlmostEqual(expected*100,value,places=10)
            for expected, value in zip(reflected,actual['reflected']):
                self.assertAlmostEqual(expected,value,places=12)
