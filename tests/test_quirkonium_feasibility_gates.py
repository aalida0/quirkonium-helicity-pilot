"""Model-domain and truth-neutrino reconstruction invariants, no MG5 needed."""
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"src"))
from quirkonium_model_domain_gate import domain_point,branch_comparison
from quirkonium_neutrino_pz_gate import (
    lab_event,reco_angles,neutrino_pz_roots,run_one,sign_cost)

class ModelDomainGateTests(unittest.TestCase):
    def test_two_branch_tree_scalar_doublet_soft_mass(self):
        for m in (250.,500.,1200.,2000.):
            with self.subTest(m=m):
                data=branch_comparison(m)
                self.assertEqual(data["tree_level_scalar_doublet_gate"],"PASS")
                self.assertEqual(data["actual_fully_consistent_SUSY_UV"],"UNKNOWN")
                self.assertTrue(data["tanbeta_low_simplified_erratum_interval"])
                self.assertGreater(data["same_R2_width_ratios"]
                                   ["WZ_low_over_high_if_same_R2"],0)
                for b in data["branches"].values():
                    self.assertAlmostEqual(b["mQ2_from_up_GeV2"],
                                           b["mQ2_from_down_GeV2"],
                                           delta=1e-8*m*m)

    def test_typeII_yukawa_is_an_assumption_not_full_uv(self):
        low=domain_point(500.,.394724021524)
        hi=domain_point(500.,3.)
        self.assertGreater(low["yt_weak_scale_tree_typeII_assumption"],
                           hi["yt_weak_scale_tree_typeII_assumption"])
        self.assertGreater(low["yt_weak_scale_tree_typeII_assumption"],2.)
        self.assertLess(low["yt_weak_scale_tree_typeII_assumption"],3.6)
        self.assertGreater(hi["common_soft_mass_positive"],0)

    def test_absolute_widths_not_falsely_called_equal(self):
        item=branch_comparison(500.)
        self.assertNotAlmostEqual(
            item["same_R2_width_ratios"]["Wgamma_low_over_high_if_same_R2"],
            1.,places=2)
        self.assertEqual(item["absolute_model_production_xsec"],"UNKNOWN")

class NeutrinoAmbiguityTests(unittest.TestCase):
    def test_quadratic_contains_true_pz_for_nontrivial_boosts(self):
        for t in (.394724021524,3.):
            for phi in (.2,1.,2.6,5.):
                event=lab_event(500.,t,.3,-.5,phi,.8,.5)
                e,nu=event[2],event[3]
                sols=neutrino_pz_roots(e,nu[1],nu[2])
                self.assertTrue(any(
                    abs(v-nu[3])<1e-6*max(1,abs(nu[3]))
                    for v in sols))

    def test_exact_truth_phi_closure_with_rotation_and_boost(self):
        for t in (.394724021524,3.):
            for theta,y in ((.4,-1.2),(.9,0), (2.3,.8)):
                for phi in (.2,1.2,2.7,4.8):
                    ev=lab_event(500.,t,.3,-.4,phi,theta,y)
                    obs=reco_angles(ev,500.)
                    residual=math.atan2(
                        math.sin(obs["truth"]-phi),
                        math.cos(obs["truth"]-phi))
                    self.assertAlmostEqual(residual,0.,delta=1e-8)

    def test_toy_ensemble_closes_truth_analytic_phase(self):
        low=run_one(500.,.394724021524,3,8,3,[0.])
        high=run_one(500.,3.,3,8,3,[0.])
        for row in (low,high):
            self.assertLess(row["max_truth_angle_closure_radians"],1e-8)
            self.assertGreater(row["minpz_correct_fraction"],0.)
            self.assertLessEqual(row["minpz_correct_fraction"],1.)
            self.assertAlmostEqual(
                row["truth"]["a1"],row["analytic_closed_a1"],delta=.003)
        self.assertGreater(low["truth"]["a1"],0)
        self.assertLess(high["truth"]["a1"],0)
        self.assertLess(sign_cost(low,high,"truth",3),1000)

if __name__=="__main__":
    unittest.main()
