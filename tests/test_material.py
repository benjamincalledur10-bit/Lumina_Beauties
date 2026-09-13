import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from material import normals, periodic, resize_wrap, linear, srgb


class MaterialTests(unittest.TestCase):
    def test_flat_normal(self):
        n = normals(np.ones((64,64)))
        np.testing.assert_allclose(n, np.broadcast_to([0,0,1], n.shape))

    def test_raised_feature_points_outward(self):
        h = np.zeros((32,32))
        h[16,16] = .1
        n = normals(h)
        self.assertLess(n[16,15,0], 0)  # left slope points left
        self.assertGreater(n[16,17,0], 0)
        self.assertLess(n[15,16,1], 0)  # top slope points up in DX coordinates
        self.assertGreater(n[17,16,1], 0)

    def test_wrap_filter_commutes_with_tile_shift(self):
        a = np.random.default_rng(4).random((64,64))
        np.testing.assert_allclose(resize_wrap(np.roll(a,8,0),32), np.roll(resize_wrap(a,32),4,0), atol=1e-6)

    def test_periodic_correction_and_color_roundtrip(self):
        a = np.tile(np.linspace(0,1,64), (64,1))
        p = periodic(a)
        self.assertLess(abs(p[:,0]-p[:,-1]).mean(), .02)
        np.testing.assert_allclose(srgb(linear(a)), a, atol=1e-7)


if __name__ == '__main__':
    unittest.main()
