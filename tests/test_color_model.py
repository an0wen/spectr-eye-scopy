import unittest
from color_model import cone_activation, display_rgb


class ColorModelTests(unittest.TestCase):
    def test_darkness_overrides_all_channels(self):
        for rgb in [(255, 255, 255), (255, 0, 80), (0, 0, 0)]:
            self.assertEqual(cone_activation(*rgb, 0), (0, 0, 0))
            self.assertEqual(display_rgb(*rgb, 0), (0, 0, 0))

    def test_white_reference_and_linear_intensity(self):
        for response in cone_activation(255, 255, 255):
            self.assertAlmostEqual(response, 1)
        full = cone_activation(40, 170, 230)
        half = cone_activation(40, 170, 230, .5)
        for a, b in zip(full, half):
            self.assertAlmostEqual(a / 2, b)
        self.assertEqual(display_rgb(255, 255, 255, .5), (188, 188, 188))

    def test_primary_overlap_and_dominance(self):
        red = cone_activation(255, 0, 0)
        blue = cone_activation(0, 0, 255)
        self.assertTrue(all(v > 0 for v in red))
        self.assertGreater(red[2], red[1])
        self.assertGreater(blue[0], blue[1])
        self.assertGreater(blue[0], blue[2])

    def test_display_identity(self):
        for value in range(256):
            self.assertEqual(display_rgb(value, value, value), (value,) * 3)

    def test_reject_invalid_inputs(self):
        for args in [(-1, 0, 0, 1), (256, 0, 0, 1), (0, 0, 0, 2),
                     (0, 0, 0, float('nan'))]:
            with self.assertRaises(ValueError):
                cone_activation(*args)


if __name__ == '__main__':
    unittest.main()
