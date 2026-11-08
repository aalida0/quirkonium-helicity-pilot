#!/usr/bin/env python3
"""FCC-hh / HE-LHC PDF-weighted longitudinal-boost neutrino-pz toy.

Source LO production: Forsyth et al PRD111 115021 (2025), App A.2.
Spin-correlated on-shell W+Z -> e+ nu mu+ mu- decay:
  quirkonium_neutrino_pz_gate.py (validated analytic toy).

Crucial distinction:
  - The PDF weighting computes RAPIDITY OF THE INITIALLY PRODUCED
    squirk-pair CM: y=0.5*log(x1/x2).
  - It is NOT necessarily the final ground-state quirkonium boost:
    infracolor deexcitation recoil, ISR and beta decay are absent.
  - The weighted W+ angle result is an *ideal conditional* pilot.
    W- requires separate CP-conjugate lepton-angle validation.
  - Do not call this a detector sensitivity or a guaranteed signal yield.

Use a rapidity-factorized independent PDF integration:
  t=ln(x1*x2) from ln(M²/s) to -2|y|,
  y=1/2 ln(x1/x2) from -ln(sqrt(s)/M) to +ln(sqrt(s)/M).
  d x1 d x2 f1 f2 == d t d y [x1*f1][x2*f2].
This integral is cross-checked against the EXISTING independent
triangular (ln x1, ln x2) LO PDF convolution in the production script.

The moment integral is deterministic and MEMORY-STREAMED. An increase
in angular nodes or PDF rapidity nodes is not guaranteed to improve
a discontinuous smaller-|p_z| root selection monotonically; compare
at least two resolutions and do not call it converged otherwise.

Example:
  python scripts/quirkonium_fcc_pdf_rapidity_gate.py \
    --pdf-set MSTW2008lo68cl --scenarios 85:20000 100:30000 \
    --mass 500 --polar-nodes 5 --phis 12 --orientations 5 \
    --rapidity-nodes 24 --shat-nodes 40 \
    --output /data/aalida/quirkonium-production/fcc_pdf_rapidity_pilot.json

This may need time on AF because every angular point reconstructs two
neutrino roots. No generator, Athena, Delphes or MG5 needed.
"""
import argparse
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from quirkonium_production_pdf_gate import (
    partonic_fb, channels, pdf_convolution)
from quirkonium_neutrino_pz_gate import run_one, sign_cost
from quirkonium_branch_degeneracy import find_low_branch, model_point
from scalar_threshold_amplitudes import splitting

W_TO_E_MU_NU=0.216
Z_TO_EE_MUMU=0.0673

def rapidity_pdf_quadrature(pdf,sqrts,mass,delta,Q,n_y=24,n_u=40,
                           flavor_mode="full-ckm"):
    """Integral with explicit y nodes, differential W+/W- charge rates.

    The d t d y Jacobian is unity, not 1/2. The integrand uses
    LHAPDF's x*f(x,Q), not f(x,Q). Both orientations of the
    SAME incoming quarks in a pp collision are included exactly once.
    """
    import numpy as np
    if (n_y<8 or n_u<8 or mass<=0 or mass>=sqrts or
        abs(delta)>=mass or Q<=0):
        raise ValueError("Invalid rapidity/source phase space")
    y_max=math.log(sqrts/mass)
    t_min=-2*y_max
    yn,yw=np.polynomial.legendre.leggauss(n_y)
    un,uw=np.polynomial.legendre.leggauss(n_u)
    allowed_flavors=channels(flavor_mode)
    cache={}
    def xf(pid,x):
        key=(pid,x)
        if key not in cache:
            v=float(pdf.xfxQ(pid,x,Q))
            if not math.isfinite(v):
                raise RuntimeError("Nonfinite PDF x*f(x)")
            cache[key]=v
        return cache[key]
    nodes=[]
    for y_unit,wy_unit in zip(yn,yw):
        y=float(y_unit)*y_max
        wy=float(wy_unit)*y_max
        t_max=-2*abs(y)
        dt=(t_max-t_min)/2
        center=(t_min+t_max)/2
        Wp=0.; Wm=0.
        for u_unit,wu_unit in zip(un,uw):
            t=center+dt*float(u_unit)
            x1=math.exp(.5*t+y)
            x2=math.exp(.5*t-y)
            if not (0.<x1<1. and 0.<x2<1.):
                raise RuntimeError(f"Partonic x out of (0,1): x1={x1} x2={x2}")
            shat=sqrts*sqrts*x1*x2
            kernel=wy*dt*float(wu_unit)*partonic_fb(shat,mass,delta)
            if kernel==0:continue
            plus=minus=0.
            for up,down,V2 in allowed_flavors:
                # Per charge: both proton-beam assignments (q1 qbar2
                # and qbar1 q2). Different charges have different PDFs.
                plus+=V2*(xf(up,x1)*xf(-down,x2)+
                          xf(-down,x1)*xf(up,x2))
                minus+=V2*(xf(down,x1)*xf(-up,x2)+
                           xf(-up,x1)*xf(down,x2))
            Wp+=kernel*plus
            Wm+=kernel*minus
        nodes.append({"pair_y":y,"wplus_fb":Wp,"wminus_fb":Wm,
                      "charged_sum_fb":Wp+Wm})
    wplus=sum(row["wplus_fb"] for row in nodes)
    wminus=sum(row["wminus_fb"] for row in nodes)
    if wplus<=0 or wminus<=0:
        raise RuntimeError("Non-positive charged production integral")
    # Identical proton beams imply an exactly even rapidity
    # distribution *for each charge separately*; this is a powerful
    # internal check against mixing W+ and W- or dropping a beam.
    def symmetry(name):
        errors=[abs(a[name]-b[name]) for a,b in zip(nodes,reversed(nodes))]
        return max(errors)/max(sum(row[name] for row in nodes)/len(nodes),1e-20)
    return {"sqrt_s_GeV":sqrts,"mass_GeV":mass,"delta_GeV":delta,
            "scale_GeV":Q,"flavor_mode":flavor_mode,
            "rapidity_max_abs":y_max,"rapidity_nodes":n_y,
            "log_shat_nodes":n_u,"wplus_fb":wplus,"wminus_fb":wminus,
            "charged_sum_fb":wplus+wminus,
            "max_pp_beam_evenness_rel_to_mean":{
                key:symmetry(key) for key in ("wplus_fb","wminus_fb")},
            "nodes":nodes}

def mode_rapidity_weights(spectrum,charge_mode):
    key={"wplus":"wplus_fb",
         "both_cp_assumed":"charged_sum_fb"}[charge_mode]
    y=[node["pair_y"] for node in spectrum["nodes"]]
    raw=[node[key] for node in spectrum["nodes"]]
    total=sum(raw)
    if total<=0 or any(w<0 for w in raw):
        raise RuntimeError("Need nonnegative, positive-total PDF rapidity weights")
    return y,[w/total for w in raw],total

def analyze_scenario(pdf,sqrts_tev,lumi_fb,mass,high_tb,polar,phis,
                     orientations,y_nodes,u_nodes,ref_nodes,
                     flavor_mode,charge_mode,scale_ratio):
    sqrt_s=sqrts_tev*1000.
    low_tb=find_low_branch(mass,high_tb)
    cases={"low":low_tb,"high":high_tb}
    physics={}
    for name,t in cases.items():
        delta=splitting(mass,t)
        spectrum=rapidity_pdf_quadrature(
            pdf,sqrt_s,mass,delta,mass*scale_ratio,y_nodes,
            u_nodes,flavor_mode)
        # Different coordinate factorization: this must reproduce
        # the earlier user-validated integrated cross section.
        crosscheck=pdf_convolution(
            pdf,sqrt_s,mass,delta,mass*scale_ratio,ref_nodes,
            flavor_mode)
        ref=crosscheck["charged_sum_fb"]
        ratio=abs(spectrum["charged_sum_fb"]-ref)/max(ref,1e-20)
        positions,weights,charged_rate=mode_rapidity_weights(
            spectrum,charge_mode)
        if ratio>0.02:
            raise RuntimeError(
                f"PDF rapidity / original total disagreement "
                f"{ratio:.2%} for {sqrts_tev}TeV {name}; "
                "do not trust the angular result")
        row=run_one(mass,t,polar,phis,orientations,
                    positions,rapidity_weights=weights)
        physics[name]={
            "tanbeta":t,"delta_GeV":delta,
            "pdf_source_rate":spectrum,
            "crosscheck_earlier_ln_x_integration":crosscheck,
            "relative_total_rate_disagreement":ratio,
            "selected_charge_raw_sigma_fb":charged_rate,
            "charge_mode":charge_mode,
            "moments":row}
    # Use a single physical W+ channel by default. Combining W-
    # assumes the appropriate CP-conjugate sign convention and
    # therefore is explicitly conditional until amplitude validated.
    BR=model_point(mass,high_tb)["branch_wz_two_channels"]
    decay_B=BR*W_TO_E_MU_NU*Z_TO_EE_MUMU
    significance={}
    for label in ("truth","min_abs_pz",
                  "known_resonance_mass","equal_roots"):
        lo=physics["low"]["moments"]
        hi=physics["high"]["moments"]
        for_z={}
        for z in (3,5):
            n=sign_cost(lo,hi,label,z)
            requirements={}
            for name in ("low","high"):
                sigma=physics[name]["selected_charge_raw_sigma_fb"]
                requirements[name]=n/(lumi_fb*decay_B*sigma)
            for_z[str(z)]={
                "ideal_signal_selected_events":n,
                "required_Psurvival_times_eff_by_branch":requirements,
                "worst_branch_minimum_product":max(requirements.values()),
                "necessary_condition_Psurv_eff_1":all(
                    a<=1. for a in requirements.values())}
        significance[label]={
          "delta_a1":lo[label]["a1"]-hi[label]["a1"],
          "3sigma":for_z["3"],"5sigma":for_z["5"]}
    result={"sqrt_s_TeV":sqrts_tev,"luminosity_fb_inv":lumi_fb,
            "M_GeV":mass,"high_tanbeta":high_tb,
            "low_tanbeta":low_tb,
            "charge_mode":charge_mode,"wminus_angular_CP_validation":(
                "NOT_DONE" if charge_mode=="both_cp_assumed"
                else "NOT_INCLUDED_IN_WPLUS_ONLY"),
            "angular_grid":{"polar_nodes":polar,"phis":phis,
                            "orientation_nodes":orientations},
            "model_for_parent_longitudinal_boost":
                "initial squirk-pair y from LO collinear PDFs; "
                "NOT final resonance after infracolor cooling",
            "pdf_reference_total_check_tolerance":.02,
            "groundstate_WZ_two_channel_BR":BR,
            "WZ_leptonic_BR_product":decay_B,
            "min_pz_reconstruction_exact_MET_only":True,
            "analysis_not_background_aware":True,
            "actual_charged_survival":"UNKNOWN",
            "physical_low_tanbeta_UV":"UNKNOWN",
            "branches":physics,
            "sign_discrimination":significance}
    print(f"=== {sqrts_tev:g} TeV, L={lumi_fb:g} fb^-1, "
          f"charge={charge_mode} ===")
    for name in ("low","high"):
        item=physics[name]
        print(name,"tanbeta",f"{item['tanbeta']:.8g}",
              "sigma_selected_charge",f"{item['selected_charge_raw_sigma_fb']:.5g}",
              "sigma_charge_sum",f"{item['pdf_source_rate']['charged_sum_fb']:.5g}",
              "vs triangular PDF rate",
              f"{item['relative_total_rate_disagreement']:.3%}",
              "truth a1",f"{item['moments']['truth']['a1']:+.6f}",
              "min|pz| a1",f"{item['moments']['min_abs_pz']['a1']:+.6f}",
              "root correct",
              f"{item['moments']['minpz_correct_fraction']:.3f}")
    for label in ("truth","min_abs_pz","known_resonance_mass",
                  "equal_roots"):
        row=significance[label]
        g=row["3sigma"]
        print(label,"delta a1",f"{row['delta_a1']:+.6f}",
              "3sigma N",g["ideal_signal_selected_events"],
              "required Psurv*eps worst branch",
              f"{g['worst_branch_minimum_product']:.5g}",
              "NECESSARY_LO_EVENT_GATE",
              ("PASS" if g["necessary_condition_Psurv_eff_1"] else "FAIL"))
    return result

def parse_scenarios(entries):
    result=[]
    for item in entries:
        parts=item.split(":")
        if len(parts)!=2:raise ValueError("Scenarios must look like 85:20000")
        tev,lum=float(parts[0]),float(parts[1])
        if tev<=1 or lum<=0 or not math.isfinite(tev+lum):
            raise ValueError("Nonpositive or nonfinite energy/luminosity")
        result.append((tev,lum))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf-set",required=True)
    p.add_argument("--pdf-member",type=int,default=0)
    p.add_argument("--scenarios",nargs="+",default=["85:20000","100:30000"],
                   help="Collider energy in TeV : integrated L in fb^-1")
    p.add_argument("--mass",type=float,default=500.)
    p.add_argument("--tanbeta-high",type=float,default=3.)
    p.add_argument("--polar-nodes",type=int,default=5)
    p.add_argument("--phis",type=int,default=12)
    p.add_argument("--orientations",type=int,default=5)
    p.add_argument("--rapidity-nodes",type=int,default=24)
    p.add_argument("--shat-nodes",type=int,default=40)
    p.add_argument("--reference-nodes",type=int,default=72,
                   help="Independent x1,x2 triangular-convolution check")
    p.add_argument("--flavor-mode",choices=("ud","full-ckm"),
                   default="full-ckm")
    p.add_argument("--charge-mode",choices=("wplus","both_cp_assumed"),
                   default="wplus",
                   help="W+ only is source-matched to the validated angle "
                        "definition; sum W+- assumes unvalidated CP mapping")
    p.add_argument("--scale-ratio",type=float,default=1.)
    p.add_argument("--output",type=Path,default=ROOT/
         "validation/local_logs/fcc_pdf_rapidity_gate.json")
    args=p.parse_args()
    scenarios=parse_scenarios(args.scenarios)
    if (args.mass<=200 or args.tanbeta_high<=1 or
        args.polar_nodes<3 or args.phis<8 or args.orientations<3 or
        args.rapidity_nodes<8 or args.shat_nodes<8 or
        args.reference_nodes<8 or args.scale_ratio<=0 or
        any(tev*1000<=args.mass for tev,lum in scenarios)):
        p.error("Invalid model/collider/integration parameters")
    try:import lhapdf
    except ImportError as e:
        raise SystemExit("BLOCKED_LHAPDF: first source Key4HEP "
                         "and configure LHAPDF_DATA_PATH") from e
    try:pdf=lhapdf.mkPDF(args.pdf_set,args.pdf_member)
    except Exception as e:
        raise SystemExit(f"BLOCKED_PDF_SET: {e}") from e
    report={"source":"Forsyth et al PRD111 115021 (2025), App A.2",
            "PDF":args.pdf_set,"member":args.pdf_member,
            "alpha_and_EW_scheme":"existing scalar_threshold_amplitudes",
            "CKM_mode":args.flavor_mode,
            "Q_over_M":args.scale_ratio,
            "charge_mode":args.charge_mode,
            "source_color_normalization_audit":"PENDING",
            "physical_deexcitation_recoil":"NOT_SIMULATED",
            "full_pp_ISR":"NOT_SIMULATED",
            "SM_WZ_background":"NOT_CALCULATED",
            "fiducial_selection":"NOT_APPLIED",
            "Wminus_angular_validation":"NOT_DONE",
            "numerical_grid_convergence":
                "NOT_PROVEN_BY_ONE_RUN; repeat polar/phi and rapidity grids",
            "scenarios":[]}
    for tev,lumi in scenarios:
        report["scenarios"].append(
            analyze_scenario(pdf,tev,lumi,args.mass,args.tanbeta_high,
                             args.polar_nodes,args.phis,args.orientations,
                             args.rapidity_nodes,args.shat_nodes,
                             args.reference_nodes,args.flavor_mode,
                             args.charge_mode,args.scale_ratio))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False))
    print("SAVED",args.output)
    print("STATUS: PDF_WEIGHTED_INITIAL_PAIR_RAPIDITY_PILOT_ONLY; "
          "not a final resonance-boost, survival or collider forecast.")

if __name__=="__main__":
    main()
