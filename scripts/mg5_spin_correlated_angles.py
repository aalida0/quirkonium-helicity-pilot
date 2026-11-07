#!/usr/bin/env python3
"""Independent MG5_aMC 6-leg test of signed WZ decay-plane interference a1.

MG5 process: ul dl~ > w+ z, w+ > e+ ve, z > mu+ mu- (MSSM_SLHA2).
Analytical comparator: fixed scalar 0+ WZ -> e+nu mu+mu- spin density.
Both are evaluated at precisely the same on-shell external 6-particle
four-momenta, independently normalizing the Phi distribution. The FULL
spin-correlated 6-leg amplitude tests interference, not just helicity
squares. It does not reproduce a physical UV model, formation fractions
or detector-level acceptance.

Caveats:
- The 2026 D-term splitting permits two mathematical tanbeta branches.
  Their UV/spectrum viability is UNKNOWN.
- Keep W,Z widths NONZERO in temporary 6-leg cards: they are internal
  resonances here, unlike external W/Z in the older 2->2 study.
- Strict external leg order from the generated subprocess folder:
  ul (incoming), dl~ (incoming), e+ (out), ve (out), mu+ (out), mu- (out).
- If the generated model uses nonzero lepton masses or different leg
  order the kinematics must be amended; STOP rather than force agreement.
- Everything under validation/local_logs is ignored generated output.
"""
import argparse
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import (Setup,MW,MZ,splitting)
from joint_wz_angles import (joint_density,azimuthal_cos1_amplitude,
                              azimuthal_cos2_amplitude)
from mg5_matrix2py_compare import compile_extension,stage_ident_card
from mg5_threshold_preflight import parse_card,replace_card
from mg5_benchmark_grid import compact_card_for_point
from quirkonium_branch_degeneracy import find_low_branch

def boosted_z(p,beta):
    """Boost [E,px,py,pz] along +z with velocity beta (negative for Z)."""
    if abs(beta)>=1:raise ValueError("Invalid boost velocity")
    gamma=1./math.sqrt(1-beta*beta)
    E,x,y,z=p
    return [gamma*(E+beta*z),x,y,gamma*(z+beta*E)]

def inner(p,q):
    return p[0]*q[0]-sum(x*y for x,y in zip(p[1:],q[1:]))

def add(p,q):
    return [x+y for x,y in zip(p,q)]

def six_leg_point(m,tb,cw,cz,phi):
    """Return 6 [E,px,py,pz] in the *generated* MG5 external-leg order."""
    b=Setup(m,splitting(m,tb),"Z")
    if m<=MW+MZ:raise ValueError("WZ channel below threshold")
    if not(-1<=cw<=1 and -1<=cz<=1):raise ValueError("Cosines out of bounds")
    Ew=(m*m+MW*MW-MZ*MZ)/(2*m)
    Ez=m-Ew
    p=math.sqrt(max(0.,Ew*Ew-MW*MW))
    # z_W=+z, x_W=+x, y_W=+y; positive lepton W decay angle.
    # z_Z=-z, x_Z=-x, y_Z=+y; negative lepton Z decay angle.
    sw=math.sqrt(max(0.,1-cw*cw))
    sz=math.sqrt(max(0.,1-cz*cz))
    w_e=[MW/2, MW/2*sw, 0., MW/2*cw]
    w_nu=[MW/2,-MW/2*sw, 0.,-MW/2*cw]
    z_minus=[MZ/2,-MZ/2*sz*math.cos(phi),
             MZ/2*sz*math.sin(phi),-MZ/2*cz]
    z_plus=[MZ/2,-z_minus[1],-z_minus[2],-z_minus[3]]
    eplus=boosted_z(w_e,+p/Ew)
    ve=boosted_z(w_nu,+p/Ew)
    muminus=boosted_z(z_minus,-p/Ez)
    muplus=boosted_z(z_plus,-p/Ez)
    ps=[[b.mu,0.,0.,0.],[b.md,0.,0.,0.],eplus,ve,muplus,muminus]
    incoming=add(ps[0],ps[1])
    outgoing=[sum(ps[k][j] for k in range(2,6)) for j in range(4)]
    for d in range(4):
        if not math.isclose(incoming[d],outgoing[d],
                            abs_tol=5e-8,rel_tol=2e-10):
            raise RuntimeError(f"Six-leg momentum not conserved: {incoming}, {outgoing}")
    for leg,me in zip(ps,(b.mu,b.md,0.,0.,0.,0.)):
        mass2=inner(leg,leg)
        if not math.isclose(mass2,me*me,rel_tol=1e-10,abs_tol=5e-7):
            raise RuntimeError(f"Offshell external leg {leg}: {mass2} vs {me*me}")
    for pair,mass in [((ps[2],ps[3]),MW),((ps[4],ps[5]),MZ)]:
        reconstructed=add(*pair)
        if not math.isclose(inner(reconstructed,reconstructed),mass*mass,
                            rel_tol=1e-10,abs_tol=5e-7):
            raise RuntimeError("Internal W/Z not on shell")
    return ps

def find_generated_process(base):
    model=base/"MG5_UL_DL_WZ_3LNU"
    subs=sorted((model/"SubProcesses").glob("P*/matrix.f"))
    if len(subs)!=1:raise RuntimeError(
        f"Expected one six-leg matrix.f under {model}, got {len(subs)}. "
        "First generate madgraph/mssm_wz_spin_correlated.mg5")
    work=subs[0].parent
    expected="uldlx_wpz_wp_epve_z_mupmum"
    if expected not in work.name:
        raise RuntimeError(f"Generated subprocess name changed: {work.name}; "
            "inspect actual particle ordering before evaluating six-leg vectors")
    source=subs[0].read_text(errors="replace")
    # Generated matrix.f often INCLUDEs nexternal.inc rather than declaring
    # NEXTERNAL=6 literally. Verify all external HELAS wavefunctions instead.
    external={}
    wavefunction=re.compile(
        r"CALL\s+([SIVOT]XXXXX)\s*\(\s*P\(0,\s*(\d+)\)\s*,\s*([^,]+)",
        re.I)
    for found in wavefunction.finditer(source):
        idx=int(found.group(2))
        mass=found.group(3).strip().upper()
        if idx in external:
            # Some MG5 backends have multiple subroutines; do not quietly
            # assume a duplicated external leg is harmless.
            if external[idx]!=mass:raise RuntimeError(
                f"Conflicting external leg {idx} mass args: "
                f"{external[idx]} and {mass}")
        external[idx]=mass
    if set(external)!=set(range(1,7)):
        raise RuntimeError(
            f"Cannot verify all six external wavefunctions in matrix.f: {external}; "
            "inspect actual HELAS calls before claiming a signed angle")
    for idx in range(3,7):
        if external[idx] not in ("ZERO","0D0","0.D0","0.0D+00"):
            raise RuntimeError(
                f"Outgoing lepton leg {idx} uses mass argument "
                f"{external[idx]}, not ZERO. Current 6-leg momenta assume "
                "massless charged leptons and neutrinos.")
    stage_ident_card(model,work)
    return model,work

def make_6leg_card(model,m,tb,w_width,z_width):
    """Copy original generated card, edit only selected physical inputs."""
    orig=model/"Cards/param_card.dat"
    if not orig.is_file():raise RuntimeError(f"Missing generated original SLHA: {orig}")
    b=Setup(m,splitting(m,tb),"Z")
    compact,changes=compact_card_for_point(orig.read_text(),b,tb)
    widths={("DECAY",24):w_width,("DECAY",23):z_width}
    new,changed=replace_card(compact,widths)
    if changed!=set(widths):
        raise RuntimeError("W/Z DECAY widths missing in generated card; do not "
                           "run exactly on shell with Γ=0")
    params,new_widths=parse_card(new)
    if not(0<new_widths.get(24,0) and 0<new_widths.get(23,0)):
        raise RuntimeError("Required nonzero widths missing")
    if any(len(f"{v:.12E}")>20 for v in widths.values()):
        raise RuntimeError("Wide SLHA width field")
    return new,{"W_width":w_width,"Z_width":z_width,
                "incoming_mass_u":b.mu,"incoming_mass_d":b.md}

def build_cases(m,tb,nodes,nphi):
    import numpy as np
    positions,weights=np.polynomial.legendre.leggauss(nodes)
    phis=[(2*math.pi*k/nphi) for k in range(nphi)]
    cases=[]
    for k,phi in enumerate(phis):
        for i,cw in enumerate(positions):
            for j,cz in enumerate(positions):
                cid=f"k{k}_i{i}_j{j}"
                cases.append({"id":cid,"momenta":six_leg_point(
                    m,tb,float(cw),float(cz),phi)})
    return cases,positions.tolist(),weights.tolist(),phis

def coefficients(phi_yields,phis):
    if not phi_yields or len(phi_yields)!=len(phis):
        raise ValueError("Empty/incompatible azimuthal samples")
    norm=sum(phi_yields)
    if norm<=0:raise ValueError("No positive matrix element density")
    a1=2*sum(y*math.cos(x) for y,x in zip(phi_yields,phis))/norm
    a2=2*sum(y*math.cos(2*x) for y,x in zip(phi_yields,phis))/norm
    sin1=2*sum(y*math.sin(x) for y,x in zip(phi_yields,phis))/norm
    return {"a1":a1,"a2":a2,"sin1":sin1,
            "normalized_phi":[v/norm for v in phi_yields]}

def measure_branch(m,tb,base,work,nodes,nphi,w_width,z_width,logdir):
    import hashlib
    code,provenance=make_6leg_card(base/"MG5_UL_DL_WZ_3LNU",
                                    m,tb,w_width,z_width)
    tag=f"M{m:g}_tanbeta{tb:.12g}"
    folder=logdir/tag
    folder.mkdir(parents=True,exist_ok=True)
    card=folder/"param_card_spin_correlated_compact.dat"
    card.write_text(code)
    cases,cosines,weights,phis=build_cases(m,tb,nodes,nphi)
    input_file=folder/"phase_points.json"
    output_file=folder/"six_leg_worker.json"
    input_file.write_text(json.dumps({"cases":cases},indent=2))
    if output_file.exists():output_file.unlink()
    command=[sys.executable,str(ROOT/"scripts/mg5_6leg_worker.py"),
        "--card",str(card.resolve()),"--input",str(input_file.resolve()),
        "--output",str(output_file.resolve())]
    try:
        proc=subprocess.run(command,cwd=work,capture_output=True,text=True,
                            timeout=300)
    except subprocess.TimeoutExpired as err:
        raise RuntimeError(f"Six-leg Fortran worker timed out: {err}") from err
    (folder/"worker.log").write_text("$ "+" ".join(command)+"\n"+
                                    proc.stdout+"\n"+proc.stderr)
    if proc.returncode or not output_file.is_file():
        raise RuntimeError(f"No complete 6-leg Fortran result for {tag}; "
                           f"worker returncode={proc.returncode}, "
                           f"log={folder/'worker.log'}")
    values=json.loads(output_file.read_text())
    if values.get("status")!="EVALUATED" or values.get("n_returned")!=len(cases):
        raise RuntimeError("Fortran worker did not evaluate all angular samples")
    received={x["id"]:x["ME2"] for x in values["values"]}
    if len(received)!=len(cases):raise RuntimeError("Repeated or missing angular IDs")
    b=Setup(m,splitting(m,tb),"Z")
    mg_yields=[]
    theory_yields=[]
    for k,phi in enumerate(phis):
        mg_acc=theory_acc=0.
        for i,cw in enumerate(cosines):
            for j,cz in enumerate(cosines):
                weight=weights[i]*weights[j]
                mg_acc+=weight*received[f"k{k}_i{i}_j{j}"]
                theory_acc+=weight*joint_density(b,cw,cz,phi)
        mg_yields.append(mg_acc)
        theory_yields.append(theory_acc)
    mg=coefficients(mg_yields,phis)
    ana_num=coefficients(theory_yields,phis)
    ana_closed={
       "a1":azimuthal_cos1_amplitude(b),
       "a2":azimuthal_cos2_amplitude(b),
    }
    maximum=max(abs(x-y) for x,y in zip(mg["normalized_phi"],
                                        ana_num["normalized_phi"]))
    report={"M":m,"tanbeta":tb,"delta":b.delta,
        "num_cos_nodes":nodes,"num_phi_samples":nphi,
        "n_me_evaluations":len(cases),
        "compact_card":str(card),"compact_card_sha256":
            hashlib.sha256(code.encode()).hexdigest(),
        "widths":provenance,
        "mg5_moments":mg,"analytic_numerical_quadrature":ana_num,
        "analytic_closed_moments":ana_closed,
        "max_phi_fraction_abs_diff":maximum,
        "a1_signed_difference":mg["a1"]-ana_num["a1"],
        "a2_difference":mg["a2"]-ana_num["a2"],
        "phase_external_status":("PASS_DIFFERENTIAL_SHAPE_SCOPED"
            if maximum<=2e-5 and
               abs(mg["a1"]-ana_num["a1"])<2e-4 and
               abs(mg["a2"]-ana_num["a2"])<2e-4 else
            "FAIL_DIFFERENTIAL_SHAPE"),
        "relative_complex_amplitude_directly_extracted":False}
    (folder/"comparison.json").write_text(json.dumps(report,indent=2))
    print(f"BRANCH tanbeta={tb:.12g} MG5 a1={mg['a1']:+.8f} "
          f"analytic quadrature a1={ana_num['a1']:+.8f} "
          f"analytic closed a1={ana_closed['a1']:+.8f}; "
          f"max |Δfraction|={maximum:.3g}; "
          f"{report['phase_external_status']}",flush=True)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mass",type=float,default=500.)
    p.add_argument("--tanbeta-high",type=float,default=3.)
    p.add_argument("--nodes",type=int,default=10)
    p.add_argument("--phis",type=int,default=8)
    p.add_argument("--w-width",type=float,default=2.085)
    p.add_argument("--z-width",type=float,default=2.4952)
    p.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    args=p.parse_args()
    if args.mass<=MW+MZ or args.tanbeta_high<=1 or args.nodes<4 or args.phis<8:
        p.error("Need WZ above threshold, high tanbeta>1, >=4 nodes and >=8 phis")
    if args.w_width<=0 or args.z_width<=0:p.error("W/Z widths must be nonzero")
    base=args.root.resolve()
    model,work=find_generated_process(base)
    outdir=base/"threshold_benchmarks"/"spin_correlated_3lnu"
    outdir.mkdir(parents=True,exist_ok=True)
    compile_extension(work,outdir)
    tb_low=find_low_branch(args.mass,args.tanbeta_high)
    report={"generated_at":datetime.now(timezone.utc).isoformat(),
            "model":"MG5 MSSM_SLHA2 generated resonance decay chain",
            "scope":"tree_level_on_shell_spin_correlated_shape_only",
            "mass":args.mass,"high_tanbeta":args.tanbeta_high,
            "low_tanbeta":tb_low,"branches":{},
            "paper_novelty":"UNKNOWN","low_tanbeta_physical_viability":"UNKNOWN",
            "detector_sensitivity":"NOT_APPLICABLE"}
    for name,tb in (("low",tb_low),("high",args.tanbeta_high)):
        report["branches"][name]=measure_branch(
            args.mass,tb,base,work,args.nodes,args.phis,args.w_width,
            args.z_width,outdir)
    low=report["branches"]["low"];high=report["branches"]["high"]
    x=low["mg5_moments"]["a1"]
    y=high["mg5_moments"]["a1"]
    report["opposite_sign_measured"]=(x>0 and y<0)
    report["opposite_sign_magnitude_consistency"]=abs(x+y)
    report["status"]=(
        "PASS_MODEL_SPECIFIC_A1_SIGN_SCOPED" if
        report["opposite_sign_measured"] and
        abs(x+y)<3e-3 and
        all(c["phase_external_status"]=="PASS_DIFFERENTIAL_SHAPE_SCOPED"
            for c in report["branches"].values())
        else "FAIL_OR_INCONCLUSIVE")
    result_path=outdir/"summary.json"
    result_path.write_text(json.dumps(report,indent=2))
    print("FINAL",report["status"],"saved",result_path)
    if report["status"]!="PASS_MODEL_SPECIFIC_A1_SIGN_SCOPED":
        raise SystemExit(2)

if __name__=="__main__":
    main()
