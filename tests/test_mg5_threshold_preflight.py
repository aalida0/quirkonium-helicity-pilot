"""Test the on-shell threshold PS and safe card editing without MadGraph."""
import sys
import unittest
import tempfile
import json
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"src"))
from mg5_threshold_preflight import (momenta,validate_ps,parse_card,
                                   replace_card,reference,ew_input_audit,run)
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
    def test_optional_absent_sminputs2_is_reported_not_fabricated(self):
        card=("Block SMINPUTS\n 1 1.28E2 # aEWM1\n 3 0.118 # aS\n")
        vals,_=parse_card(card)
        edited,found=replace_card(card,{("SMINPUTS",1):133.,
                                       ("SMINPUTS",2):1.2e-5})
        status=ew_input_audit(vals,found,1.2e-5)
        self.assertEqual(status["SMINPUTS_codes_present"],[1,3])
        self.assertFalse(status["SMINPUTS_2_Gf_present"])
        self.assertFalse(status["SMINPUTS_2_Gf_was_updated"])
        self.assertNotIn(" 2 ",edited)

    def test_preflight_missing_gf_preview_succeeds_but_apply_blocked(self):
        slha=("Block SMINPUTS\n 1 1.28E2 # aEWM1\n 3 0.118 # aS\n"
              "Block MASS\n 23 91.19\n 24 80.38\n"
              " 1000001 330.\n 1000002 320.\n")
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for dirname in ("MG5_UL_DL_WZ","MG5_UL_DL_WA"):
                out=root/dirname
                (out/"Cards").mkdir(parents=True)
                (out/"SubProcesses"/"P1_sample").mkdir(parents=True)
                (out/"SubProcesses"/"P1_sample"/"matrix.f").write_text(
                    "      PARAMETER (NGRAPHS=4)\n")
                (out/"Cards"/"param_card.dat").write_text(slha)
            argv=["mg5_threshold_preflight.py","--root",str(root),
                  "--mass","500","--tanbeta","3","--write-cards"]
            with patch.object(sys,"argv",argv),redirect_stdout(StringIO()):
                run()
            manifest=json.loads((root/"threshold_benchmarks"/
                                 "M500_tanbeta3_preflight.json").read_text())
            for V in ("Z","gamma"):
                report=manifest["channels"][V]
                self.assertFalse(report["electroweak_input_audit"][
                    "SMINPUTS_2_Gf_present"])
                self.assertTrue(Path(report["matched_card"]).is_file())
                self.assertIn("3 0.118",(root/("MG5_UL_DL_WZ" if V=="Z" else
                        "MG5_UL_DL_WA")/"Cards"/"param_card.dat").read_text())
            argv.append("--apply")
            with patch.object(sys,"argv",argv),redirect_stdout(StringIO()):
                with self.assertRaisesRegex(RuntimeError,
                                            "unknown GF/EW input scheme"):
                    run()
            self.assertFalse((root/"MG5_UL_DL_WZ"/"Cards"/
                              "param_card_before_quirkonium.dat").exists())

    def test_readps_switch(self):
        original="      PARAMETER (READPS = .FALSE.)\n      PARAMETER (NPSPOINTS = 4)\n"
        new=patch_readps(original)
        self.assertIn("READPS = .TRUE.",new)
        self.assertIn("NPSPOINTS = 1",new)
        with self.assertRaises(RuntimeError):
            patch_readps("C no readps here\n")

if __name__=="__main__":
    unittest.main()
