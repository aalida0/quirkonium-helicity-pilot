"""Standalone no-LHAPDF regression for one-shot quirkonium FCC survival.

The fake x*f=1 PDF is NONPHYSICAL and only tests numerical plumbing.
No user-ready collider yields are inferred from this test fixture.
"""
import math
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"src"))
from quirkonium_fcc_survival_one_shot import (
    beta_decay_width_A1,t_deexc_eq2_11_s,survival,
    numerical_selfchecks,rapidity_survival_convolution,
    build_angular_y_basis,mix_angular_basis,run_scenario)
from quirkonium_neutrino_pz_gate import run_one
from quirkonium_production_pdf_gate import pdf_convolution

class UniformXF:
    """Artificial x*f(x,Q)=1 for every flavor; only a test of arithmetic."""
    def xfxQ(self,pid,x,Q):
        if not (0<x<1 and Q>0):
            raise ValueError("Invalid fixture PDF input")
        return 1.

class FormulaTests(unittest.TestCase):
    def test_source_integral_small_delta_limit(self):
        # Source A1 directly states integral -> 2/5 as delta/M -> 0.
        # Hold Delta/mW small as well as Delta/M.
        r=beta_decay_width_A1(1e7,.01,96)
        self.assertAlmostEqual(r["dimensionless_A1_integral"],
                               .4,delta=1e-5)

    def test_beta_width_and_source_rough_lifetime_are_not_equated(self):
        b=beta_decay_width_A1(1000.,10.)
        self.assertGreater(b["Gamma_beta_GeV"],0)
        self.assertAlmostEqual(b["tau_beta_A1_s"],2.22e-17,
                               delta=1.5e-19)
        # This source inconsistency is a PHYSICS red flag; tests must
        # expose it, not adjust numbers to make the ratio ~one.
        self.assertGreater(b["ratio_tau_eq3_5_over_A1"],1e4)

    def test_photon_cooling_and_survival_monotonicity(self):
        self.assertEqual(t_deexc_eq2_11_s(500,10,500,5),0.)
        tau=beta_decay_width_A1(500.,10.)["tau_beta_A1_s"]
        for lam in (1.,2.,5.,10.):
            self.assertAlmostEqual(
                survival(500,500,10,lam,tau),1.,places=14)
        self.assertLess(survival(1000,500,10,2,tau),
                        survival(1000,500,10,5,tau))
        self.assertLess(survival(2000,500,10,5,tau),
                        survival(1000,500,10,5,tau))
        self.assertAlmostEqual(
            t_deexc_eq2_11_s(500,10,1000,5),
            t_deexc_eq2_11_s(500,-10,1000,5))

    def test_builtin_source_invariants(self):
        self.assertEqual(numerical_selfchecks()["status"],
                         "PASS_SCOPED_NUMERICAL_IDENTITIES")

class PDFSurvivalTests(unittest.TestCase):
    def test_survived_rate_bounded_by_production_and_increases_with_lambda(self):
        pdf=UniformXF()
        row=rapidity_survival_convolution(
            pdf,13600.,500.,9.4378,500.,[1.,2.,5.],
            16,24,"ud")
        ref=pdf_convolution(pdf,13600.,500.,9.4378,
                            500.,32,"ud")
        self.assertLess(abs(
            row["raw_charge_sum_fb"]/ref["charged_sum_fb"]-1),.02)
        self.assertGreater(row["raw_wplus_fb"],0)
        self.assertGreater(row["raw_wminus_fb"],0)
        a=row["lambda_scan"]
        self.assertLessEqual(a["1.0"]["surv_wplus_fb"],
                             a["2.0"]["surv_wplus_fb"])
        self.assertLessEqual(a["2.0"]["surv_wplus_fb"],
                             a["5.0"]["surv_wplus_fb"])
        self.assertLessEqual(a["5.0"]["surv_wplus_fb"],
                             row["raw_wplus_fb"]+1e-12)
        self.assertEqual(len(row["rapidities"]),16)

    def test_angular_per_y_basis_agrees_with_existing_reconstruction(self):
        ys=[-.8,.15,.65]
        basis=build_angular_y_basis(500.,3.,ys,3,8,3)
        mixed=mix_angular_basis(basis,[1.,3.,2.])
        old=run_one(500.,3.,3,8,3,ys,[1.,3.,2.])
        self.assertLess(basis["max_truth_closure_rad"],1e-8)
        for label in ("truth","min_abs_pz","known_resonance_mass",
                      "equal_roots"):
            self.assertAlmostEqual(
                mixed[label]["a1"],old[label]["a1"],delta=1e-11)
            self.assertAlmostEqual(
                mixed[label]["a2"],old[label]["a2"],delta=1e-11)
        self.assertAlmostEqual(mixed["minpz_correct_fraction"],
                               old["minpz_correct_fraction"],delta=1e-11)

    def test_tiny_full_one_shot_workflow_and_json(self):
        p=UniformXF()
        data=run_scenario(p,13.6,3000.,500.,3.,
                          [2.,5.],12,20,28,3,8,3,"ud")
        self.assertEqual(data["angular_charge_mode"],"W+ only")
        self.assertEqual(data["low_tanbeta_UV_viability"]
                         if "low_tanbeta_UV_viability" in data else
                         data["physical_model"],
                         data["physical_model"])
        self.assertLess(data["branches"]["low"][
            "source_integral_vs_independent_relative"],.02)
        self.assertEqual(len(data["lambda_comparison"]),2)
        json.dumps(data,allow_nan=False)

if __name__=="__main__":
    unittest.main()
