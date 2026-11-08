#!/usr/bin/env python3
"""ONE-SHOT source-matched FCC-hh charged-squirkonium survival feasibility audit.

Runs the full job with one command: numerical/physics selftests, two
FCC-hh scenarios, full LO PDF production, exact Appendix A.1 heavy-squirk
beta width, photon-only Eq. 2.11 deexcitation, Eq. 3.6 survival,
survival-weighted W+ rapidities, and same analytic W+Z spin-correlated
neutrino-pz reconstruction; produces JSON + Markdown report.

Physics source: Forsyth, Low, Tenney, Verhaaren, PRD 111 115021 (2025),
arXiv:2504.02940; Appendix A.1 Eq A.1, Sec II Eq 2.11, Sec III Eq 3.5,
Eq 3.6, Appendix A.2 Eq A.2. Corrected D-term in 2026 erratum.

NO model-independent 3sigma/exclusion/discovery claim:
- beta width Eq A.1 and rough lifetime Eq 3.5 appear grossly different
  numerically for Delta~10 GeV. Both are reported WITHOUT selecting an
  agreement by hand. Physical source consistency is a STOP/REVIEW gate.
- Photon-only cooling: sigma(string)=3.6 Lambda'^2 (GeV^2),
  alpha=1/137.036. No phenomenological glueball energy-loss rate.
- E_T=sqrt(shat) of pair in its CM; final bound-state rapidity is taken
  as pair rapidity. ISR and hidden-radiation recoil are absent.
- Signed decay angles are validated for W+Z only, not W-Z.
- Exact MET, no fiducial lepton cuts or SM WZ backgrounds.
- Infracolor final-color factor in published Eq A.2 not independently
  derived; no arbitrary factor 3 added.
- Low tanbeta weak-scale top Yukawa is only a heuristic, not a UV RGE.
- Angular quadrature with a discontinuous min-|pz| neutrino-root choice
  is not guaranteed converged; output reports scope and grid.
"""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import MW,splitting,Setup
from joint_wz_angles import joint_density,azimuthal_cos1_amplitude
from quirkonium_branch_degeneracy import find_low_branch,model_point
from quirkonium_model_domain_gate import domain_point
from quirkonium_production_pdf_gate import partonic_fb,channels,pdf_convolution
from quirkonium_neutrino_pz_gate import lab_event,reco_angles,sign_cost

GF=1.1663787e-5      # GeV^-2, PDG
ALPHA_EM=1/137.035999084
HBAR_GEV_S=6.582119569e-25
W_LEPTONIC=0.216
Z_LEPTONIC=0.0673

def beta_decay_width_A1(mass,delta,nodes=96):
    """Three-body width [GeV], Eq A.1, for mH-mL=|Delta|<mW.

    The numerator is sqrt[(1-e)(1-delta_norm^2 e)] times
    [4e - (1+delta_norm*e)^2/(1+delta_norm)^2].
    The W propagator correction in the denominator is squared.
    The source notes that the dimensionless integral tends to 2/5
    for delta_norm->0. This is separately unit-tested.
    """
    import numpy as np
    D=abs(float(delta))
    if not (mass>D>0 and D<MW):
        raise ValueError("Eq A.1 requires 0<|Delta|<min(M,mW)")
    dn=D/mass
    k=(D/MW)**2
    xi,wi=np.polynomial.legendre.leggauss(nodes)
    integral=0.
    for x,w in zip(xi,wi):
        e=(float(x)+1)/2
        z=((1+dn*e)/(1+dn))**2
        den=(1-k*z+k*e)**2
        val=(math.sqrt((1-e)*(1-dn*dn*e))*(4*e-z)/den)
        integral+=float(w)*val/2
    gamma=GF*GF*D**5/(6*math.pi**3*(1+dn))*integral
    if gamma<=0 or not math.isfinite(gamma):
        raise RuntimeError("Invalid source Eq A1 beta width")
    return {"Gamma_beta_GeV":gamma,
            "tau_beta_A1_s":HBAR_GEV_S/gamma,
            "dimensionless_A1_integral":integral,
            "A1_quadrature_nodes":nodes,
            "tau_beta_rough_eq3_5_s":1e-12*(10/D)**5,
            "ratio_tau_eq3_5_over_A1":(
                1e-12*(10/D)**5)/(HBAR_GEV_S/gamma)}

def t_deexc_eq2_11_s(mass,delta,et,lam):
    """Photon-only Eq 2.11 upper deexcitation time in seconds.

    sigma is the string tension [GeV^2], NOT a cross section.
    E_T is sqrt(shat), invariant total CM pair energy [GeV].
    """
    if not (mass>abs(delta) and et>=mass and lam>0):
        raise ValueError("Invalid photon deexcitation kinematics")
    sigma_string=3.6*lam**2
    d=(delta/mass)**2
    t_gevinv=(3*mass**3/(64*math.pi*ALPHA_EM*sigma_string**2)
              *(et/mass-1)*(1-d)**2/(1+d))
    return t_gevinv*HBAR_GEV_S

def survival(et,mass,delta,lam,tau_beta):
    if not (tau_beta>0):raise ValueError("Positive beta lifetime required")
    t=t_deexc_eq2_11_s(mass,delta,et,lam)
    return math.exp(-t/tau_beta)

def numerical_selfchecks():
    """Independent physical identities, no LHAPDF required."""
    import numpy as np
    # A1 integral ->2/5 when BOTH delta/M and Delta/mW vanish.
    # Holding Delta=10 GeV while M->infinity leaves a finite
    # W-propagator correction and does NOT approach the claimed 2/5.
    for n in (64,96):
        b=beta_decay_width_A1(1e7,.01,n)
        if abs(b["dimensionless_A1_integral"]-.4)>.00005:
            raise AssertionError("A1 small-delta integral does not approach 2/5")
    # Cross section is even in mass splitting, cooling and lifetime too.
    for shat in (1e6,2e6):
        assert partonic_fb(shat,500.,9.4)==partonic_fb(shat,500.,-9.4)
    assert t_deexc_eq2_11_s(500,10,500,5)==0
    assert 0<survival(1000,500,10,5,1e-17)<1
    assert survival(1000,500,10,10,1e-17)>survival(1000,500,10,2,1e-17)
    # Source's beta lifetime and rough scaling are not silently equated:
    b=beta_decay_width_A1(1000.,10.,96)
    if b["ratio_tau_eq3_5_over_A1"]<100:
        raise AssertionError("Expected explicit source-lifetime tension vanished")
    return {"status":"PASS_SCOPED_NUMERICAL_IDENTITIES",
            "small_delta_integral_limit":0.4,
            "A1_reference_at_M1000_Delta10":b,
            "rough_Eq3_5_inconsistent_with_A1":True}

def rapidity_survival_convolution(pdf,sqrts,mass,delta,Q,lambdas,
                                  ny=40,nu=64,flavor_mode="full-ckm",
                                  beta_nodes=96):
    """Physically weight raw and survived W+/W- pair rates over x1,x2.

    Transform t=ln(x1*x2), y=.5ln(x1/x2):
      d x1 d x2 f1 f2 = dt dy (x1 f1)(x2 f2).
    Each rapidity row is integrated over its allowed t interval.
    For every Lambda, apply photon-only survival P(sqrt(shat)).
    """
    import numpy as np
    if mass>=sqrts or ny<8 or nu<8:
        raise ValueError("Invalid collider/numerical settings")
    bet=beta_decay_width_A1(mass,delta,beta_nodes)
    yminmax=math.log(sqrts/mass)
    low_t=-2*yminmax
    ys,yws=np.polynomial.legendre.leggauss(ny)
    us,uws=np.polynomial.legendre.leggauss(nu)
    fch=channels(flavor_mode)
    cache={}
    def xf(pid,x):
        key=(pid,x)
        if key not in cache:
            v=float(pdf.xfxQ(pid,x,Q))
            if not math.isfinite(v):raise RuntimeError("Nonfinite PDF")
            cache[key]=v
        return cache[key]
    grid=[]
    for yi,wyi in zip(ys,yws):
        y=float(yi)*yminmax
        weight_y=float(wyi)*yminmax
        upper_t=-2*abs(y)
        half=(upper_t-low_t)/2
        mid=(upper_t+low_t)/2
        entry={"y":y,"raw_wplus_fb":0.,"raw_wminus_fb":0.,
               "surv_wplus_fb":{str(lam):0. for lam in lambdas},
               "surv_wminus_fb":{str(lam):0. for lam in lambdas}}
        for ui,wui in zip(us,uws):
            t=mid+half*float(ui)
            x1=math.exp(.5*t+y);x2=math.exp(.5*t-y)
            shat=sqrts*sqrts*x1*x2
            kernel=weight_y*half*float(wui)*partonic_fb(
                shat,mass,delta)
            if kernel==0:continue
            plus=minus=0.
            for up,down,ckm2 in fch:
                plus+=ckm2*(xf(up,x1)*xf(-down,x2)+
                            xf(-down,x1)*xf(up,x2))
                minus+=ckm2*(xf(down,x1)*xf(-up,x2)+
                             xf(-up,x1)*xf(down,x2))
            raw_p=kernel*plus
            raw_m=kernel*minus
            entry["raw_wplus_fb"]+=raw_p
            entry["raw_wminus_fb"]+=raw_m
            et=math.sqrt(shat)
            for lam in lambdas:
                sval=survival(et,mass,delta,lam,bet["tau_beta_A1_s"])
                entry["surv_wplus_fb"][str(lam)]+=raw_p*sval
                entry["surv_wminus_fb"][str(lam)]+=raw_m*sval
        grid.append(entry)
    raw_wp=sum(e["raw_wplus_fb"] for e in grid)
    raw_wm=sum(e["raw_wminus_fb"] for e in grid)
    if min(raw_wp,raw_wm)<=0:
        raise RuntimeError("No positive raw production")
    summary={}
    for lam in lambdas:
        key=str(lam)
        wp=sum(e["surv_wplus_fb"][key] for e in grid)
        wm=sum(e["surv_wminus_fb"][key] for e in grid)
        summary[key]={"surv_wplus_fb":wp,"surv_wminus_fb":wm,
                      "surv_charge_sum_fb":wp+wm,
                      "Psurvival_integrated_wplus":wp/raw_wp,
                      "Psurvival_integrated_wminus":wm/raw_wm,
                      "Psurvival_integrated_charge_sum":(
                          (wp+wm)/(raw_wp+raw_wm))}
    if any(e["raw_wplus_fb"]<0 or e["raw_wminus_fb"]<0 for e in grid):
        raise RuntimeError("Negative PDF production weight")
    return {"M_GeV":mass,"delta_GeV":delta,
            "beta_decay":bet,"sqrt_s_GeV":sqrts,"scale_GeV":Q,
            "raw_wplus_fb":raw_wp,"raw_wminus_fb":raw_wm,
            "raw_charge_sum_fb":raw_wp+raw_wm,
            "rapidity_nodes":ny,"log_shat_nodes":nu,
            "rapidities":grid,"lambda_scan":summary}

ANGLE_LABELS=("truth","min_abs_pz","known_resonance_mass","equal_roots")

def build_angular_y_basis(mass,tanbeta,positions,nodes,phis,norient):
    """Calculate per-y W+ decay moment basis ONCE; reuse for ALL lambdas.

    Saves substantial redundant 2->4 reconstruction work compared with
    independently scanning each Lambda through the entire angular grid.
    """
    import numpy as np
    cw,wcw=np.polynomial.legendre.leggauss(nodes)
    cz,wcz=np.polynomial.legendre.leggauss(nodes)
    co,wco=np.polynomial.legendre.leggauss(norient)
    setup=Setup(mass,splitting(mass,tanbeta),"Z")
    basis=[]
    for y in positions:
        basis.append({"total":0.,"minpz_correct":0.,
                      "moments":{name:{"cos":0.,"cos2":0.}
                                 for name in ANGLE_LABELS}})
    maxclosure=0.
    for c,wc in zip(cw,wcw):
        for d,wd in zip(cz,wcz):
            for k in range(phis):
                phi=2*math.pi*k/phis
                dens=joint_density(setup,float(c),float(d),phi)
                if dens<-1e-12:raise RuntimeError("Negative joint decay density")
                for orient,wo in zip(co,wco):
                    theta=math.acos(float(orient))
                    aw=float(wc*wd*wo)*dens*(2*math.pi/phis)/2.
                    for j,y in enumerate(positions):
                        obs=reco_angles(
                            lab_event(mass,tanbeta,float(c),float(d),
                                      phi,theta,y),mass)
                        diff=math.atan2(math.sin(obs["truth"]-phi),
                                        math.cos(obs["truth"]-phi))
                        maxclosure=max(maxclosure,abs(diff))
                        if abs(diff)>1e-8:
                            raise RuntimeError("Truth angle closure broken")
                        r=basis[j]
                        r["total"]+=aw
                        r["minpz_correct"]+=aw*obs["minpz_is_true"]
                        for label in ANGLE_LABELS:
                            if label=="equal_roots":
                                c1=obs["equal_roots_cos"]
                                c2=obs["equal_roots_cos2"]
                            else:
                                ph=obs[label]
                                c1=math.cos(ph);c2=math.cos(2*ph)
                            r["moments"][label]["cos"]+=aw*c1
                            r["moments"][label]["cos2"]+=aw*c2
    return {"basis":basis,
            "max_truth_closure_rad":maxclosure,
            "analytic_closed_a1":azimuthal_cos1_amplitude(setup),
            "grid":{"polar":nodes,"phis":phis,"orientations":norient,
                    "rapidities":len(positions)}}

def mix_angular_basis(basis,weight_array):
    rows=basis["basis"]
    if len(rows)!=len(weight_array) or any(w<0 for w in weight_array):
        raise ValueError("Bad rapidity weights")
    total=sum(row["total"]*w for row,w in zip(rows,weight_array))
    if total<=0:
        return None
    result={}
    for label in ANGLE_LABELS:
        a1=2*sum(
            w*row["moments"][label]["cos"]
            for w,row in zip(weight_array,rows))/total
        a2=2*sum(
            w*row["moments"][label]["cos2"]
            for w,row in zip(weight_array,rows))/total
        result[label]={"a1":a1,"a2":a2,
                       "variance_simple_moment_coefficient":2+a2-a1*a1}
    result["minpz_correct_fraction"]=sum(
        w*row["minpz_correct"] for w,row in zip(weight_array,rows))/total
    result["max_truth_angle_closure_radians"]=basis[
        "max_truth_closure_rad"]
    result["analytic_closed_a1"]=basis["analytic_closed_a1"]
    return result

def run_scenario(pdf,tev,lumi,mass,t_high,lambdas,ny,nu,refnodes,
                 polar,phis,norient,mode):
    t_low=find_low_branch(mass,t_high)
    cases={"low":t_low,"high":t_high}
    blocks={}
    for name,t in cases.items():
        D=splitting(mass,t)
        spectrum=rapidity_survival_convolution(
            pdf,tev*1000,mass,D,mass,lambdas,ny,nu,mode)
        independent=pdf_convolution(
            pdf,tev*1000,mass,D,mass,refnodes,mode)
        rel=abs(spectrum["raw_charge_sum_fb"]-
                independent["charged_sum_fb"])/independent["charged_sum_fb"]
        if rel>.02:
            raise RuntimeError(
                f"{tev}TeV {name}: independent PDF rate closure failed "
                f"({rel:.2%})")
        positions=[r["y"] for r in spectrum["rapidities"]]
        basis=build_angular_y_basis(
            mass,t,positions,polar,phis,norient)
        per_lambda={}
        for lam in lambdas:
            key=str(lam)
            weights=[r["surv_wplus_fb"][key]
                     for r in spectrum["rapidities"]]
            mix=mix_angular_basis(basis,weights)
            per_lambda[key]={"angular":mix,
                             "survival_rate":spectrum["lambda_scan"][key]}
        raw_weight=[r["raw_wplus_fb"] for r in spectrum["rapidities"]]
        blocks[name]={"tanbeta":t,"delta_GeV":D,
                      "tree_level_domain":domain_point(mass,t),
                      "source_integral_vs_independent_relative":rel,
                      "source_pdf":spectrum,
                      "wplus_angular_basis_validation":{
                        key:value for key,value in basis.items()
                        if key!="basis"},
                      "raw_wplus_angular":mix_angular_basis(
                          basis,raw_weight),
                      "lambda":per_lambda}
    both={}
    for lam in lambdas:
        key=str(lam)
        lo=blocks["low"]["lambda"][key]
        hi=blocks["high"]["lambda"][key]
        momlo,momhi=lo["angular"],hi["angular"]
        BR=model_point(mass,t_high)["branch_wz_two_channels"]
        BR3=BR*W_LEPTONIC*Z_LEPTONIC
        outcomes={}
        for lab in ANGLE_LABELS:
            if momlo is None or momhi is None:
                outcomes[lab]={"status":"ZERO_SURVIVED_RATE"}
                continue
            n3=sign_cost(momlo,momhi,lab,3)
            n5=sign_cost(momlo,momhi,lab,5)
            sigL=lo["survival_rate"]["surv_wplus_fb"]
            sigH=hi["survival_rate"]["surv_wplus_fb"]
            possible_L=lumi*BR3*sigL
            possible_H=lumi*BR3*sigH
            if min(possible_L,possible_H)<=0:
                outcomes[lab]={"status":"ZERO_SURVIVED_RATE"}
                continue
            worst=n3/min(possible_L,possible_H)
            outcomes[lab]={
              "delta_a1":momlo[lab]["a1"]-momhi[lab]["a1"],
              "a1_low":momlo[lab]["a1"],
              "a1_high":momhi[lab]["a1"],
              "3sigma_selected_clean_signal_N":n3,
              "5sigma_selected_clean_signal_N":n5,
              "max_prompt_3lnu_no_fiducial_low":possible_L,
              "max_prompt_3lnu_no_fiducial_high":possible_H,
              "minimum_remaining_selection_epsilon_for_3sigma":worst,
              "necessary_no_background_3sigma_epsilon1":worst<=1,
              "physical_significance":"NOT_EVALUATED"}
        both[key]={"BR_ground_WZ_2channels":BR,
                   "prompt_three_lepton_BR":BR3,
                   "outcomes":outcomes}
    print(f"\n=== {tev:g} TeV; L={lumi:g}/fb; W+ ONLY; M={mass:g} GeV ===")
    for name in ("low","high"):
        block=blocks[name]
        b=block["source_pdf"]["beta_decay"]
        print(name,
              f"tanb={block['tanbeta']:.7f} Delta={block['delta_GeV']:+.5f} "
              f"raw sigma(W+)={block['source_pdf']['raw_wplus_fb']:.4g}fb "
              f"pdf closure={block['source_integral_vs_independent_relative']:.3%}")
        print("  A1 tau_beta",f"{b['tau_beta_A1_s']:.4e}s",
              "Eq3.5 rough",f"{b['tau_beta_rough_eq3_5_s']:.4e}s",
              "rough/exact",f"{b['ratio_tau_eq3_5_over_A1']:.4g}",
              "SOURCE_TENSION",
              ("YES" if b["ratio_tau_eq3_5_over_A1"]>10 else "NO"))
    print("Lambda' [GeV] | P_surv_low/high | minpz delta(a1) | "
          "3sigma clean N | required epsilon | gate")
    for lam in lambdas:
        key=str(lam)
        low=blocks["low"]["lambda"][key]["survival_rate"]
        hi=blocks["high"]["lambda"][key]["survival_rate"]
        mom=both[key]["outcomes"]["min_abs_pz"]
        if "3sigma_selected_clean_signal_N" in mom:
            print(f"{lam:>8g} | "
                  f"{low['Psurvival_integrated_wplus']:.4f}/"
                  f"{hi['Psurvival_integrated_wplus']:.4f} | "
                  f"{mom['delta_a1']:+.6f} | "
                  f"{mom['3sigma_selected_clean_signal_N']:>7} | "
                  f"{mom['minimum_remaining_selection_epsilon_for_3sigma']:.5g} | "
                  f"{'PASS_NECESSARY' if mom['necessary_no_background_3sigma_epsilon1'] else 'FAIL_NECESSARY'}")
        else:
            print(f"{lam:>8g} | ZERO_SURVIVAL")
    return {"sqrt_s_TeV":tev,"L_fb_inv":lumi,
            "mass_GeV":mass,"angular_charge_mode":"W+ only",
            "CP_conjugate_Wminus_angle":"NOT_VALIDATED",
            "partonic_E_T":"sqrt_shat",
            "infracolor_alpha_photon":ALPHA_EM,
            "string_tension_relation":"sigma_string=3.6 LambdaPrime^2",
            "physical_model":"folded-SUSY-inspired scalar doublet, "
                             "UV completion NOT validated",
            "source_beta_width_eqA1_vs_rough_eq3_5":
                "NUMERICAL_TENSION_EXPLICITLY_FLAGGED",
            "no_detector":True,"background":"NOT_CALCULATED",
            "fiducial_cuts":"NOT_CALCULATED",
            "final_quirkonium_boost":"initial-pair rapidity inherited, "
                                      "deexcitation/ISR recoil NOT modeled",
            "photon_only_cooling":"upper deexcitation time, no glueballs",
            "angular_numerical_convergence":"NOT_ESTABLISHED",
            "branches":blocks,"lambda_comparison":both}

def write_md(report,filename):
    lines=["# FCC-hh charged scalar quirkonium one-shot survival gate",
           "",f"Source: Forsyth et al., Phys Rev D 111 115021 (2025), "
              "arXiv:2504.02940; 2026 erratum.",
           "", "**IMPORTANT:** These are LO source-inspired, "
           "photon-only, no-detector, W+-only conditional estimates. "
           "No discovery/95% CL claim.",
           "", "## Numerical checks and paper-source tension",
           "", "Internal Eq A.1 small-splitting integral: 2/5; "
           "Eq 3.5 versus Eq A.1 beta lifetime comparison "
           "flagged separately. A large mismatch is a "
           "SOURCE-NORMALIZATION/INTERPRETATION STOP gate.",
           "", "## Scenario and Lambda' scan",
           "",
           "| Energy | Lambda' (GeV) | Psurv low/high | "
           "a1(low)-a1(high), min pz | clean N for 3sigma | "
           "epsilon needed after survival | Necessary gate |",
           "|---|---:|---|---:|---:|---:|---|"]
    for scen in report["scenarios"]:
        for lam in report["lambda_grid_GeV"]:
            key=str(lam)
            low=scen["branches"]["low"]["lambda"][key]["survival_rate"]
            hi=scen["branches"]["high"]["lambda"][key]["survival_rate"]
            row=scen["lambda_comparison"][key]["outcomes"]["min_abs_pz"]
            if "3sigma_selected_clean_signal_N" not in row:continue
            lines.append(f"| {scen['sqrt_s_TeV']:g} TeV | {lam:g} | "
              f"{low['Psurvival_integrated_wplus']:.4g}/"
              f"{hi['Psurvival_integrated_wplus']:.4g} | "
              f"{row['delta_a1']:+.6f} | "
              f"{row['3sigma_selected_clean_signal_N']} | "
              f"{row['minimum_remaining_selection_epsilon_for_3sigma']:.5g} | "
              f"{'PASS necessary only' if row['necessary_no_background_3sigma_epsilon1'] else 'FAIL necessary'} |")
    lines+=["","## Model and publication limitations",
            "",
            "- The true constituent beta lifetime has source-level "
            "tension between Eq A.1 and the rough Eq 3.5; "
            "do not treat these results as certified until resolved.",
            "- W- signed angular convention not validated. "
            "The event count uses **W+ only**, not both charges.",
            "- String cooling is treated semiclassically with "
            "only photon radiation (conservative in source context).",
            "- Pair rapidity is substituted for final resonance rapidity; "
            "ISR and deexcitation recoil omitted.",
            "- No SM WZ continuum, fiducial pT/eta selections, "
            "detector resolution or analysis shape systematics.",
            "- Production Eq A.2 infracolor factor "
            "not independently checked against a model-matched ME.",
            "- Low tanbeta UV spectrum, Higgs constraints and "
            "Yukawa running remain UNKNOWN.",
            "- Root-switching angular integration "
            "convergence NOT established. Numerical tests "
            "do not certify physical sensitivity.",
            "",
            "## Paper decision","",
            "**NO-GO for paper / discovery projection from this run alone.** "
            "Use as a source-exposing quirk dynamics and "
            "minimal event-yield test. Next source audit "
            "must resolve the beta lifetime discrepancy.",
            ""]
    filename.write_text("\n".join(lines))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf-set",default="MSTW2008lo68cl")
    p.add_argument("--pdf-member",type=int,default=0)
    p.add_argument("--scenarios",nargs="+",default=["85:20000","100:30000"])
    p.add_argument("--mass",type=float,default=500.)
    p.add_argument("--tanbeta-high",type=float,default=3.)
    p.add_argument("--lambda-grid",nargs="+",type=float,default=[1.,2.,3.,5.,10.])
    p.add_argument("--rapidity-nodes",type=int,default=40)
    p.add_argument("--shat-nodes",type=int,default=64)
    p.add_argument("--reference-nodes",type=int,default=72)
    p.add_argument("--polar-nodes",type=int,default=8)
    p.add_argument("--phis",type=int,default=16)
    p.add_argument("--orientations",type=int,default=5)
    p.add_argument("--flavor-mode",choices=("ud","full-ckm"),
                   default="full-ckm")
    p.add_argument("--run-tests",action="store_true",
                   help="Execute all repo unit tests before physics")
    p.add_argument("--output",type=Path,default=ROOT/
                   "validation/local_logs/fcc_survival_one_shot.json")
    args=p.parse_args()
    if (args.mass<200 or args.tanbeta_high<=1 or
        min(args.lambda_grid)<=0 or
        args.rapidity_nodes<8 or args.shat_nodes<8 or
        args.reference_nodes<8 or args.polar_nodes<3 or args.phis<8 or
        args.orientations<3):
        p.error("Invalid physical or integration settings")
    if args.run_tests:
        tests=subprocess.run([sys.executable,"-m","unittest","discover",
                              "-s","tests","-v"],cwd=str(ROOT),
                             check=False)
        if tests.returncode:
            raise SystemExit("UNITTEST_FAIL: aborted physics production")
    checks=numerical_selfchecks()
    print("SELFTEST",checks["status"])
    try:import lhapdf
    except ImportError as ex:
        raise SystemExit("BLOCKED_LHAPDF: activate Key4HEP on AF") from ex
    pdf=lhapdf.mkPDF(args.pdf_set,args.pdf_member)
    scen=[]
    for x in args.scenarios:
        parts=x.split(":")
        if len(parts)!=2:p.error("scenarios require TeV:luminosity_fb_inv")
        tev,lumi=(float(q) for q in parts)
        if not (tev>0 and lumi>0 and tev*1000>args.mass):
            p.error("Invalid collider scenario")
        scen.append((tev,lumi))
    if len(set(args.lambda_grid))!=len(args.lambda_grid):
        p.error("Duplicate confinement scales")
    report={"job":"FCC_LO_photon_cooling_beta_decay_survival_and_Wplus_angle",
            "date_label":"2026-11-08",
            "source":"Forsyth et al PRD111 115021 2025 Eqs "
                     "A1 2.11 3.5 3.6 A2",
            "LHAPDF_set":args.pdf_set,"LHAPDF_member":args.pdf_member,
            "lambda_grid_GeV":args.lambda_grid,
            "luminosity_scenarios":scen,
            "input":{"M_GeV":args.mass,"tanbeta_high":args.tanbeta_high,
                     "polar_nodes":args.polar_nodes,"phis":args.phis,
                     "orientations":args.orientations,
                     "rapidity_nodes":args.rapidity_nodes,
                     "shat_nodes":args.shat_nodes,
                     "reference_nodes":args.reference_nodes,
                     "flavor_mode":args.flavor_mode},
            "internal_checks":checks,
            "source_lifetime_consistency":"DISCREPANCY_TO_RESOLVE",
            "absolute_source_color_normalization":"UNKNOWN",
            "glueball_cooling":"NOT_MODELED",
            "SM_WZ_background":"NOT_MODELED",
            "fiducial_detector_acceptance":"NOT_MODELED",
            "low_tanbeta_UV_viability":"UNKNOWN",
            "paper_discovery_reach":"NOT_ESTABLISHED",
            "scenarios":[]}
    for tev,lumi in scen:
        report["scenarios"].append(run_scenario(
            pdf,tev,lumi,args.mass,args.tanbeta_high,args.lambda_grid,
            args.rapidity_nodes,args.shat_nodes,args.reference_nodes,
            args.polar_nodes,args.phis,args.orientations,
            args.flavor_mode))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False))
    summary=args.output.with_suffix(".md")
    write_md(report,summary)
    print("SAVED_JSON",args.output)
    print("SAVED_REPORT",summary)
    print("VERDICT: NUMERICAL_PRODUCTION_RECONSTRUCTION_SCOPED_ONLY; "
          "BETA_LIFETIME_SOURCE_TENSION; MODEL_AND_PAPER_NOT_ESTABLISHED.")

if __name__=="__main__":
    main()
