#!/usr/bin/env python3
"""Scoped tree-level consistency screen for the two LO WZ a1-sign branches.

This is NOT a folded-SUSY spectrum calculation, vacuum test, perturbative
RGE evolution, or a proof of physical model viability. It checks the exact
restricted D-term scalar-doublet mass relation, Yukawa *weak-scale* size,
absolute width differences at fixed |R(0)|², and minimal trilepton-yield
requirements. No detector-level inputs or fictional cross sections.

Source: Forsyth et al., PRD 111 115021 (2025) Sec 3, App A.3,
and PRD 113 079901 (2026) erratum corrected Eq 3.4.
"""
import argparse
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import (
    Setup,MW,MZ,S2,splitting,published_width)
from quirkonium_branch_degeneracy import find_low_branch,model_point
from ideal_a1_statistical_gate import moment_cost

VEV=246.22
TOP_RUNNING=163.0
TOP_POLE=172.5
W_TO_E_MU=0.216
Z_TO_EE_MUMU=0.0673

def domain_point(m,t,mt=TOP_RUNNING):
    delta=splitting(m,t)
    q=(1-t*t)/(1+t*t)
    up,down=(m+delta)/2,(m-delta)/2
    Du=(.5-2*S2/3)*MZ*MZ*q
    Dd=(-.5+S2/3)*MZ*MZ*q
    msoft_u=up*up-Du
    msoft_d=down*down-Dd
    # In the first-generation massless-quark approximation
    # m_uL² - m_dL² = mW² cos(2 beta).
    delta_relation=(up*up-down*down)-MW*MW*q
    yuk=math.sqrt(2)*mt/(VEV*(t/math.hypot(1,t)))
    return {
       "M":m,"tanbeta":t,"cos2beta":q,
       "delta":delta,"mu":up,"md":down,
       "D_up_left_GeV2":Du,"D_down_left_GeV2":Dd,
       "mQ2_from_up_GeV2":msoft_u,
       "mQ2_from_down_GeV2":msoft_d,
       "doublet_residual_GeV2":delta_relation,
       "common_soft_mass_positive":msoft_u>0 and msoft_d>0,
       "tree_doublet_consistency":abs(msoft_u-msoft_d)<1e-8*max(m*m,1),
       "yt_weak_scale_tree_typeII_assumption":yuk,
       "yt_below_sqrt4pi":yuk<math.sqrt(4*math.pi),
       "yt2_over_16pi2":yuk*yuk/(16*math.pi*math.pi),
       "beta_decay_lifetime_estimate_s":(1e-12*(10/abs(delta))**5
          if delta else math.inf),
       "beta_decay_model":"Forsyth 2025 Eq3.5 approximate, not survival probability"
    }

def branch_comparison(m,high=3.,luminosity=3000.,efficiencies=(1.,.3,.1)):
    low=find_low_branch(m,high)
    b0=domain_point(m,low)
    b1=domain_point(m,high)
    ph0=Setup(m,b0["delta"],"gamma")
    ph1=Setup(m,b1["delta"],"gamma")
    z0=Setup(m,b0["delta"],"Z")
    z1=Setup(m,b1["delta"],"Z")
    r0=published_width(ph0,R2=1.)
    r1=published_width(ph1,R2=1.)
    wz0=published_width(z0,R2=1.)
    wz1=published_width(z1,R2=1.)
    relative_widths={"Wgamma_low_over_high_if_same_R2":r0/r1,
                     "WZ_low_over_high_if_same_R2":wz0/wz1}
    a=model_point(m,high)
    a1=a["a1"];a2=a["a2"]
    if a1==0:raise ValueError("No signed-interference contrast")
    variance=2+a2-a1*a1
    requirements={}
    B=a["branch_wz_two_channels"]*W_TO_E_MU*Z_TO_EE_MUMU
    for z in (3,5):
        # Testing two known opposite-a1 hypotheses with the moment
        # estimator a1hat=2*mean(cosPhi). Binary contrast 2*abs(a1).
        n=math.ceil(z*z*variance/(2*abs(a1))**2)
        requirements[str(z)+"sigma"]={
            "ideal_selected_signal_events":n,
            "sigma_prod_effective_fb_by_efficiency":{
               str(eff):n/(luminosity*B*eff) for eff in efficiencies},
            "conditional_on_background_free_full_sign_recovery":True}
    return {
        "M":m,"branches":{"low":b0,"high":b1},
        "same_R2_width_ratios":relative_widths,
        "branching_to_prompt_e_mu_3lnu":B,
        "lumi_fb_inv":luminosity,
        "selected_events_binary_moment":requirements,
        "tree_level_scalar_doublet_gate":("PASS" if all(
            x["tree_doublet_consistency"] and x["common_soft_mass_positive"]
            for x in (b0,b1)) else "FAIL"),
        "tanbeta_low_simplified_erratum_interval":0.1<=low<=10.,
        "actual_fully_consistent_SUSY_UV":"UNKNOWN",
        "beta_decay_vs_cooling":"UNKNOWN",
        "absolute_model_production_xsec":"UNKNOWN",
        "publication_readiness":"NO_GO_UNTIL_UV_AND_YIELD_GATES",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--masses",type=float,nargs="+",default=[250,500,1000,2000])
    p.add_argument("--high-tanbeta",type=float,default=3.)
    p.add_argument("--luminosity",type=float,default=3000.)
    p.add_argument("--output",type=Path,default=ROOT/
      "validation/local_logs/model_domain_and_yield_gate.json")
    args=p.parse_args()
    if args.high_tanbeta<=1 or args.luminosity<=0:
        p.error("Require high tanbeta>1, positive luminosity")
    rows=[branch_comparison(m,args.high_tanbeta,args.luminosity)
          for m in args.masses]
    out={"scope":"tree_level_Dterm_and_ideal_event_requirements_ONLY",
         "not":"UV_consistent_model_or_LHC_sensitivity",
         "mt_reference_running_GeV":TOP_RUNNING,
         "mt_pole_GeV_for_systematic_comparison":TOP_POLE,
         "masses":rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2))
    for item in rows:
        b=item["branches"]
        print(f"M={item['M']:g} Dterm={item['tree_level_scalar_doublet_gate']} "
              f"tanbeta(low,high)=({b['low']['tanbeta']:.8f},"
              f"{b['high']['tanbeta']:.3g}) "
              f"yt(low,mt_running)={b['low']['yt_weak_scale_tree_typeII_assumption']:.4f} "
              f"Gamma(WZ)low/high[R2 equal]={item['same_R2_width_ratios']['WZ_low_over_high_if_same_R2']:.4f} "
              f"minimum sigma_eff(3sigma,100% acc)="
              f"{item['selected_events_binary_moment']['3sigma']['sigma_prod_effective_fb_by_efficiency']['1.0']:.2f} fb")
    print("Saved",args.output,
          "UV viability UNKNOWN; production and reconstruction efficiencies UNKNOWN.")

if __name__=="__main__":
    main()
