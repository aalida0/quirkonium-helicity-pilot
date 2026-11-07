"""Pure unit tests for an independent MG5 6-point benchmark grid.

These do not invoke generated Fortran, nor certify physics by themselves.
"""
import math
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import Setup,splitting,MW,MZ
from mg5_benchmark_grid import (POINTS,bench_label,generated_averaging_factor,
                                compact_card_for_point)
from mg5_threshold_preflight import parse_card,momenta,validate_ps

SYNTHETIC=("BLOCK SMINPUTS\n"
           " 1 1.279340000E+02 # aEWM1\n 3 1.180000E-01\n"
           "BLOCK MASS\n 23 9.118760E+01 # MZ\n"
           " 24 7.982901E+01 # MW\n"
           " 1000001 5.684411E+02 # down-L\n"
           " 1000002 5.611190E+02 # up-L\n"
           "BLOCK MINPAR\n 3 1.000000E+01 # tanbeta\n"
           "DECAY 24 2.0000E+00\n"
           "DECAY 23 2.4900E+00\n")

class TestIndependentMEGrid(unittest.TestCase):
    def test_covers_splitting_signs_zero_and_mass_range(self):
        self.assertEqual(len(POINTS),6)
        self.assertEqual(len({bench_label(*p) for p in POINTS}),len(POINTS))
        deltas=[splitting(m,tb) for m,tb in POINTS]
        self.assertTrue(any(d<0 for d in deltas))
        self.assertTrue(any(d>0 for d in deltas))
        self.assertTrue(any(abs(d)<1e-12 for d in deltas))
        self.assertTrue(max(m for m,_ in POINTS)>=2000)
        self.assertTrue(min(m for m,_ in POINTS)<500)

    def test_each_channel_card_round_trip(self):
        original_values,original_widths=parse_card(SYNTHETIC)
        for m,tb in POINTS:
            for channel in ("Z","gamma"):
                b=Setup(m,splitting(m,tb),channel)
                s,updates=compact_card_for_point(SYNTHETIC,b,tb)
                card,widths=parse_card(s)
                for key,value in updates.items():
                    recorded=widths[key[1]] if key[0]=="DECAY" else card[key]
                    self.assertTrue(math.isclose(recorded,value,rel_tol=2e-12,
                                                  abs_tol=1e-11))
                self.assertEqual(card[("SMINPUTS",3)],original_values[("SMINPUTS",3)])
                self.assertAlmostEqual(widths[24],0.)
                self.assertAlmostEqual(widths[23],0.)
                ps=momenta(b)
                validate_ps(ps,[b.mu,b.md,MW,b.mv])
                self.assertEqual(len(ps),4)

    def test_color_source_audit_accepts_only_3_over_9(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"matrix.f"
            content=("DATA IDEN/ 9/\n"
                     "PARAMETER (NWAVEFUNCS=5, NCOLOR=1)\n"
                     "DATA (CF(I,  1),I=  1,  1) "
                     "/3.000000000000000D+00/\n")
            p.write_text(content)
            self.assertEqual(generated_averaging_factor(p),1./3.)
            p.write_text(content.replace("IDEN/ 9/","IDEN/ 6/"))
            with self.assertRaises(RuntimeError):
                generated_averaging_factor(p)

if __name__=="__main__":
    unittest.main()
