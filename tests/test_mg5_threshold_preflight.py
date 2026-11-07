"""Test the on-shell threshold PS and safe card editing without MadGraph."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"src"))
from mg5_threshold_preflight import momenta,validate_ps,parse_card,replace_card,reference
from mg5_evaluate_threshold import patch_readps
from scalar_threshold_amplitudes import Setup,MW,splitting

class ThresholdPreflightTest(unittest.TestCase):
    def test_threshold_kinematics(self):
        for M in (250.,500.,1000.):
            for tb in (1.,3.,10.):
                for mode in ("Z","gamma"):
                    b=Setup(M,splitting(M,tb),mode)
                    ps=momenta(b)
                    validate_ps(ps,(b.mu,b.md,MW,b.mv))
                    self.assertAlmostEqual(sum(ps[0][i]+ps[1][i]-
                                                ps[2][i]-ps[3][i]
                                                for i in range(4)),0.,places=10)
    def test_matched_slha_values(self):
        card=("BLOCK SMINPUTS\n 1 1.27e2 # aewm1\n 2 1.16e-5 # GF\n"
              "BLOCK MASS\n 1000002 1200 # ul\n 1000001 1210 # dl\n"
              " 23 91.2 # Z\n 24 80.4 # W\n"
              "DECAY 24 2.0 # Wwidth\nBLOCK MINPAR\n 3 2.0 # tanbeta\n")
        updates={("MASS",1000002):250.,("MASS",1000001):250.,
                 ("SMINPUTS",1):132.4,("SMINPUTS",2):1.164e-5,
                 ("DECAY",24):0.,("MINPAR",3):1.}
        new,found=replace_card(card,updates)
        self.assertEqual(found,set(updates))
        vals,widths=parse_card(new)
        self.assertEqual(vals[("MASS",1000002)],250.)
        self.assertEqual(vals[("MASS",1000001)],250.)
        self.assertEqual(widths[24],0.)
        self.assertEqual(vals[("MINPAR",3)],1.)
    def test_expected_fixed_color_target(self):
        b=Setup(500.,splitting(500.,3.),"Z")
        r=reference(b)
        self.assertAlmostEqual(r["analytic_fixed_color_helicity_sum"]/3,
                               r["candidate_MG5_color_averaged_if_denominator_3"])
    def test_readps_switch(self):
        original="      PARAMETER (READPS = .FALSE.)\n      PARAMETER (NPSPOINTS = 4)\n"
        new=patch_readps(original)
        self.assertIn("READPS = .TRUE.",new)
        self.assertIn("NPSPOINTS = 1",new)
        with self.assertRaises(RuntimeError):
            patch_readps("C no readps here\n")

if __name__=="__main__":
    unittest.main()
