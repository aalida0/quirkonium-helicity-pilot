"""Test EW input split and exact-review card reconciliation without MG5."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mg5_ew_input_audit import make_cases,numeric_card_delta
from mg5_parameter_isolation import card_data

class EWInputAuditTest(unittest.TestCase):
    def setUp(self):
        self.original=("BLOCK SMINPUTS\n 1 127.934 # aEWM1\n 3 0.118 # aS\n"
                       "BLOCK MASS\n 23 91.1876\n 24 79.82901\n"
                       " 1000001 568.4411\n 1000002 561.119\n"
                       "DECAY 24 2.1\nBLOCK MINPAR\n 3 10.0\n")
        self.review=("BLOCK SMINPUTS\n 1 132.663875755 # aEWM1\n 3 0.118 # aS\n"
                     "BLOCK MASS\n 23 91.1876\n 24 80.379\n"
                     " 1000001 255.1686\n 1000002 244.8314\n"
                     "DECAY 24 0.0\nBLOCK MINPAR\n 3 3.0\n")

    def test_single_parameter_isolation(self):
        cards,comparison=make_cases(self.original,self.review)
        self.assertEqual(len(cards),9)
        orig=card_data(cards["original_exact"])
        a=card_data(cards["alpha_em_inverse_only"])
        w=card_data(cards["mw_only"])
        aw=card_data(cards["alpha_and_mw_only"])
        self.assertEqual(a[("SMINPUTS",1)],132.663875755)
        self.assertEqual(a[("MASS",24)],orig[("MASS",24)])
        self.assertEqual(w[("SMINPUTS",1)],orig[("SMINPUTS",1)])
        self.assertEqual(w[("MASS",24)],80.379)
        self.assertEqual(aw[("MASS",1000001)],orig[("MASS",1000001)])
        self.assertEqual(aw[("SMINPUTS",1)],132.663875755)
        self.assertEqual(aw[("MASS",24)],80.379)

    def test_full_reconstruction_semantically_matches_exact_preview(self):
        cards,comparison=make_cases(self.original,self.review)
        diff=comparison["review_vs_group_rebuilt"]
        self.assertFalse(diff["changed"],diff)
        self.assertFalse(diff["added"],diff)
        self.assertFalse(diff["removed"],diff)
        self.assertEqual(card_data(cards["full_review_all_scalar_rebuilt"]),
                         card_data(self.review))
        self.assertEqual(cards["full_review_exact"],self.review)

    def test_missing_group_component_is_reported(self):
        mutated=self.review.replace(
            "BLOCK MASS\n","BLOCK MASS\n 25 125.0 # new independent mass\n")
        _,comparison=make_cases(self.original,mutated)
        diff=comparison["review_vs_group_rebuilt"]
        self.assertIn("('MASS', 25)",diff["added"])

    def test_exact_review_is_not_recreated_by_formatting(self):
        pref=self.review.replace(
            "1 132.663875755","1 1.32663875755E+02")
        cards,comparison=make_cases(self.original,pref)
        self.assertEqual(cards["full_review_exact"],pref)
        self.assertEqual(card_data(cards["full_review_group_rebuilt"]),
                         card_data(pref))
        self.assertNotEqual(cards["full_review_group_rebuilt"],pref)

if __name__=="__main__":
    unittest.main()
