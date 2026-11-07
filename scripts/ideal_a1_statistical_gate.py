#!/usr/bin/env python3
"""Back-of-envelope *ideal* statistical cost for measured cos(Phi) moment.

For a fully reconstructed, clean, efficiency-one sample distributed as
p(Phi)=(1+a1 cos Phi+a2 cos 2Phi)/(2pi), the unbiased moment estimator
a1hat = 2/N sum cos Phi satisfies:

 Var(a1hat) = (2 + a2 - a1^2)/N.

Therefore an asymptotic z-sigma separation from a1=0 based on THIS
moment estimator requires N >= z^2 (2+a2-a1^2)/a1^2 selected signal events.

This is not optimal-likelihood sensitivity; backgrounds, reconstruction
ambiguities, acceptance, spin mixtures and systematic errors are OMITTED.
No detector-level prediction or lower bound on *all possible* estimators.
"""
import argparse
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import Setup,splitting,f00
from joint_wz_angles import azimuthal_cos1_amplitude,azimuthal_cos2_amplitude

def moment_cost(a1,a2,z):
    if not math.isfinite(a1+a2+z) or z<=0:raise ValueError("Invalid parameters")
    variance_coeff=2+a2-a1*a1
    if variance_coeff<=0:raise ValueError("Unphysical moment variance")
    if a1==0:return math.inf
    return math.ceil((z*z)*variance_coeff/(a1*a1))

def point(m,tb):
    b=Setup(m,splitting(m,tb),"Z")
    a1=azimuthal_cos1_amplitude(b)
    a2=azimuthal_cos2_amplitude(b)
    return {"M":m,"tanbeta":tb,"delta":b.delta,
            "f00":f00(b),"a1":a1,"a2":a2,
            "ideal_selected_N_for_3sigma_nonzero_a1":moment_cost(a1,a2,3),
            "ideal_selected_N_for_5sigma_nonzero_a1":moment_cost(a1,a2,5)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mass",type=float,default=500.)
    ap.add_argument("--tanbeta",type=float,nargs="+",default=[.1,1.,3.,10.])
    ap.add_argument("--output",type=Path,default=
        ROOT/"validation/local_logs/ideal_a1_statistical_gate.json")
    args=ap.parse_args()
    report={"scope":"perfect_fully_reconstructed_signal_only_moment_estimator",
            "not":"detector_sensitivity_or_background_estimate",
            "points":[point(args.mass,t) for t in args.tanbeta]}
    for d in report["points"]:
        print("M",d["M"],"tb",d["tanbeta"],"f00",f"{d['f00']:.6f}",
              "a1",f"{d['a1']:+.6f}","a2",f"{d['a2']:.6f}",
              "selected ideal N(3sigma)",d["ideal_selected_N_for_3sigma_nonzero_a1"],
              "N(5sigma)",d["ideal_selected_N_for_5sigma_nonzero_a1"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2))
    print("Saved",args.output)
    print("These are approximate selected signal event requirements in a clean "
          "perfect-angular-reconstruction sample, NOT collider sensitivity.")

if __name__=="__main__":
    main()
