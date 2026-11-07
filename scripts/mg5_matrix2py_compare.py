#!/usr/bin/env python3
"""Direct MG5_aMC v3.5 standalone scalar ME test via matrix2py.

Avoids check_sa.f/READPS entirely. This does not overwrite default cards.
Run once for Z and once for gamma from the repository root.
Requires: generated standalone outputs, a preview card from
  mg5_threshold_preflight.py --write-cards, numpy, f2py, gfortran.

Evidence class: external-generator calculation if output and model/color
conventions are independently checked. A plausible ratio alone is not a PASS.
"""
import argparse
import importlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import Setup,splitting,MW,MZ,S2,ALPHA_W,helicities
from mg5_threshold_preflight import momenta,validate_ps,parse_card,reference

LABELS={"Z":"MG5_UL_DL_WZ","gamma":"MG5_UL_DL_WA"}
BAD_INPUT=re.compile(r"\bGF\b|\bMDL_GF\b",re.I)

def external_input_audit(model_dir):
    """Report observed generated parameter readers, not assumed UFO internals."""
    f=model_dir/"Source/MODEL/param_read.inc"
    if not f.is_file():
        return {"file":str(f),"found":False,"gf_status":"UNKNOWN_NO_READER"}
    lines=f.read_text(errors="replace").splitlines()
    keylines=[{"line":i+1,"source":line.strip()[:250]}
              for i,line in enumerate(lines)
              if "LHA_GET_REAL" in line.upper() and
                 any(key in line.upper() for key in ("AEWM1","MDL_MW","MDL_MZ","GF"))]
    matches=[x for x in keylines if BAD_INPUT.search(x["source"])]
    return {"file":str(f),"found":True,"external_read_lines":keylines[:40],
            "gf_status":("READER_MENTIONS_GF" if matches
                         else "NO_GF_IN_READER_NOT_PROOF_OF_ALL_DEPENDENCIES")}

def prepare(channel,mass,tb,base):
    name=LABELS[channel]
    directory=base/name
    sub=sorted((directory/"SubProcesses").glob("P*/matrix.f"))
    if len(sub)!=1:
        raise RuntimeError(f"Expected exactly 1 matrix.f for {name}; found {len(sub)}")
    work=sub[0].parent
    default=directory/"Cards/param_card.dat"
    review=directory/"Cards/param_card_quirkonium_review.dat"
    if not default.is_file() or not review.is_file():
        raise RuntimeError("Missing standalone original/review cards. Run "
          f"python scripts/mg5_threshold_preflight.py --mass {mass:g} "
          f"--tanbeta {tb:g} --write-cards")
    prior,_=parse_card(default.read_text())
    matched,_=parse_card(review.read_text())
    b=Setup(mass,splitting(mass,tb),channel)
    expected={("MASS",1000002):b.mu,("MASS",1000001):b.md,
              ("MASS",23):MZ,("MASS",24):MW,
              ("SMINPUTS",1):1/(ALPHA_W*S2)}
    for key,val in expected.items():
        have=matched.get(key)
        if have is None or not math.isclose(have,val,rel_tol=1e-10,abs_tol=1e-9):
            raise RuntimeError(f"Review card mismatches {key}: expected {val}, got {have}")
    if ("SMINPUTS",2) in matched and ("SMINPUTS",2) not in prior:
        raise RuntimeError("Review card injected unregistered GF into MSSM model")
    ps=momenta(b)
    validate_ps(ps,[b.mu,b.md,MW,b.mv])
    return directory,work,review,b,ps

def compile_extension(work,logdir):
    candidates=list(work.glob("matrix2py*.so"))
    if candidates:return candidates
    command=["make","matrix2py.so"]
    print("Building standalone Python ME extension:",work,flush=True)
    try:
        proc=subprocess.run(command,cwd=work,capture_output=True,text=True,timeout=240)
    except (OSError,subprocess.TimeoutExpired) as ex:
        raise RuntimeError(f"Cannot compile matrix2py: {ex}") from ex
    (logdir/"matrix2py_build.log").write_text(
        "$ "+" ".join(command)+"\n"+proc.stdout+"\n"+proc.stderr)
    if proc.returncode:
        raise RuntimeError("MadGraph standalone make matrix2py.so failed. "
                           f"Inspect {logdir/'matrix2py_build.log'}; "
                           "requires a compatible Python, NumPy/f2py and gfortran.")
    candidates=list(work.glob("matrix2py*.so"))
    if not candidates:
        raise RuntimeError("make returned 0 but no matrix2py shared library appeared")
    return candidates

def run():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--channel",required=True,choices=list(LABELS))
    p.add_argument("--mass",type=float,default=500.)
    p.add_argument("--tanbeta",type=float,default=3.)
    p.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    p.add_argument("--alpha-s",type=float,default=.118)
    p.add_argument("--no-build",action="store_true")
    p.add_argument("--tolerance",type=float,default=.01,
                  help="Only for a diagnostic ratio comparison; not a model-validity threshold")
    args=p.parse_args()
    if args.mass<=MW+MZ or args.tanbeta<=0:p.error("invalid mass/tanbeta")
    base=args.root.expanduser().resolve()
    directory,work,review,b,ps=prepare(args.channel,args.mass,args.tanbeta,base)
    logdir=base/"threshold_benchmarks"/f"M{args.mass:g}_tanbeta{args.tanbeta:g}_{args.channel}"
    logdir.mkdir(parents=True,exist_ok=True)
    ew=external_input_audit(directory)
    (logdir/"external_parameter_reader.json").write_text(json.dumps(ew,indent=2))
    print("EW reader audit:",ew["gf_status"])
    for line in ew.get("external_read_lines",[]):print(" ",line)
    if args.no_build:
        if not list(work.glob("matrix2py*.so")):
            raise RuntimeError("--no-build but no existing matrix2py shared library")
    else:
        compile_extension(work,logdir)
    import numpy as np
    if "matrix2py" in sys.modules:
        raise RuntimeError("One process per Python interpreter; use separate CLI calls")
    sys.path.insert(0,str(work))
    matrix2py=importlib.import_module("matrix2py")
    init=getattr(matrix2py,"initialisemodel",None)
    get=getattr(matrix2py,"get_value",None)
    if not callable(init) or not callable(get):
        raise RuntimeError("Generated extension does not expose initialisemodel/get_value. "
                           f"Found {sorted(k for k in dir(matrix2py) if not k.startswith('_'))[:40]}")
    print("Loading review card (original remains unmodified):",review)
    init(str(review))
    # MadGraph uses P(0:3, NEXTERNAL), Fortran column-major.
    four=np.asfortranarray(np.array(ps,dtype=np.float64).T)
    value=float(get(four,args.alpha_s,-1))
    analytic=reference(b)
    fixed=analytic["analytic_fixed_color_helicity_sum"]
    target=analytic["candidate_MG5_color_averaged_if_denominator_3"]
    if not math.isfinite(value) or value<0:
        raise RuntimeError(f"Nonphysical MG5 ME numerical result: {value}")
    ratio=value/target if target>0 else float('nan')
    print(f"{args.channel} MG5 color-averaged ME2 = {value:.16g}")
    print(f"Analytic fixed-color helicity ME2 = {fixed:.16g}")
    print(f"Analytic /3 candidate MG5 ME2 = {target:.16g}")
    print(f"Ratio MG5 / analytic_color_average_candidate = {ratio:.12g}")
    print("Numerical ratio is diagnostic. Audit external mixing, diagrams, "
          "color denominator and angular conventions before assigning PASS.")
    output={"channel":args.channel,"mass":args.mass,"tanbeta":args.tanbeta,
            "ew_source_audit":ew,"mass_card_review":str(review),
            "matrix":str(work/"matrix.f"),"momenta":ps,"alpha_s":args.alpha_s,
            "mg5_color_averaged_me2":value,**analytic,
            "ratio_to_expected_color_average":ratio,
            "candidate_ratio_tolerance":args.tolerance,
            "candidate_ratio_near_one":abs(ratio-1.)<=args.tolerance,
            "status":"RAW_MG5_RESULT_NEEDS_INDEPENDENT_MODEL_AND_COLOR_AUDIT"}
    saved=logdir/"matrix2py_result.json"
    saved.write_text(json.dumps(output,indent=2))
    print("Wrote:",saved)
    # A nontrivial discrepancy should stop a pipeline, but retain evidence.
    if abs(ratio-1)>args.tolerance:
        print("DISCREPANCY: investigate model couplings/color; "
              "no automatic normalization correction permitted.",file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(run())
