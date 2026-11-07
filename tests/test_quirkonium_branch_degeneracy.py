"""Scoped mathematical, not physical-viability, signed interference proof."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from quirkonium_branch_degeneracy import (compare_branches,
    find_low_branch,signal_count_for_sign_discrimination)

class BranchDegeneracyTest(unittest.TestCase):
    def test_two_branches_match_rates_and_f00_flip_a1(self):
        for mass in (250.,400.,500.,1000.,2000.):
            with self.subTest(mass=mass):
                result=compare_branches(mass,3.)
                self.assertEqual(result["mathematical_two_branch_gate"],"PASS")
                self.assertLess(result["low_branch"]["tanbeta"],1.)
                self.assertGreater(result["high_branch"]["tanbeta"],1.)
                self.assertLess(result["f00_abs_diff"],1e-10)
                self.assertLess(result["BR_WZ_abs_diff"],1e-10)
                self.assertLess(abs(result["a1_signed_sum"]),1e-10)
                self.assertEqual(result["physical_both_branches_allowed"],"UNKNOWN")

    def test_500_geV_resonant_benchmark(self):
        p=compare_branches(500.,3.)
        self.assertAlmostEqual(p["low_branch"]["tanbeta"],
                               .394724021524,places=9)
        self.assertAlmostEqual(p["high_branch"]["f00"],.90928144813,places=7)
        self.assertAlmostEqual(p["high_branch"]["branch_wz_two_channels"],
                               .75308164527,places=7)
        self.assertAlmostEqual(p["low_branch"]["a1"],+.12030511054,places=6)
        self.assertAlmostEqual(p["high_branch"]["a1"],-.12030511054,places=6)
        n=signal_count_for_sign_discrimination(
            p["high_branch"]["a1"],p["high_branch"]["a2"],5.)
        self.assertGreater(n,840)
        self.assertLess(n,900)

    def test_invalid_interval_refused(self):
        with self.assertRaises(ValueError):
            find_low_branch(500.,3.,low=1.1)

if __name__=="__main__":
    unittest.main()
