import unittest
from source.spectral_model import pixel_spectrum, cone_sensitivities


class SpectralModelTests(unittest.TestCase):
    def test_darkness(self):
        data = pixel_spectrum(255, 255, 255, 0)
        for name in ('red', 'green', 'blue', 'total'):
            self.assertTrue(all(v == 0 for v in data[name]))

    def test_intensity_and_additivity(self):
        full = pixel_spectrum(255, 160, 80)
        half = pixel_spectrum(255, 160, 80, .5)
        for i, value in enumerate(full['total']):
            self.assertAlmostEqual(half['total'][i], value / 2)
            self.assertAlmostEqual(value, sum(full[c][i] for c in ('red','green','blue')))

    def test_reference_sensitivity(self):
        data = cone_sensitivities()
        self.assertEqual(data['wavelength'], list(range(390, 781)))
        peaks = []
        for cone in ('S', 'M', 'L'):
            self.assertAlmostEqual(max(data[cone]), 1)
            self.assertTrue(all(0 <= v <= 1 for v in data[cone]))
            peaks.append(data['wavelength'][data[cone].index(1)])
        self.assertTrue(430 <= peaks[0] <= 450)
        self.assertTrue(530 <= peaks[1] <= 550)
        self.assertTrue(560 <= peaks[2] <= 580)
