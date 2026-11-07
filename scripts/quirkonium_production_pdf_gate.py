#!/usr/bin/env python3
"""Paper-matched LO charged-squirk pair production via PDFs (NOT final yield).

Source: Forsyth et al., PRD 111 (2025) 115021, Appendix A.2, Eqs A.2-A.3.
The formula is for W*-mediated SM-color-singlet squirk-pair production,
NOT for QCD-squark production or a 2->1 on-shell resonance.

PDF integration requires installed Python LHAPDF + PDF set; no downloads.
The source rate is a *ceiling* for a charged bound-state signal, BEFORE
unknown deexcitation-vs-beta-decay survival, WZ BR and acceptance.
Default CKM flavor extension is explicitly not the displayed ud-only Eq A2.
No extra hidden-color multiplier is applied (source convention to audit).

Example:
 python scripts/quirkonium_production_pdf_gate.py --pdf-set MSTW2008lo68cl
"""
import argparse
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import MW, ALPHA_W, splitting
from quirkonium_branch_degeneracy import find_low_branch

FB_PER_GEV2=3.893793656e11
# Optional leading CKM 2x3 extension; numerical constants are approximations.
CKM={(2,1):.97373,(2,3):.2243,(2,5):.00382,
     (4,1):.221,(4,3):.975,(4,5):.0410}

def partonic_fb(shat,mass,delta):
    """The published partonic sigma, in fb; one incoming flavor process."""
    if not all(math.isfinite(a) for a in (shat,mass,delta)):
        raise ValueError("nonfinite kinematics")
    if mass<=0 or shat<=mass*mass or abs(delta)>=mass:
        return 0.
    beta_squared=(1-mass*mass/shat)*(1-delta*delta/shat)
    if beta_squared<=0:return 0.
    return FB_PER_GEV2*ALPHA_W**2*math.pi/(32*shat) * (
        beta_squared**1.5)/(1-MW*MW/shat)**2

def channels(flavor_mode):
    if flavor_mode=="ud":
        return [(2,1,1.)]
    if flavor_mode=="full-ckm":
        return [(up,down,v*v) for (up,down),v in CKM.items()]
    raise ValueError("unknown flavor mode")

def pdf_convolution(pdf,sqrts,mass,delta,Q,n=64,flavor_mode="full-ckm"):
    """Gauss 2D convolution with x_i in (0,1),  x1*x2>=tau.

    y_i=ln(x_i); dxi fi(xi)=dyi * xi*fi(xi).
    Includes BOTH pp beam assignments and W+, W-; records each charge.
    """
    import numpy as np
    if n<8 or sqrts<=mass or mass<=abs(delta) or Q<=0:
        raise ValueError("invalid convolution range")
    xi,weights=np.polynomial.legendre.leggauss(n)
    logtau=2*math.log(mass/sqrts)
    result={"wplus_fb":0.,"wminus_fb":0.}
    cache={}
    def xf(pid,x):
        key=(pid,x)
        if key not in cache:
            value=float(pdf.xfxQ(pid,x,Q))
            if not math.isfinite(value):
                raise RuntimeError(f"PDF non-finite: pid={pid} x={x}")
            cache[key]=value
        return cache[key]
    for t,wt in zip(xi,weights):
        y1=(1-float(t))*logtau/2
        x1=math.exp(y1)
        weight1=(-logtau/2)*float(wt)
        low2=logtau-y1
        for u,wu in zip(xi,weights):
            y2=(1-float(u))*low2/2
            x2=math.exp(y2)
            weight2=(-low2/2)*float(wu)
            shat=(sqrts*sqrts)*x1*x2
            base=weight1*weight2*partonic_fb(shat,mass,delta)
            if base==0:continue
            plus=minus=0.
            for up,down,V2 in channels(flavor_mode):
                plus+=V2*(xf(up,x1)*xf(-down,x2)+
                          xf(-down,x1)*xf(up,x2))
                minus+=V2*(xf(down,x1)*xf(-up,x2)+
                           xf(-up,x1)*xf(down,x2))
            result["wplus_fb"]+=base*plus
            result["wminus_fb"]+=base*minus
    result["charged_sum_fb"]=result["wplus_fb"]+result["wminus_fb"]
    return result

def ceiling(rate,needed):
    """Necessary condition ONLY for specific background-free cosPhi moment."""
    if needed<=0 or rate<0:raise ValueError("invalid rate comparison")
    return {"raw_LO_charged_pair_fb":rate,
            "required_production_fb_for_user_toy":needed,
            "max_possible_charged_survival":1.,
            "required_survival_times_acceptance":(
                needed/rate if rate>0 else math.inf),
            "necessary_condition_met_if_Psurvival_eff1":rate>=needed,
            "physical_survival":"UNKNOWN",
            "fiducial_efficiency":"UNKNOWN",
            "SM_WZ_background":"UNKNOWN",
            "LHC_sensitivity":"NOT_EVALUATED"}

def make_point(pdf,sqrts,mass,t_high,nlist,mode,needed,scale):
    t_low=find_low_branch(mass,t_high)
    out={}
    for name,t in (("low",t_low),("high",t_high)):
        d=splitting(mass,t)
        integrations=[pdf_convolution(pdf,sqrts,mass,d,mass*scale,n,mode)
                      for n in nlist]
        latest=integrations[-1]
        earlier=integrations[-2]
        drift=abs(latest["charged_sum_fb"]-earlier["charged_sum_fb"])/max(
            latest["charged_sum_fb"],1e-25)
        out[name]={"tanbeta":t,"delta_GeV":d,"convolutions":integrations,
                   "nodes":nlist,"relative_integration_drift":drift,
                   "integration_status":("STABLE_1PCT" if drift<.01
                                          else "NOT_CONVERGED"),
                   "ceiling":ceiling(latest["charged_sum_fb"],needed)}
    out["low_over_high_production"]=(
        out["low"]["convolutions"][-1]["charged_sum_fb"]/
        out["high"]["convolutions"][-1]["charged_sum_fb"])
    out["source_partonic_sign_parity_residual"]=(
        partonic_fb(2*mass*mass,mass,out["low"]["delta_GeV"])-
        partonic_fb(2*mass*mass,mass,-out["low"]["delta_GeV"]))
    return out

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--pdf-set",required=True)
    a.add_argument("--pdf-member",type=int,default=0)
    a.add_argument("--energies",nargs="+",type=float,default=[13.6])
    a.add_argument("--masses",nargs="+",type=float,default=[500.])
    a.add_argument("--tanbeta-high",type=float,default=3.)
    a.add_argument("--nodes",nargs=2,type=int,default=[48,72])
    a.add_argument("--flavor-mode",choices=("ud","full-ckm"),
                   default="full-ckm")
    a.add_argument("--scale-ratio",type=float,default=1.)
    a.add_argument("--required-fb",type=float,default=90.71,
                   help="User's 12x24 ideal simple-moment test; NOT converged")
    a.add_argument("--output",type=Path,default=ROOT/
        "validation/local_logs/charged_squirkonium_LO_production.json")
    args=a.parse_args()
    if args.nodes[0]<8 or args.nodes[1]<=args.nodes[0] or (
            args.tanbeta_high<=1 or args.scale_ratio<=0 or
            args.required_fb<=0):
        a.error("bad numerical/physics settings")
    try:import lhapdf
    except ImportError as err:
        raise SystemExit(
          "BLOCKED_PDF_DEPENDENCY: missing Python LHAPDF. "
          "This does not imply zero production. Check local lhapdf-config, "
          "lhapdf ls, and the active Python environment.") from err
    try:pdf=lhapdf.mkPDF(args.pdf_set,args.pdf_member)
    except Exception as err:
        raise SystemExit("BLOCKED_PDF_SET: PDF set/member not installed "
          "or bindings incompatible: "+str(err)) from err
    result={"source":"Forsyth et al PRD111 115021 (2025), Eqs A2-A3",
            "PDF":args.pdf_set,"member":args.pdf_member,
            "mode":args.flavor_mode,"CKM_approx":(
                CKM if args.flavor_mode=="full-ckm" else None),
            "extra_hidden_color_multiplier":"NONE",
            "infracolor_normalization_source_audit":"PENDING",
            "Q_over_M":args.scale_ratio,
            "charged_survival_vs_beta_decay":"UNKNOWN",
            "no_strong_QCD_pair_production":True,"points":[]}
    for tev in args.energies:
        for mass in args.masses:
            if mass>=tev*1000:a.error("mass above sqrt(s)")
            row=make_point(pdf,tev*1000,mass,args.tanbeta_high,
                           args.nodes,args.flavor_mode,args.required_fb,
                           args.scale_ratio)
            result["points"].append({"sqrt_s_TeV":tev,"M_GeV":mass,**row})
            for name in ("low","high"):
                item=row[name]
                latest=item["convolutions"][-1]
                print(f"sqrt(s)={tev:g} TeV M={mass:g} {name} "
                      f"tanb={item['tanbeta']:.7g} "
                      f"sigma_pair(W±)={latest['charged_sum_fb']:.5g} fb; "
                      f"num_drift={item['relative_integration_drift']:.3%}; "
                      f"required Psurv*eff="
                      f"{item['ceiling']['required_survival_times_acceptance']:.4g}")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2))
    print("SAVED",args.output)
    print("This is NOT sigma(pp->Psi±->3lnu): charged survival, "
          "acceptance and backgrounds remain UNKNOWN.")
    if any(row[key]["integration_status"]!="STABLE_1PCT"
           for row in result["points"] for key in ("low","high")):
        raise SystemExit(2)

if __name__=="__main__":
    main()
