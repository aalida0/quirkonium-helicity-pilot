"""Unit-test source-indexed fixed-helicity parsing and classification."""
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mg5_fixed_helicity_audit import find_helicity_configs,classify

class FixedHelicityAuditTests(unittest.TestCase):
    def test_generated_data_rows_and_fraction_types(self):
        text=("      DATA (NHEL(I, 1),I=1,4) /0,0,-1,-1/\n"
              "      DATA (NHEL(I, 2),I=1,4) /0,0,0,0/\n"
              "      DATA (NHEL(I, 3),I=1,4) /0,0,1,1/\n"
              "      DATA (NHEL(I, 4),I=1,4) /0,0,1,-1/\n")
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"matrix.f";f.write_text(text)
            rows=find_helicity_configs(f)
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[1]["helicities"],[0,0,0,0])
        for row,val in zip(rows,[.4,.5,.4,0.]):
            row["me2"]=val
        groups,details=classify(rows,"Z")
        self.assertAlmostEqual(groups["transverse"],.8)
        self.assertAlmostEqual(groups["00"],.5)
        self.assertAlmostEqual(groups["other"],0.)
        self.assertEqual(details[1]["kind"],"00")

    def test_gamma_has_no_longitudinal_wgamma(self):
        rows=[{"nhel":1,"helicities":[0,0,-1,-1],"me2":.5},
              {"nhel":2,"helicities":[0,0,1,1],"me2":.5},
              {"nhel":3,"helicities":[0,0,0,1],"me2":0.}]
        groups,_=classify(rows,"gamma")
        self.assertEqual(groups["00"],0.)
        self.assertEqual(groups["other"],0.)
        self.assertEqual(groups["transverse"],1.)

    def test_noncontiguous_rows_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"matrix.f"
            f.write_text("      DATA (NHEL(I, 2),I=1,4) /0,0,1,1/\n")
            with self.assertRaises(RuntimeError):
                find_helicity_configs(f)

if __name__=="__main__":
    unittest.main()
