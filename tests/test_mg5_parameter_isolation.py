"""Parameter-isolation audit tests: no external MG5 executable required."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mg5_parameter_isolation import (build_cases,changed_group_updates,
                                     on_shell_mass_tuple)

class TestParameterIsolation(unittest.TestCase):
    def setUp(self):
        self.original=("Block SMINPUTS\n 1 1.27934E+02 # aEWM1\n 3 1.18E-1\n"
                       "Block MASS\n 23 91.1876\n 24 79.82901\n"
                       " 1000001 568.4411\n 1000002 561.119\n"
                       "DECAY 24 2.1\n"
                       "Block MINPAR\n 3 10.0\n")
        self.review=("Block SMINPUTS\n 1 1.32663E+02 # aEWM1\n 3 1.18E-1\n"
                     "Block MASS\n 23 91.1876\n 24 80.379\n"
                     " 1000001 255.1686\n 1000002 244.8314\n"
                     "DECAY 24 0.0\n"
                     "Block MINPAR\n 3 3.0\n")

    def test_group_updates_are_disjoint(self):
        groups=[changed_group_updates(self.original,self.review,[name])
                for name in ("squarks","ew","widths","other")]
        keys=[set(g) for g in groups]
        self.assertEqual(len(set().union(*keys)),sum(map(len,keys)))
        self.assertEqual(groups[0][("MASS",1000002)],244.8314)
        self.assertEqual(groups[1][("MASS",24)],80.379)
        self.assertEqual(groups[2][("DECAY",24)],0.0)
        self.assertEqual(groups[3][("MINPAR",3)],3.0)

    def test_both_full_and_original_cases_exist(self):
        cases,unique=build_cases(self.original,self.review)
        by_name={label:(raw,groups) for label,groups,raw,_,_ in cases}
        self.assertEqual(len(cases),10)
        self.assertGreaterEqual(unique,8)
        self.assertEqual(on_shell_mass_tuple(
            by_name["original"][0],"Z"),(561.119,568.4411,79.82901,91.1876))
        self.assertEqual(on_shell_mass_tuple(
            by_name["full_review"][0],"gamma"),(244.8314,255.1686,80.379,0.))
        self.assertEqual(on_shell_mass_tuple(
            by_name["squarks_only"][0],"Z"),(244.8314,255.1686,79.82901,91.1876))
        self.assertEqual(on_shell_mass_tuple(
            by_name["ew_only"][0],"Z"),(561.119,568.4411,80.379,91.1876))
        self.assertNotEqual(by_name["full_review"][0],by_name["original"][0])

    def test_missing_gf_never_added(self):
        cases,_=build_cases(self.original,self.review)
        for _,_,text,_,_ in cases:
            self.assertNotIn(" 2 1.16",text)
            self.assertNotIn("SMINPUTS\n 2",text)
if __name__=="__main__":
    unittest.main()
