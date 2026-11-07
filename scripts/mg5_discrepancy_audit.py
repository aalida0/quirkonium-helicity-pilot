#!/usr/bin/env python3
"""Read-only MG5/analytic discrepancy audit for the existing WZ and Wgamma outputs.

Records the actual generated diagrams, color/mixing conventions and SLHA inputs.
Optional --probe evaluates existing matrix2py on the exact threshold, slight
nonzero relative momenta and original unmodified MSSM card. DOES NOT modify
Fortran source, original cards, couplings, color factors or analytic formulas.

A failing benchmark must not be promoted to PASS by rescaling.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import MW,MZ,Setup,splitting
from mg5_threshold_preflight import parse_card,reference
from mg5_matrix2py_compare import (LABELS,prepare,stage_ident_card,
                                  evaluate_in_worker)

def ps_at_relative_q(mu,md,mw,mv,q,angle=.35):
    """On-shell 2->2 CM kinematics with initial scalar 3-momenta +/-q."""
    e1=math.hypot(mu,q)
    e2=math.hypot(md,q)
    ecm=e1+e2
    if ecm <= mw+mv:
        raise ValueError("2-body final state closed")
    ew=(ecm*ecm+mw*mw-mv*mv)/(2*ecm)
    ev=ecm-ew
    pf=math.sqrt(max(0.,ew*ew-mw*mw))
    ps=[[e1,0.,0.,q],[e2,0.,0.,-q],
        [ew,pf*math.sin(angle),0.,pf*math.cos(angle)],
        [ev,-pf*math.sin(angle),0.,-pf*math.cos(angle)]]
    for p,m in zip(ps,[mu,md,mw,mv]):
        mass2=p[0]*p[0]-sum(x*x for x in p[1:])
        if not math.isclose(mass2,m*m,abs_tol=1e-7,rel_tol=1e-9):
            raise ValueError(f"Off-shell input {p}: {mass2} != {m*m}")
    for j in range(4):
        if abs(ps[0][j]+ps[1][j]-ps[2][j]-ps[3][j])>1e-8:
            raise ValueError("Momentum conservation failure")
    return ps

def mixing_block(text,name):
    lines=text.splitlines();active=False; entries={}
    for line in lines:
        line=line.split("#",1)[0].strip()
        if not line:continue
        match=re.match(r"(?i)BLOCK\s+(\S+)",line)
        if match:
            active=(match.group(1).upper()==name)
            continue
        if line.upper().startswith("DECAY"):
            active=False
        if not active:continue
        cols=line.split()
        if len(cols)>=3 and all(re.fullmatch(r"-?\d+",x) for x in cols[:2]):
            try:
                entries[(int(cols[0]),int(cols[1]))]=float(
                    cols[2].replace("D","E"))
            except ValueError:pass
    return {f"{i},{j}":v for (i,j),v in sorted(entries.items())
            if abs(v)>1.e-10}

def matrix_source_audit(matrix):
    content=matrix.read_text(errors="replace")
    lines=content.splitlines()
    keys=("NGRAPHS","NCOLOR","DENOM","AVG","IDEN","CF(",
          "CALL SXXXXX","CALL VXXXXX","CALL IXXXXX","CALL OXXXXX")
    excerpts=[]
    for n,line in enumerate(lines,1):
        if any(key in line.upper().replace(" ","") if key in
               ("NGRAPHS","NCOLOR","DENOM","IDEN","CF(")
               else key in line.upper() for key in keys):
            excerpts.append({"line":n,"text":line.strip()[:180]})
    # Do not equate NGRAPHS to distinct physical graphs if model contains
    # multiparticle definitions or 0 couplings; inspect HELAS calls directly.
    amps=[line.strip()[:160] for line in lines
          if re.search(r"\bCALL\s+\w+\s*\(",line,re.I)]
    return {
        "head_comments":[line.strip() for line in lines[:65]
                         if line.lstrip().startswith(("C","c","#"))][:24],
        "color_and_averaging_lines":excerpts[:65],
        "helas_calls":amps[:90],
        "number_of_helas_calls":len(amps),
    }

def coupling_source_audit(model):
    # Collect candidate electroweak relations for independent scheme check.
    candidates=[model/"Source/MODEL/couplings.f",
                model/"Source/MODEL/parameters.f",
                model/"Source/MODEL/param_read.inc"]
    rx=re.compile(
        r"\b(MDL_SW|MDL_CW|MDL_EE|MDL_GW|MDL_MW|MDL_MZ|AEWM1|"
        r"MDL_USQMIX|MDL_DSQMIX)\b",re.I)
    result=[]
    for path in candidates:
        if not path.is_file():continue
        for number,line in enumerate(path.read_text(errors="replace").splitlines(),1):
            if rx.search(line):
                result.append({"file":str(path),"line":number,
                               "text":line.strip()[:200]})
                if len(result)>=75:return result
    return result

def audit_one(base,channel,mass,tb,probe):
    model,work,review,b,nominal_ps=prepare(channel,mass,tb,base)
    source=work/"matrix.f"
    original_card=model/"Cards/param_card.dat"
    raw=original_card.read_text()
    default,_=parse_card(raw)
    fixed,_=parse_card(review.read_text())
    m2_json=base/"threshold_benchmarks"/f"M{mass:g}_tanbeta{tb:g}_{channel}"/"matrix2py_result.json"
    previous=json.loads(m2_json.read_text()) if m2_json.exists() else None
    result={"channel":channel,"model_dir":str(model),
            "matrix":str(source),"reference_fixed_color":reference(b),
            "previous_me_result":previous,
            "original_MASS":{str(pdg):default.get(("MASS",pdg)) for pdg
                    in (23,24,25,35,36,37,1000001,1000002)},
            "review_MASS":{str(pdg):fixed.get(("MASS",pdg)) for pdg
                    in (23,24,25,35,36,37,1000001,1000002)},
            "original_SMINPUTS":{str(i):default.get(("SMINPUTS",i))
                    for i in (1,2,3)},
            "review_SMINPUTS":{str(i):fixed.get(("SMINPUTS",i))
                    for i in (1,2,3)},
            "review_USQMIX_nonzero":mixing_block(review.read_text(),"USQMIX"),
            "review_DSQMIX_nonzero":mixing_block(review.read_text(),"DSQMIX"),
            "matrix_source":matrix_source_audit(source),
            "ew_coupling_source_hints":coupling_source_audit(model)}
    if probe:
        provenance=stage_ident_card(model,work)
        result["ident_card"]=provenance
        ps_cases={
          # At q=0 the initial scalars are both at rest: the ME2 must be
          # independent of the common final-state 3-axis orientation.
          "matched_q0_aligned":(review,b.mu,b.md,MW,b.mv,0.,0.),
          "matched_q0_rotated":(review,b.mu,b.md,MW,b.mv,0.,.35),
          "matched_q0p1":(review,b.mu,b.md,MW,b.mv,.1,.35),
          "matched_q1":(review,b.mu,b.md,MW,b.mv,1.,.35),
        }
        du=default.get(("MASS",1000002))
        dd=default.get(("MASS",1000001))
        dmw=default.get(("MASS",24))
        dmv=default.get(("MASS",23)) if channel=="Z" else 0.
        if all(x is not None and x>0 for x in (du,dd,dmw)) and (
                channel=="gamma" or (dmv is not None and dmv>0)):
            ps_cases["original_card_q0"]=(original_card,du,dd,dmw,dmv,0.,.35)
        results={}
        for label,(card,mu,md,mw,mv,q,theta) in ps_cases.items():
            pp=ps_at_relative_q(mu,md,mw,mv,q,theta)
            directory=base/"threshold_benchmarks"/f"M{mass:g}_tanbeta{tb:g}_{channel}"/"discrepancy_probe"/label
            directory.mkdir(parents=True,exist_ok=True)
            try:
                value=evaluate_in_worker(work,card,pp,.118,directory)
                results[label]={"status":"EVALUATED","value":value,
                                "momenta":pp,"card":str(card),"q":q,"angle_rad":theta}
            except Exception as exc:
                results[label]={"status":"ERROR","error":str(exc),
                                "momenta":pp,"card":str(card),"q":q}
        result["numeric_probes"]=results
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mass",type=float,default=500.)
    parser.add_argument("--tanbeta",type=float,default=3.)
    parser.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    parser.add_argument("--probe",action="store_true",
                        help="Evaluate matched q=0,0.1,1 and original-card q=0")
    args=parser.parse_args()
    base=args.root.resolve()
    output={"mass":args.mass,"tanbeta":args.tanbeta,"channels":{}}
    for channel in ("Z","gamma"):
        print("\nAUDITING",channel,flush=True)
        output["channels"][channel]=audit_one(
            base,channel,args.mass,args.tanbeta,args.probe)
    destination=base/"threshold_benchmarks"/f"M{args.mass:g}_tanbeta{args.tanbeta:g}_discrepancy_audit.json"
    destination.write_text(json.dumps(output,indent=2))
    for channel,data in output["channels"].items():
        print(f"\n=== {channel}: MODEL / GENERATED MATRIX ===")
        print("MASS original:",data["original_MASS"])
        print("MASS review:",data["review_MASS"])
        print("SMINPUTS original:",data["original_SMINPUTS"])
        print("SMINPUTS review:",data["review_SMINPUTS"])
        print("USQMIX:",data["review_USQMIX_nonzero"])
        print("DSQMIX:",data["review_DSQMIX_nonzero"])
        print("MATRIX COLOR/AVERAGING:")
        for line in data["matrix_source"]["color_and_averaging_lines"][:25]:
            print(f"  L{line['line']}: {line['text']}")
        print("HELAS calls:",data["matrix_source"]["number_of_helas_calls"])
        for line in data["matrix_source"]["helas_calls"][-25:]:
            print("  ",line)
        if args.probe:
            print("PROBES:")
            for name,info in data["numeric_probes"].items():
                print(" ",name,info.get("value",info.get("error")))
    print("\nSaved:",destination)
    print("DIAGNOSTIC ONLY — no couplings, colors, or analytic predictions were altered.")
if __name__=="__main__":
    main()
