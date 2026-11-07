#!/usr/bin/env python3
"""Independently compare Mathematica tensor/angle logs with Python.

Accepts Mathematica's arbitrary-precision notation (e.g. 0.123\`16.).
Run: python scripts/compare_wolfram.py validation/local_logs/mathematica.log
"""
import argparse
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from scalar_threshold_amplitudes import Setup,splitting,f00
from joint_wz_angles import azimuthal_cos1_amplitude,azimuthal_cos2_amplitude

# Mathematica prints numbers as 0.123\`16. unless formatted with InputForm.
# Remove only those suffixes; do NOT modify exponents or digits of the value.
PRECISION_SUFFIX=re.compile(r"\u0060\d+(?:\.\d*)?")
NUM=r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)"
RX=re.compile(
    r"M=\s*(\d+)\s+tanbeta=\s*([\d.]+)\s+f00=\s*"+NUM+
    r"\s+a1=\s*"+NUM+r"\s+a2=\s*"+NUM
)
EXPECTED={(float(m),float(t)) for m in (250,500,1000) for t in (1,3,10)}
PASS_MARKER="PASS Mathematica tensor / published rates / Ward"

def compare(log,tolerance=5e-8):
    cleaned=PRECISION_SUFFIX.sub("",log)
    rows=[]
    for line in cleaned.splitlines():
        match=RX.search(line)
        if not match:continue
        mass,tb,frac,a1,a2=map(float,match.groups())
        b=Setup(mass,splitting(mass,tb),'Z')
        expected=(f00(b),azimuthal_cos1_amplitude(b),
                  azimuthal_cos2_amplitude(b))
        diffs=[abs(actual-ref) for actual,ref in zip((frac,a1,a2),expected)]
        rows.append((mass,tb,*diffs))
    if not rows:
        raise ValueError("No numeric Mathematica benchmark rows parsed")
    bad=[row for row in rows if max(row[2:])>tolerance]
    return rows,bad

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path)
    parser.add_argument('--tolerance',type=float,default=5e-8)
    parser.add_argument('--allow-incomplete',action='store_true',
                        help="Allow a partial/diagnostic Mathematica grid")
    opts=parser.parse_args()
    raw=opts.log.read_text(errors='replace')
    if PASS_MARKER not in raw or "FAIL " in raw:
        print("FAIL: Mathematica log lacks the exact PASS marker or has FAIL",file=sys.stderr)
        return 2
    rows,bad=compare(raw,opts.tolerance)
    combos={(m,t) for m,t,*_ in rows}
    if not opts.allow_incomplete and (combos!=EXPECTED or len(rows)!=len(EXPECTED)):
        missing=sorted(EXPECTED-combos)
        print(f"FAIL: expected 9 distinct benchmarks; parsed {len(rows)}; missing={missing}",file=sys.stderr)
        return 2
    for mass,tb,df,da1,da2 in rows:
        print(f"M={mass:g} tanbeta={tb:g} df00={df:.3g} "
              f"da1={da1:.3g} da2={da2:.3g}")
    print(f"Compared {len(rows)} rows; failed={len(bad)}; "
          f"maximum_abs_difference={max(max(row[2:]) for row in rows):.4g}")
    if "N::meprec" in raw:
        print("CAUTION: Mathematica reported N::meprec precision warnings; "
              "double-precision agreement does not certify the 1e-22 "
              "internal precision target.")
    return 1 if bad else 0

if __name__=="__main__":
    raise SystemExit(main())
