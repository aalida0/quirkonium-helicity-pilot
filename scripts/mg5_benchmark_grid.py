#!/usr/bin/env python3
"""Reproducible independent MadGraph5 threshold matrix-element benchmark grid.

This validates *helicity-summed* MG5 matrix elements against analytical
fixed-color scalar doublet results with explicit 1/3 QCD color averaging,
for a compact SLHA card and physical on-shell momenta at each benchmark.
No regeneration, detector model, physical squark-potential viability or
helicity-by-helicity claim is made.

All generated cards are NEW files inside ignored validation/local_logs.
Original MSSM cards, UFO, matrix.f and any previous M=500 preview stay intact.
Use the venv that compiled matrix2py and NumPy 1.26.4.

Example:
 .venv-mg5-f2py/bin/python scripts/mg5_benchmark_grid.py
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import Setup,splitting,MW,MZ,S2,ALPHA_W
from mg5_threshold_preflight import parse_card,replace_card,reference,momenta,validate_ps
from mg5_matrix2py_compare import (LABELS,stage_ident_card,evaluate_in_worker)

# Covers both mass-splitting signs, the degenerate zero, positive/negative
# longitudinal effects, and moderate-to-high masses. No new MG generation.
POINTS=((300.,1.),(400.,.3),(500.,3.),(800.,10.),
        (1200.,1.),(2000.,3.))
NUMERIC_TOL=1.e-8

def generated_averaging_factor(matrix):
    """Require the familiar one-color-flow scalar 3/9; fail on source drift."""
    s=matrix.read_text(errors="replace").upper()
    iden=re.search(r"DATA\s+IDEN\s*/\s*(\d+)\s*/",s)
    cf=re.search(r"DATA\s*\(\s*CF\s*\(I,\s*1\)",s)
    three=re.search(r"/\s*3\.0+[0]*D\+00\s*/",s)
    ncolor=re.search(r"NCOLOR\s*=\s*(\d+)",s)
    if not iden or not cf or not three or not ncolor:
        raise RuntimeError("Unable to verify MG5 generated color average; inspect "+str(matrix))
    if int(iden.group(1))!=9 or int(ncolor.group(1))!=1:
        raise RuntimeError("MG5 color factor/denominator changed. Stop and audit.")
    return 3./9.

def compact_card_for_point(original,b,tanbeta):
    """Produce one safe SLHA copy, not a new MSSM spectrum solution."""
    present,widths=parse_card(original)
    updates={("MASS",1000002):b.mu,("MASS",1000001):b.md,
             ("MASS",23):MZ,("MASS",24):MW,
             ("SMINPUTS",1):1./(ALPHA_W*S2)}
    for pdg in (23,24,1000001,1000002):
        if pdg in widths:updates[("DECAY",pdg)]=0.
    for candidate in (("MINPAR",3),("HMIX",2)):
        if candidate in present:updates[candidate]=tanbeta
    missing=[key for key in updates
             if key[0]!="DECAY" and key not in present]
    if missing:raise ValueError(f"Generated card lacks keys {missing}")
    changed,found=replace_card(original,updates)
    if found!=set(updates):
        raise RuntimeError(f"Card replacement incomplete: {set(updates)-found}")
    parsed,newwidths=parse_card(changed)
    for key,value in updates.items():
        read=(newwidths.get(key[1]) if key[0]=="DECAY" else parsed.get(key))
        if read is None or not math.isclose(read,value,rel_tol=2.e-12,abs_tol=1.e-11):
            raise RuntimeError(f"SLHA numeric round trip mismatch {key}: {read} != {value}")
    # Exclude unsafe wide tokens in *all updated* lines; untouched model card
    # may have its own original formats, which are known to parse successfully.
    from mg5_threshold_preflight import format_slha_number
    for val in updates.values():
        if len(format_slha_number(val))>20:raise RuntimeError("Wide SLHA update")
    return changed,updates

def reference_channels(base):
    files={}
    for channel,label in LABELS.items():
        directory=(base/label).resolve()
        paths=list((directory/"SubProcesses").glob("P*/matrix.f"))
        if len(paths)!=1:
            raise RuntimeError(f"Expected 1 generated matrix.f for {channel}; got {len(paths)}")
        original=directory/"Cards/param_card.dat"
        if not original.is_file():raise RuntimeError(f"Original MSSM card missing: {original}")
        work=paths[0].parent
        factor=generated_averaging_factor(paths[0])
        provenance=stage_ident_card(directory,work)
        files[channel]={"work":work,"original":original,
                        "averaging":factor,"ident_card":provenance}
    return files

def bench_label(m,tb):
    return f"M{m:g}_tanbeta{tb:g}"

def evaluate_point(channel,base,compiled,m,tb,tolerance=NUMERIC_TOL):
    b=Setup(m,splitting(m,tb),channel)
    ps=momenta(b)
    validate_ps(ps,[b.mu,b.md,MW,b.mv])
    record=compiled[channel]
    original=record["original"].read_text()
    slha,updates=compact_card_for_point(original,b,tb)
    folder=base/"threshold_benchmarks"/"independent_grid"/bench_label(m,tb)/channel
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/"param_card_compact.dat"
    target.write_text(slha)
    actual=evaluate_in_worker(record["work"],target,ps,.118,folder)
    analytic=reference(b)
    fixed=analytic["analytic_fixed_color_helicity_sum"]
    expected=fixed*record["averaging"]
    rel=(actual-expected)/expected
    data={"channel":channel,"M":m,"tanbeta":tb,
          "delta":b.delta,"mu":b.mu,"md":b.md,
          "momentum":ps,"card":str(target),
          "card_sha256":hashlib.sha256(slha.encode()).hexdigest(),
          "color_averaging":record["averaging"],"mg5_me2":actual,
          "analytic_fixed_color_me2":fixed,
          "analytic_avg_me2":expected,"signed_rel":rel,
          "abs_rel":abs(rel),
          "numeric_tolerance":tolerance,
          "numeric_status":("PASS" if math.isfinite(rel) and
                           abs(rel)<=tolerance else "FAIL")}
    (folder/"comparison.json").write_text(json.dumps(data,indent=2))
    return data

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    parser.add_argument("--tolerance",type=float,default=NUMERIC_TOL)
    parser.add_argument("--channel",choices=("both","Z","gamma"),default="both")
    parser.add_argument("--stop-on-fail",action="store_true")
    args=parser.parse_args()
    if args.tolerance<=0:parser.error("tolerance must be positive")
    base=args.root.expanduser().resolve()
    generated=reference_channels(base)
    channels=("Z","gamma") if args.channel=="both" else (args.channel,)
    result={"utc":datetime.now(timezone.utc).isoformat(),
            "scope":"tree_level_helicity_summed_MSSM_EW_proxy_not_bound_state_formation",
            "tolerance":args.tolerance,
            "points":[], "status":"UNKNOWN_INCOMPLETE"}
    for m,tb in POINTS:
        row={"M":m,"tanbeta":tb,"channels":{}}
        for channel in channels:
            try:
                record=evaluate_point(channel,base,generated,m,tb,args.tolerance)
            except Exception as exc:
                record={"channel":channel,"numeric_status":"ERROR","error":str(exc)}
            row["channels"][channel]=record
            if record["numeric_status"]=="PASS":
                print(f"PASS {channel:>5} {bench_label(m,tb):>18} "
                      f"rel={record['signed_rel']:+.3e}",flush=True)
            else:
                print(f"FAIL {channel:>5} {bench_label(m,tb):>18} "
                      f"{record.get('error',record.get('signed_rel'))}",flush=True)
        result["points"].append(row)
        if args.stop_on_fail and any(c["numeric_status"]!="PASS"
                                     for c in row["channels"].values()):
            break
    items=[r for row in result["points"] for r in row["channels"].values()]
    result["tested"]=len(items)
    result["passed"]=sum(r["numeric_status"]=="PASS" for r in items)
    result["worst_rel"]=max((r["abs_rel"] for r in items
                             if "abs_rel" in r),default=None)
    result["status"]=("PASS_SCOPED" if len(items)==len(POINTS)*len(channels)
                      and result["passed"]==len(items) else "FAIL_OR_INCOMPLETE")
    location=base/"threshold_benchmarks"/"independent_grid"/"summary.json"
    location.parent.mkdir(exist_ok=True,parents=True)
    location.write_text(json.dumps(result,indent=2))
    print(f"\nRESULT {result['status']}: {result['passed']}/{result['tested']} "
          f"worst_rel={result['worst_rel']} saved={location}")
    if result["status"]!="PASS_SCOPED":raise SystemExit(2)

if __name__=="__main__":
    main()
