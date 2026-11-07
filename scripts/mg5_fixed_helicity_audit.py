#!/usr/bin/env python3
"""Independent MG5 squared-helicity audit of scalar 0+ -> WZ/Wgamma.

Uses generated matrix.f DATA NHEL arrays and standalone matrix2py's documented
nhel index. No source edits, no model re-generation and no new physics input.
Per-helicity *squares* do NOT check complex relative phase: a1 remains UNKNOWN.

Run:
 .venv-mg5-f2py/bin/python scripts/mg5_fixed_helicity_audit.py

The worker must reproduce unpolarized get_value(nhel=-1) as sum of every
individual squared helicity nhel=1..N before any physics verdict.
"""
import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mg5_matrix2py_compare import prepare,stage_ident_card
from mg5_threshold_preflight import reference

def find_helicity_configs(matrix):
    """Read explicit 1-based matrix.f NHEL(I,j) DATA rows, not guessed order."""
    text=matrix.read_text(errors="replace")
    compact=re.sub(r"\n\s*[+&]\s*"," ",text)
    regex=re.compile(
        r"DATA\s*\(\s*NHEL\s*\(\s*I\s*,\s*(\d+)\s*\)\s*,\s*"
        r"I\s*=\s*1\s*,\s*(?:NEXTERNAL|4)\s*\)\s*/([^/]*)/",
        flags=re.I|re.S)
    found={}
    for match in regex.finditer(compact):
        index=int(match.group(1))
        vals=[int(x.strip()) for x in match.group(2).split(",") if x.strip()]
        if len(vals)!=4 or any(x not in (-1,0,1) for x in vals):
            raise RuntimeError(f"Invalid NHEL row j={index}: {vals}")
        if index in found:raise RuntimeError(f"Repeated NHEL index {index}")
        found[index]=vals
    if not found:
        raise RuntimeError("No NHEL DATA rows found; inspect matrix.f before audit")
    expected=set(range(1,max(found)+1))
    if set(found)!=expected:raise RuntimeError(f"Non-contiguous helicities: {sorted(found)}")
    return [{"nhel":j,"helicities":found[j]} for j in sorted(found)]

def classify(rows,channel):
    """Extract physical spin-0 longitudinal/transverse equal-helicity groups."""
    groups={"00":0.,"transverse":0.,"other":0.}
    details=[]
    for row in rows:
        h=row["helicities"]
        if h[:2]!=[0,0]:
            raise RuntimeError(f"Generated incoming scalars have nonzero helicity: {h}")
        _,_,hw,hv=h
        if channel=="Z" and hw==0 and hv==0:
            kind="00"
        elif hw==hv and hw in (-1,1):
            kind="transverse"
        else:
            kind="other"
        groups[kind]+=row["me2"]
        details.append({"kind":kind,**row})
    return groups,details

def run_one(channel,mass,tanbeta,base,tolerance):
    directory,work,review,b,ps=prepare(channel,mass,tanbeta,base)
    stage_ident_card(directory,work)
    configs=find_helicity_configs(work/"matrix.f")
    save=base/"threshold_benchmarks"/(
        f"M{mass:g}_tanbeta{tanbeta:g}_{channel}")/"fixed_helicity"
    save.mkdir(parents=True,exist_ok=True)
    input_file=save/"helicity_input.json"
    output_file=save/"helicity_worker.json"
    input_file.write_text(json.dumps({
        "momenta":ps,"helicity_configurations":configs},indent=2))
    if output_file.exists():output_file.unlink()
    command=[sys.executable,str(ROOT/"scripts/mg5_helicity_worker.py"),
             "--card",str(review.resolve()),
             "--input",str(input_file.resolve()),
             "--output",str(output_file.resolve())]
    try:
        proc=subprocess.run(command,cwd=work,timeout=90,capture_output=True,
                            text=True)
    except subprocess.TimeoutExpired as err:
        raise RuntimeError(f"Helicity worker timed out: {err}") from err
    (save/"worker.log").write_text(
        "$ "+" ".join(command)+"\n"+proc.stdout+"\n"+proc.stderr)
    if proc.returncode or not output_file.is_file():
        raise RuntimeError("MG5 fixed-helicity worker returned no valid output. "
                           "See "+str(save/"worker.log"))
    result=json.loads(output_file.read_text())
    if result.get("status")!="EVALUATED":
        raise RuntimeError("Worker missing evaluated marker")
    rows=result["components"]
    if len(rows)!=len(configs):raise RuntimeError("Incomplete helicity results")
    total=result["summed_me2"]
    sum_parts=result["sum_components"]
    if total<=0 or not math.isclose(sum_parts,total,rel_tol=tolerance,abs_tol=1e-12):
        raise RuntimeError("nhel indices do not sum to nhel=-1: "+
                           f"{sum_parts} versus {total}. No helicity PASS.")
    groups,details=classify(rows,channel)
    analytic=reference(b)
    target_trans=analytic["transverse_sum"]/3.
    target_long=analytic["longitudinal_sum"]/3.
    comparisons={
        "transverse":{"mg5":groups["transverse"],"target":target_trans},
        "longitudinal":{"mg5":groups["00"],"target":target_long},
        "unphysical_others":{"mg5":groups["other"],"target":0.},
    }
    for name,row in comparisons.items():
        divisor=max(abs(row["target"]),abs(total)*1e-12,1e-14)
        row["relative_or_scaled_residual"]=(row["mg5"]-row["target"])/divisor
        row["pass"]=math.isclose(row["mg5"],row["target"],
                                 rel_tol=tolerance,
                                 abs_tol=max(1e-12,tolerance*total*1e-8))
    passed=all(x["pass"] for x in comparisons.values())
    report={"channel":channel,"mass":mass,"tanbeta":tanbeta,
            "status":"PASS_FIXED_HELICITY_SQUARES_ONLY" if passed else "FAIL",
            "nhel_sum_consistency":(sum_parts-total)/total,
            "fractions":{"mg5_f00":groups["00"]/total,
                         "analytic_f00":target_long/(target_long+target_trans)
                            if channel=="Z" else 0.},
            "components":details,
            "comparisons":comparisons,
            "complex_interference_phase_status":"UNKNOWN_NOT_PROBED"}
    (save/"summary.json").write_text(json.dumps(report,indent=2))
    print(channel,report["status"],"f00_MG5=",report["fractions"]["mg5_f00"],
          "f00_analytic=",report["fractions"]["analytic_f00"])
    for name,record in comparisons.items():
        print(" ",name,record)
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mass",type=float,default=500.)
    ap.add_argument("--tanbeta",type=float,default=3.)
    ap.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    ap.add_argument("--tolerance",type=float,default=1e-8)
    args=ap.parse_args()
    if args.tolerance<=0:ap.error("nonpositive tolerance")
    base=args.root.expanduser().resolve()
    statuses=[]
    for channel in ("Z","gamma"):
        try:
            status=run_one(channel,args.mass,args.tanbeta,base,args.tolerance)
            statuses.append(status["status"]=="PASS_FIXED_HELICITY_SQUARES_ONLY")
        except Exception as err:
            statuses.append(False)
            print("FAIL",channel,type(err).__name__,err,file=sys.stderr)
    if not all(statuses):raise SystemExit(2)
    print("PASS: MG5 squared-helicity contributions match; relative complex "
          "phases and a1 are NOT externally validated.")

if __name__=="__main__":
    main()
