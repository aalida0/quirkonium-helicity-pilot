#!/usr/bin/env python3
"""Compare independent Wolfram benchmark lines with Python scalar theory."""
import argparse
from pathlib import Path
import re
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from scalar_threshold_amplitudes import Setup,splitting,polarization_fraction
from joint_wz_angles import azimuthal_cos1_amplitude,azimuthal_cos2_amplitude

RX=re.compile(r'M=\s*(\d+)\s+tanbeta=\s*([\d.]+)\s+f00=\s*([-+\d.eE]+)'
              r'\s+a1=\s*([-+\d.eE]+)\s+a2=\s*([-+\d.eE]+)')
def compare(log,tolerance=5e-8):
    rows=[]
    for line in log.splitlines():
        m=RX.search(line)
        if not m: continue
        mass,tb,f00,a1,a2=map(float,m.groups())
        b=Setup(mass,splitting(mass,tb),'Z')
        ref=(polarization_fraction(b),azimuthal_cos1_amplitude(b),
             azimuthal_cos2_amplitude(b))
        diffs=[abs(x-y) for x,y in zip((f00,a1,a2),ref)]
        rows.append((mass,tb,*diffs))
    if not rows: raise ValueError('No independent Mathematica benchmark lines')
    return rows,[row for row in rows if max(row[2:])>tolerance]
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('log',type=Path)
    ap.add_argument('--tolerance',type=float,default=5e-8)
    x=ap.parse_args()
    s=x.log.read_text()
    if 'PASS' not in s or 'FAIL' in s:
        raise SystemExit('Mathematica log did not PASS')
    rows,bad=compare(s,x.tolerance)
    for mass,tb,df,da1,da2 in rows:
        print(f'M={mass:g} tanbeta={tb:g} df00={df:.3g} da1={da1:.3g} da2={da2:.3g}')
    print(f'Compared {len(rows)} points, failed={len(bad)}')
    raise SystemExit(1 if bad else 0)
