"""Offline PDF-boost and angular reweighting invariants; no LHAPDF needed.

A test PDF with x*f(x,Q)=constant is NOT a physical PDF.
These tests validate coordinates, beam accounting, weights and
backward-compatible phase reconstruction, not FCC-hh physics rates.
"""
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"src"))

from quirkonium_production_pdf_gate import pdf_convolution
from quirkonium_fcc_pdf_rapidity_gate import (
    rapidity_pdf_quadrature,mode_rapidity_weights,parse_scenarios,
    analyze_scenario)
from quirkonium_neutrino_pz_gate import run_one

class UniformXF:
    def xfxQ(self,pid,x,Q):
        if not 0<x<1 or Q<=0:
            raise ValueError("unphysical fixture outside PDF domain")
        return 1.

class RapiditiyPDFTests(unittest.TestCase):
    def test_independent_y_t_coordinates_reproduce_ln_x_integral(self):
        p=UniformXF()
        for energy in (13600.,85000.):
            for flavor in ("ud","full-ckm"):
                with self.subTest(energy=energy,flavor=flavor):
                    original=pdf_convolution(
                        p,energy,500.,9.4378,500.,32,flavor)
                    new=rapidity_pdf_quadrature(
                        p,energy,500.,9.4378,500.,24,40,flavor)
                    self.assertLess(abs(new["charged_sum_fb"]/
                                        original["charged_sum_fb"]-1),.003)
                    self.assertAlmostEqual(
                        new["charged_sum_fb"],
                        new["wplus_fb"]+new["wminus_fb"])
                    self.assertEqual(len(new["nodes"]),24)
                    for key in ("wplus_fb","wminus_fb"):
                        self.assertLess(
                            new["max_pp_beam_evenness_rel_to_mean"][key],1e-11)

    def test_charge_mode_does_not_double_count_wminus(self):
        p=UniformXF()
        d=rapidity_pdf_quadrature(
            p,13600.,500.,9.44,500.,16,24,"ud")
        ys,wp,wplus=mode_rapidity_weights(d,"wplus")
        ys2,wb,both=mode_rapidity_weights(d,"both_cp_assumed")
        self.assertEqual(ys,ys2)
        self.assertEqual(len(ys),16)
        self.assertAlmostEqual(sum(wp),1.)
        self.assertAlmostEqual(sum(wb),1.)
        self.assertAlmostEqual(wplus,d["wplus_fb"])
        self.assertAlmostEqual(both,d["charged_sum_fb"])
        self.assertAlmostEqual(both,2*wplus,places=8)

    def test_weighted_angular_ensemble_legacy_equal_weights(self):
        a=run_one(500.,3.,3,8,3,[-.7,.6])
        b=run_one(500.,3.,3,8,3,[-.7,.6],
                  rapidity_weights=[1.,1.])
        for label in ("truth","min_abs_pz","known_resonance_mass",
                      "equal_roots"):
            self.assertAlmostEqual(a[label]["a1"],b[label]["a1"],
                                   delta=1e-12)
            self.assertAlmostEqual(a[label]["a2"],b[label]["a2"],
                                   delta=1e-12)
        self.assertEqual(a["n_weighted_points"],b["n_weighted_points"])

    def test_weighted_angular_replication_equivalence(self):
        # Two copies of -0.7 are exactly the same as one position
        # with twice the weight (apart from roundoff).
        repeated=run_one(500.,3.,3,8,3,[-.7,-.7,.6])
        compressed=run_one(500.,3.,3,8,3,[-.7,.6],
                           rapidity_weights=[2.,1.])
        for label in ("truth","min_abs_pz","known_resonance_mass",
                      "equal_roots"):
            self.assertAlmostEqual(
                repeated[label]["a1"],compressed[label]["a1"],
                delta=1e-12)
            self.assertAlmostEqual(
                repeated[label]["a2"],compressed[label]["a2"],
                delta=1e-12)

    def test_bad_weights_rejected(self):
        with self.assertRaises(ValueError):
            run_one(500.,3.,3,8,3,[0.,1.],[1.,-1.])
        with self.assertRaises(ValueError):
            run_one(500.,3.,3,8,3,[0.,1.],[1.])
        with self.assertRaises(ValueError):
            run_one(500.,3.,3,8,3,[0.,1.],[0.,0.])

    def test_scenario_parse(self):
        self.assertEqual(parse_scenarios(["85:20000","100:30000"]),
                         [(85.,20000.),(100.,30000.)])
        with self.assertRaises(ValueError):
            parse_scenarios(["85"])

    def test_end_to_end_tiny_pilot_scope_and_pdf_check(self):
        # Small toy fixture tests code plumbing/JSON only, not rates.
        # Use W+ only; CP conjugate W- angles are unvalidated.
        out=analyze_scenario(
            UniformXF(),13.6,3000.,500.,3.,
            3,8,3,8,12,20,"ud","wplus",1.)
        self.assertEqual(out["charge_mode"],"wplus")
        self.assertEqual(
            out["wminus_angular_CP_validation"],
            "NOT_INCLUDED_IN_WPLUS_ONLY")
        self.assertTrue(
            out["sign_discrimination"]["truth"]["3sigma"][
                "necessary_condition_Psurv_eff_1"] in (True,False))
        self.assertLess(
            out["branches"]["low"]["relative_total_rate_disagreement"],.02)
        self.assertGreater(
            out["sign_discrimination"]["truth"]["3sigma"][
                "ideal_signal_selected_events"],0)

if __name__=="__main__":
    unittest.main()
