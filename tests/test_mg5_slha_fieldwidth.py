"""Guard 20-column SLHA numeric serialization and the fixed-width A/B."""
import math
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mg5_threshold_preflight import (format_slha_number,replace_card,parse_card)
from mg5_slha_fieldwidth_gate import alpha_long_and_compact

class SLHAFieldWidthTest(unittest.TestCase):
    def test_sci_fields_fit_legacy_20_column_reader(self):
        for value in (132.6638757554207,244.8313730872,255.1686269128,
                      80.379,0.,-250.,1.1621612149e-5):
            text=format_slha_number(value)
            self.assertLessEqual(len(text),20)
            self.assertTrue(math.isclose(float(text),value,
                                         rel_tol=1e-12,abs_tol=1e-12))
        self.assertEqual(len(f"{132.6638757554207:.15E}"),21)

    def test_slha_rewrite_never_uses_21_character_fields(self):
        original=("BLOCK SMINPUTS\n"
                  " 1 1.27934000E+02 # aEWM1\n"
                  "BLOCK MASS\n 1000001 5.684411E+02 # dl\n"
                  " 1000002 5.611190E+02 # ul\n")
        updates={("SMINPUTS",1):132.6638757554207,
                 ("MASS",1000002):244.8313730872,
                 ("MASS",1000001):255.1686269128}
        edited,found=replace_card(original,updates)
        self.assertEqual(found,set(updates))
        keys,_=parse_card(edited)
        for key,val in updates.items():
            self.assertTrue(math.isclose(keys[key],val,rel_tol=1e-12))
        for line in edited.splitlines():
            data=line.split("#",1)[0].split()
            if len(data)>=2 and data[0].isdigit():
                self.assertLessEqual(len(data[1]),20)

    def test_alpha_unchanged_numeric_but_wide_notation_is_explicit(self):
        original=("BLOCK SMINPUTS\n"
                  " 1 1.279340E+02 # aEWM1\n 3 1.18E-01 # as\n")
        compact,unsafe,info=alpha_long_and_compact(original)
        self.assertEqual(parse_card(compact)[0][("SMINPUTS",1)],127.934)
        self.assertEqual(parse_card(unsafe)[0][("SMINPUTS",1)],127.934)
        self.assertEqual(info["compact_length"],18)
        self.assertEqual(info["long_length"],21)
        inferred_if_exponent_clipped=(127.934/float(
            info["long"].split("E",1)[0]))**2
        self.assertAlmostEqual(inferred_if_exponent_clipped,10000.,places=8)

if __name__=="__main__":
    unittest.main()
