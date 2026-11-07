"""Offline tests of the paper's LO partonic formula and PDF convolution.

A fake PDF tests arithmetic and beam ordering only, not physical rates.
It cannot replace an installed, versioned LHAPDF set.
"""
import math
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from quirkonium_production_pdf_gate import (
    partonic_fb,pdf_convolution,make_point,channels,ceiling)

class UniformXF:
    """Deliberately UNPHYSICAL positive test fixture: x*f(x)=constant."""
    def xfxQ(self,pid,x,Q):
        if not(0<x<1) or Q<=0:
            raise ValueError("out-of-domain PDF integration")
        return 1.

class SourceProductionTests(unittest.TestCase):
    def test_threshold_and_delta_sign_parity_exact(self):
        m=500.
        self.assertEqual(partonic_fb(m*m,m,10),0.)
        self.assertEqual(partonic_fb(.5*m*m,m,10),0.)
        for shat in (m*m*1.1,m*m*2.,m*m*10):
            for delta in (0.,1.,9.44,10.34,40.):
                self.assertEqual(
                    partonic_fb(shat,m,delta),
                    partonic_fb(shat,m,-delta))
                self.assertGreater(partonic_fb(shat,m,delta),0.)

    def test_source_beta_cubed_and_alpha_prefactor(self):
        import math
        from quirkonium_production_pdf_gate import (
            ALPHA_W, MW, FB_PER_GEV2)
        m=500.
        shat=4*m*m
        beta2=1-m*m/shat
        expected=(FB_PER_GEV2*math.pi*ALPHA_W**2/(32*shat)
                  *beta2**1.5/(1-MW*MW/shat)**2)
        self.assertAlmostEqual(partonic_fb(shat,m,0.),expected,places=12)

    def test_proton_beam_permutations_and_charge_sums(self):
        p=UniformXF()
        result=pdf_convolution(p,13600.,500.,9.44,500.,16,"ud")
        self.assertAlmostEqual(result["wplus_fb"],result["wminus_fb"],
                               delta=1e-12*result["charged_sum_fb"])
        self.assertAlmostEqual(result["charged_sum_fb"],
                               result["wplus_fb"]+result["wminus_fb"])
        self.assertGreater(result["charged_sum_fb"],0.)
        full=pdf_convolution(p,13600.,500.,9.44,500.,16,"full-ckm")
        self.assertGreater(full["charged_sum_fb"],result["charged_sum_fb"])
        self.assertEqual(len(channels("full-ckm")),6)

    def test_delta_two_branch_effect_small(self):
        # Same M: production only feels |Delta|², not its sign.
        p=UniformXF()
        row=make_point(p,13600.,500.,3.,[12,16],"ud",90.71,1.)
        ratio=row["low_over_high_production"]
        self.assertLess(abs(ratio-1),.005)
        self.assertEqual(row["source_partonic_sign_parity_residual"],0.)
        self.assertEqual(row["low"]["ceiling"]["actual_reconstructed_efficiency"]
                             if "actual_reconstructed_efficiency" in
                                row["low"]["ceiling"] else
                         row["low"]["ceiling"]["fiducial_efficiency"],
                         "UNKNOWN")

    def test_ceiling_is_necessary_only(self):
        low=ceiling(80.,90.71)
        high=ceiling(120.,90.71)
        self.assertFalse(low["necessary_condition_met_if_Psurvival_eff1"])
        self.assertTrue(high["necessary_condition_met_if_Psurvival_eff1"])
        self.assertEqual(high["physical_survival"],"UNKNOWN")
        self.assertGreater(high["required_survival_times_acceptance"],0.)

if __name__=="__main__":
    unittest.main()
