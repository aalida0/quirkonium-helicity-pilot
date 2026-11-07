"""Only verifies ideal circular-moment variance and example event counts."""
import math
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from ideal_a1_statistical_gate import moment_cost,point

class TestIdealA1Gate(unittest.TestCase):
    def test_variance_formula_special_cases(self):
        self.assertEqual(moment_cost(0.1,0,5),4975)  # ceil(25*(2-0.01)/0.01)
        self.assertEqual(moment_cost(0.,.1,3),math.inf)
        with self.assertRaises(ValueError):
            moment_cost(.1,0,-1)

    def test_three_sigma_example_benchmark(self):
        p=point(500.,3.)
        self.assertLess(p["a1"],0.)
        self.assertAlmostEqual(p["a1"],-.120305,places=5)
        self.assertGreater(p["ideal_selected_N_for_3sigma_nonzero_a1"],1200)
        self.assertLess(p["ideal_selected_N_for_3sigma_nonzero_a1"],1300)
        self.assertGreater(p["ideal_selected_N_for_5sigma_nonzero_a1"],3400)
        self.assertLess(p["ideal_selected_N_for_5sigma_nonzero_a1"],3600)

if __name__=="__main__":
    unittest.main()
