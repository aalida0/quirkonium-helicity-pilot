"""Regression: parse actual Mathematica backtick precision and compare 9 points."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from compare_wolfram import compare,EXPECTED

class MathematicaLogRegression(unittest.TestCase):
    def test_user_benchmark_grid_matches(self):
        data=(ROOT/"validation"/"wolfram_benchmark_20261107.txt").read_text()
        rows,bad=compare(data,tolerance=5e-12)
        self.assertEqual(len(rows),9)
        self.assertEqual({(m,t) for m,t,*_ in rows},EXPECTED)
        self.assertEqual(bad,[])
        self.assertLess(max(max(r[2:]) for r in rows),2e-13)

    def test_wolfram_precision_suffix_not_silent_skip(self):
        data="M=500 tanbeta=1 f00=0.00193812074625797`16. a1=-0.01842281564018903`12. a2=0.2495154698134355`12."
        rows,bad=compare(data,tolerance=5e-12)
        self.assertEqual(len(rows),1)
        self.assertFalse(bad)
