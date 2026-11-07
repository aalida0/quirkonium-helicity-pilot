"""Read-only MG5 discrepancy diagnostic: kinematic and SLHA/mixing invariants."""
import math
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mg5_discrepancy_audit import ps_at_relative_q,mixing_block,matrix_source_audit

class TestDiscrepancyAudit(unittest.TestCase):
    def test_on_shell_momentum_scans(self):
        for q in (0.,.1,1.,20.):
            for mv in (0.,91.1876):
                ps=ps_at_relative_q(244.831373,255.168627,
                                    80.379,mv,q)
                self.assertEqual(len(ps),4)
                self.assertEqual(len(ps[0]),4)
                for i in range(4):
                    self.assertLess(abs(ps[0][i]+ps[1][i]-
                                        ps[2][i]-ps[3][i]),1e-8)
                for k,m in zip(ps,(244.831373,255.168627,80.379,mv)):
                    inv=k[0]**2-sum(x*x for x in k[1:])
                    self.assertTrue(math.isclose(inv,m*m,
                                                 abs_tol=1e-7,rel_tol=1e-9))

    def test_mixing_block_extracts_slha6(self):
        card=("BLOCK MASS\n 1000001 255.0\n"
              "BLOCK USQMIX\n 1 1 1.000000e0 # uL\n"
              " 2 2 1.0000\n 1 4 0.0000\n"
              "BLOCK DSQMIX\n 1 1 9.999e-1\n"
              "DECAY 24 0.0\n")
        self.assertEqual(mixing_block(card,"USQMIX"),
                         {"1,1":1.,"2,2":1.})
        self.assertEqual(mixing_block(card,"DSQMIX"),
                         {"1,1":.9999})

    def test_graph_and_color_lines_in_report(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/"matrix.f"
            f.write_text("      PARAMETER (NGRAPHS= 4)\n"
                         "      DATA Denom(1 )/ 3/\n"
                         "      CALL SXXXXX(P(0,1),MASS1,...)\n"
                         "      CALL VXXXXX(P(0,3),MASS3,...)\n")
            report=matrix_source_audit(f)
            self.assertEqual(report["number_of_helas_calls"],2)
            text="\n".join(x["text"] for x in report["color_and_averaging_lines"])
            self.assertIn("NGRAPHS",text)
            self.assertIn("Denom",text)
if __name__=="__main__":
    unittest.main()
