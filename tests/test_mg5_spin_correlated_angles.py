"""6-leg spin-correlated kinematics and angular Fourier test without MG5."""
import math
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mg5_spin_correlated_angles import (
    add,inner,six_leg_point,coefficients,build_cases)

class TestSpinCorrelatedSixLeg(unittest.TestCase):
    def test_two_resonance_on_shell_massless_lepton_kinematics(self):
        for m,tb in ((200.,.4),(500.,.394724021524),
                     (500.,3.),(1200.,10.)):
            for cw,cz,phi in ((0.,0.,0.),(.4,-.2,math.pi/4),
                              (-.7,.6,math.pi),(0.99,-.9,2.4)):
                with self.subTest(m=m,tb=tb,cw=cw,cz=cz,phi=phi):
                    ps=six_leg_point(m,tb,cw,cz,phi)
                    self.assertEqual(len(ps),6)
                    for leg in ps[2:]:
                        self.assertAlmostEqual(inner(leg,leg),0.,delta=1e-7)
                    self.assertAlmostEqual(inner(add(ps[2],ps[3]),
                                                 add(ps[2],ps[3])),
                                           80.379**2,delta=2e-6)
                    self.assertAlmostEqual(inner(add(ps[4],ps[5]),
                                                 add(ps[4],ps[5])),
                                           91.1876**2,delta=2e-6)

    def test_phi_azimuthal_fourier_extractor(self):
        phis=[2*math.pi*k/8 for k in range(8)]
        values=[2*(1-.1203*math.cos(x)+.02268*math.cos(2*x))
                for x in phis]
        result=coefficients(values,phis)
        self.assertAlmostEqual(result["a1"],-.1203,places=13)
        self.assertAlmostEqual(result["a2"],.02268,places=13)
        self.assertAlmostEqual(result["sin1"],0.,places=13)
        self.assertAlmostEqual(sum(result["normalized_phi"]),1.)

    def test_build_grid_correct_size(self):
        grid,cos,w,phis=build_cases(500.,3.,4,8)
        self.assertEqual(len(grid),4*4*8)
        self.assertEqual(len(phis),8)
        self.assertAlmostEqual(sum(w),2.)
        self.assertEqual(grid[0]["id"],"k0_i0_j0")
        self.assertEqual(len(grid[0]["momenta"]),6)

if __name__=="__main__":
    unittest.main()
