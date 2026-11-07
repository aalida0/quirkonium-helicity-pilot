#!/usr/bin/env python3
"""Test a D-term two-branch degeneracy in charged scalar quirkonium.

At fixed M, find tanbeta_-<1 with the SAME longitudinal fraction as a
reference tanbeta_+>1. In this LO model ΓWZ^T / ΓWgamma =
tan²(thetaW) beta_WZ/beta_Wgamma, so equal f00 implies equal
ΓWZ/ΓWgamma and (if ONLY WZ/Wgamma modes) BR(WZ). The sign-sensitive
longitudinal-transverse interference a1 need NOT be equal.

This is a mathematical/ideal-angular proof-of-principle only. The 2026
erratum explicitly displays 0.1<=tanbeta<=10, while the original 2025
model text describes tanbeta>1 for the SUSY interpretation. Therefore
the physical model admissibility of a tanbeta<1 branch is UNKNOWN.
It would be misleading to claim a physical two-branch ambiguity before
that limitation is resolved.

Run: python scripts/quirkonium_branch_degeneracy.py
"""
import argparse
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import (Setup,MW,MZ,S2,C2,splitting,f00,
                                         published_width)
from joint_wz_angles import (azimuthal_cos1_amplitude,
                             azimuthal_cos2_amplitude)

DEFAULT_M=(250.,300.,400.,500.,800.,1200.,2000.)

def model_point(m,tb):
    z=Setup(m,splitting(m,tb),"Z")
    gam=Setup(m,splitting(m,tb),"gamma")
    wz=published_width(z)
    wgamma=published_width(gam)
    a1=azimuthal_cos1_amplitude(z)
    a2=azimuthal_cos2_amplitude(z)
    return {"M":m,"tanbeta":tb,"delta":z.delta,
            "f00":f00(z),"a1":a1,"a2":a2,
            "width_wz_over_wgamma":wz/wgamma,
            "branch_wz_two_channels":wz/(wz+wgamma)}

def find_low_branch(m,reference_tb,low=.1,high=.999999999,
                    tol=1e-13,max_iter=200):
    if not(0<low<high<1<reference_tb):
        raise ValueError("Require 0<low<high<1<reference_tb")
    target=f00(Setup(m,splitting(m,reference_tb),"Z"))
    f=lambda x:f00(Setup(m,splitting(m,x),"Z"))-target
    left,right=f(low),f(high)
    if left*right>0:
        raise ValueError(f"No tanbeta<1 bracket at M={m}: {left}, {right}")
    for _ in range(max_iter):
        center=(low+high)/2
        fm=f(center)
        if abs(fm)<tol or high-low<1e-14:return center
        if left*fm>0:low,left=center,fm
        else:high,right=center,fm
    raise RuntimeError("Bisection did not converge")

def kinematics_factor(m):
    zw=Setup(m,0.,"Z")
    ph=Setup(m,0.,"gamma")
    return S2/C2*zw.beta/ph.beta

def compare_branches(m,high_tb):
    low_tb=find_low_branch(m,high_tb)
    neg=model_point(m,low_tb)
    pos=model_point(m,high_tb)
    k=kinematics_factor(m)
    for p in (neg,pos):
        f=p["f00"]
        expected=k/(1-f)
        if not math.isclose(p["width_wz_over_wgamma"],expected,
                            rel_tol=5e-11):
            raise RuntimeError("Eq A.6/A.7 rate-f00 identity fails")
    passed=(math.isclose(neg["f00"],pos["f00"],abs_tol=1e-11) and
            math.isclose(neg["branch_wz_two_channels"],
                         pos["branch_wz_two_channels"],abs_tol=1e-11) and
            math.isclose(neg["a1"],-pos["a1"],abs_tol=1e-11) and
            math.isclose(neg["a2"],pos["a2"],abs_tol=1e-11))
    return {"mass":m,"low_branch":neg,"high_branch":pos,
            "k_ratio_transverse_wz_over_wgamma":k,
            "f00_abs_diff":abs(neg["f00"]-pos["f00"]),
            "BR_WZ_abs_diff":abs(neg["branch_wz_two_channels"]-
                                 pos["branch_wz_two_channels"]),
            "a1_signed_sum":neg["a1"]+pos["a1"],
            "mathematical_two_branch_gate":"PASS" if passed else "FAIL",
            "physical_both_branches_allowed":"UNKNOWN",
            "literature_novelty":"UNKNOWN"}

def signal_count_for_sign_discrimination(a1,a2,z):
    """Moment-based asymptotic N for a1=+a versus -a (not optimal)."""
    if z<=0 or a1==0:raise ValueError("bad contrast")
    return math.ceil(z*z*(2+a2-a1*a1)/(2*abs(a1))**2)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mass",type=float,nargs="+",default=DEFAULT_M)
    ap.add_argument("--tanbeta-reference",type=float,default=3.)
    ap.add_argument("--output",type=Path,default=
        ROOT/"validation/local_logs/branch_degeneracy_pilot.json")
    args=ap.parse_args()
    if args.tanbeta_reference<=1:ap.error("Reference tanbeta must exceed 1")
    rows=[]
    for m in args.mass:
        row=compare_branches(m,args.tanbeta_reference)
        a1=row["high_branch"]["a1"];a2=row["high_branch"]["a2"]
        row["ideal_moment_sign_hypotheses_N3"]=signal_count_for_sign_discrimination(a1,a2,3.)
        row["ideal_moment_sign_hypotheses_N5"]=signal_count_for_sign_discrimination(a1,a2,5.)
        print(f"M={m:>6g} tanb_low={row['low_branch']['tanbeta']:.12g} "
              f"f00={row['high_branch']['f00']:.9f} "
              f"BRWZ={row['high_branch']['branch_wz_two_channels']:.9f} "
              f"a1_low={row['low_branch']['a1']:+.8f} "
              f"a1_high={a1:+.8f} "
              f"gate={row['mathematical_two_branch_gate']}")
        rows.append(row)
    report={"status":"PASS_SCOPED_MATHEMATICAL" if
            all(x["mathematical_two_branch_gate"]=="PASS" for x in rows)
            else "FAIL_MATHEMATICAL",
            "source":"Forsyth et al 2025 Eqs A.6-A.8 plus 2026 erratum splitting",
            "assumption":"ONLY WZ/Wgamma ground-state decays; common LO wavefunction",
            "physical_tanbeta_less_than_one":"UNKNOWN_NOT_VALIDATED",
            "decay_plane_sign_conventions":"as in theory/joint_angular_interference.md",
            "statistical_assumption":"ideal background-free fully reconstructed moment estimator",
            "points":rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2))
    print("Saved",args.output,report["status"])
    if report["status"]!="PASS_SCOPED_MATHEMATICAL":raise SystemExit(2)

if __name__=="__main__":
    main()
