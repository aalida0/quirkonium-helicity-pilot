"""No-MadGraph unit tests for matrix2py parameter/threshold preflight.

These tests are software checks, not a generator amplitude validation.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"src"))
from mg5_matrix2py_compare import prepare,external_input_audit,build_error_summary
from scalar_threshold_amplitudes import ALPHA_W,S2,MW,MZ,splitting

class MG5Matrix2PyPreflight(unittest.TestCase):
    def make_fixture(self,root):
        mass=500.
        delta=splitting(mass,3.)
        base=Path(root)
        card=("BLOCK SMINPUTS\n"
              " 1 1.279340E2 # aEWM1\n"
              " 3 1.180000E-1 # aS\n"
              "BLOCK MASS\n"
              " 23 9.118760E1 # MZ\n"
              " 24 7.982901E1 # MW\n"
              " 1000001 5.684411E2 # dL\n"
              " 1000002 5.611190E2 # uL\n")
        matched=("BLOCK SMINPUTS\n"
              f" 1 {1/(ALPHA_W*S2):.15E} # aEWM1\n"
              " 3 1.180000E-1 # aS\n"
              "BLOCK MASS\n"
              f" 23 {MZ:.15E} # MZ\n"
              f" 24 {MW:.15E} # MW\n"
              f" 1000001 {(mass-delta)/2:.15E} # dL\n"
              f" 1000002 {(mass+delta)/2:.15E} # uL\n")
        for channel in ("Z","gamma"):
            name="MG5_UL_DL_WZ" if channel=="Z" else "MG5_UL_DL_WA"
            p=base/name
            (p/"Cards").mkdir(parents=True)
            (p/"SubProcesses"/"P1_control").mkdir(parents=True)
            (p/"Source/MODEL").mkdir(parents=True)
            (p/"Cards/param_card.dat").write_text(card)
            (p/"Cards/param_card_quirkonium_review.dat").write_text(matched)
            (p/"SubProcesses/P1_control/matrix.f").write_text(
                "      SUBROUTINE SMATRIX(P,ANS)\n")
            (p/"Source/MODEL/param_read.inc").write_text(
                "      CALL LHA_GET_REAL(NPARA,PARAM,VALUE,'aEWM1',AEWM1,1.279340D+02)\n"
                "      CALL LHA_GET_REAL(NPARA,PARAM,VALUE,'mdl_MW',MDL_MW,7.982901D+01)\n")
        return base

    def test_build_error_summary_keeps_compiler_diagnostic(self):
        log=("gfortran -c matrix.f\n"
             "fatal error: Python.h: No such file or directory\n"
             "make: *** [makefile:90: matrix2py.so] Error 1\n")
        report=build_error_summary(log,tail_lines=2)
        self.assertTrue(report["error_lines"])
        self.assertIn("Python.h", "\n".join(report["error_lines"]))
        self.assertIn("Error 1", report["tail"][-1])

    def test_accepts_missing_gf_with_review_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=self.make_fixture(tmp)
            for channel in ("Z","gamma"):
                p,work,review,b,momenta=prepare(channel,500.,3.,base)
                self.assertEqual(len(momenta),4)
                self.assertEqual(len(momenta[0]),4)
                self.assertAlmostEqual(b.M,500.)
                self.assertTrue(review.exists())
                data=external_input_audit(p)
                self.assertEqual(len(data["external_read_lines"]),2)
                self.assertEqual(data["gf_status"],
                    "NO_GF_IN_READER_NOT_PROOF_OF_ALL_DEPENDENCIES")
                self.assertIn("1.279340E2",(p/"Cards/param_card.dat").read_text())

    def test_rejects_unregistered_gf_injected_into_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=self.make_fixture(tmp)
            path=base/"MG5_UL_DL_WZ/Cards/param_card_quirkonium_review.dat"
            original=path.read_text()
            path.write_text(original.replace(
                " 3 1.180000E-1", " 2 1.166370E-5\n 3 1.180000E-1"))
            with self.assertRaisesRegex(RuntimeError,"unregistered GF"):
                prepare("Z",500.,3.,base)

    def test_rejects_unmatched_electromagnetic_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=self.make_fixture(tmp)
            path=base/"MG5_UL_DL_WA/Cards/param_card_quirkonium_review.dat"
            path.write_text(path.read_text().replace(
                f"{1/(ALPHA_W*S2):.15E}","1.279340E+02"))
            with self.assertRaisesRegex(RuntimeError,"Review card mismatches"):
                prepare("gamma",500.,3.,base)

if __name__=="__main__":
    unittest.main()
