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
import os
import re
import subprocess
import sys
import shutil
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
    review=directory/"Cards/param_card_quirkonium_review_compact.dat"
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
    # A legacy fixed-width SLHA reader may silently truncate 21-character
    # scientific notation fields. Reject unsafe preview fields up front.
    import re as _re
    for line in review.read_text().splitlines():
        data=line.split("#",1)[0].strip()
        fields=data.split()
        if len(fields)>=2 and _re.fullmatch(
            r"[-+]?\d+\.\d+[EeDd][-+]?\d+",fields[1]
        ) and len(fields[1])>20:
            raise RuntimeError(f"Unsafe wide numeric field in compact review: {fields[1]}")
    if ("SMINPUTS",2) in matched and ("SMINPUTS",2) not in prior:
        raise RuntimeError("Review card injected unregistered GF into MSSM model")
    ps=momenta(b)
    validate_ps(ps,[b.mu,b.md,MW,b.mv])
    return directory,work,review,b,ps

def build_error_summary(log_text,tail_lines=70):
    """Return concise actionable build evidence; never infer a single root cause."""
    lines=log_text.splitlines()
    patterns=(
        r"\berror\b",r"\bfatal\b",r"\bnot found\b",
        r"no rule to make target",r"\btraceback\b",
        r"ModuleNotFoundError",r"undefined reference",
        r"cannot find",r"no such file",r"command not found",
        r"subprocess-exited-with-error",
    )
    rx=re.compile("|".join(patterns),re.I)
    hits=[line for line in lines if rx.search(line)]
    return {"error_lines":hits[-15:], "tail":lines[-tail_lines:],
            "line_count":len(lines)}

def compiler_environment():
    """Non-invasive snapshot to help distinguish missing tools from tool mismatches."""
    info={"python":sys.executable,"python_version":sys.version.split()[0]}
    for command in ("make","gfortran","gcc","f2py"):
        info[command]=shutil.which(command)
    try:
        import numpy
        info["numpy"]=numpy.__version__
        info["numpy_path"]=numpy.__file__
    except Exception as exc:
        info["numpy_error"]=f"{type(exc).__name__}: {exc}"
    return info

def compile_extension(work,logdir):
    candidates=list(work.glob("matrix2py*.so"))
    if candidates:return candidates
    command=["make","matrix2py.so"]
    environment=compiler_environment()
    # Standalone makefiles may produce f2py3.10 from a make variable, without
    # spelling the launcher literally in their source. Use the venv-local shim.
    # Preserve sys.executable: resolving the venv symlink loses the venv ABI.
    venv_bin=str(Path(os.path.abspath(sys.executable)).parent)
    build_env=os.environ.copy()
    build_env["PATH"]=venv_bin+os.pathsep+build_env.get("PATH","")
    f2py_cmd=shutil.which("f2py3.10",path=build_env["PATH"])
    environment["build_path_prefix"]=venv_bin
    environment["f2py3_10_resolved_for_make"]=f2py_cmd
    if f2py_cmd and Path(f2py_cmd).parent!=Path(venv_bin):
        raise RuntimeError("Make would invoke the stale system f2py3.10: "+
            str(f2py_cmd)+". Run .venv-mg5-f2py/bin/python "+
            "scripts/fix_mg5_f2py_makefile.py --apply first.")
    print("Building standalone Python ME extension:",work,flush=True)
    print("Build environment:",json.dumps(environment,sort_keys=True),flush=True)
    (logdir/"matrix2py_environment.json").write_text(
        json.dumps(environment,indent=2))
    try:
        proc=subprocess.run(command,cwd=work,capture_output=True,text=True,
                            env=build_env,timeout=240)
    except (OSError,subprocess.TimeoutExpired) as ex:
        raise RuntimeError(f"Cannot compile matrix2py: {ex}") from ex
    output="$ "+" ".join(command)+"\n"+proc.stdout+"\n"+proc.stderr
    logfile=logdir/"matrix2py_build.log"
    logfile.write_text(output)
    if proc.returncode:
        summary=build_error_summary(output)
        print("\n====== MadGraph matrix2py build diagnostics ======",file=sys.stderr)
        print("Make exit code:",proc.returncode,file=sys.stderr)
        print("Build log:",logfile,file=sys.stderr)
        print("Relevant error lines:",file=sys.stderr)
        for line in summary["error_lines"]:
            print(line[:500],file=sys.stderr)
        print("Last build-log lines:",file=sys.stderr)
        for line in summary["tail"]:
            print(line[:500],file=sys.stderr)
        print("======= End of matrix2py build diagnostics =======\n",file=sys.stderr)
        raise RuntimeError("MadGraph matrix2py compilation FAILED. "
                           f"Attach the exact build log at {logfile}. "
                           "Do not modify model inputs or downgrade packages "
                           "until the compiler's actual error is identified.")
    candidates=list(work.glob("matrix2py*.so"))
    if not candidates:
        raise RuntimeError("make returned 0 but no matrix2py shared library appeared")
    return candidates

def stage_ident_card(model_dir,work):
    """Ensure model's EXISTING ident_card.dat is visible to the Fortran reader.

    The generated LHA reader searches the working directory and its parents.
    When the canonical file is stored under Source/MODEL, link to it in the
    generated P* working directory. Never invent identity mappings or overwrite
    a user-provided identity file.
    """
    model_dir=model_dir.resolve()
    work=work.resolve()
    ancestors=[work,*work.parents]
    for ancestor in ancestors:
        existing=ancestor/"ident_card.dat"
        if existing.is_file():
            return {"found":True,"path":str(existing),
                    "staged":False,"method":"already_in_parent_search_path"}
        if ancestor==model_dir:
            break
    candidates=[
        model_dir/"Source/MODEL/ident_card.dat",
        model_dir/"Cards/ident_card.dat",
        model_dir/"Source/ident_card.dat",
        model_dir/"ident_card.dat",
    ]
    candidates=[p for p in candidates if p.is_file()]
    if not candidates:
        # Some generators put it in a less common directory. Inspect only the
        # generated standalone, never search across unrelated installations.
        candidates=sorted(model_dir.rglob("ident_card.dat"))
        candidates=[p for p in candidates if p.is_file()]
    if not candidates:
        raise RuntimeError(
            f"Existing ident_card.dat not found anywhere under {model_dir}. "
            "Fortran initialisemodel stops before get_value; do not create an "
            "empty or hand-written ident_card.dat. Inspect Source/MODEL and "
            "the generated lha_read.f. Command: find "+
            str(model_dir)+" -name ident_card.dat -ls")
    if len(candidates)>1:
        import hashlib
        hashes={hashlib.sha256(p.read_bytes()).hexdigest() for p in candidates}
        if len(hashes)!=1:
            raise RuntimeError(
                "Multiple different ident_card.dat files inside standalone: "+
                ", ".join(str(p) for p in candidates)+
                ". Do not choose arbitrarily.")
    selected=candidates[0].resolve()
    staged=work/"ident_card.dat"
    if staged.exists() or staged.is_symlink():
        if staged.is_file() and staged.resolve()==selected:
            return {"found":True,"path":str(staged),"source":str(selected),
                    "staged":True,"method":"existing_identical_symlink_or_file"}
        raise RuntimeError(f"Refusing to replace existing ident card: {staged}")
    staged.symlink_to(selected)
    return {"found":True,"path":str(staged),"source":str(selected),
            "staged":True,"method":"symlink_original_generated_metadata"}

def evaluate_in_worker(work,review,ps,alpha_s,logdir):
    """Run Fortran in generated P* directory; detect silent STOP (even exit 0)."""
    inputs=logdir/"matrix2py_momenta.json"
    outputs=logdir/"matrix2py_worker_result.json"
    transcript=logdir/"matrix2py_initialization.log"
    inputs.write_text(json.dumps(ps,indent=2))
    if outputs.exists():outputs.unlink()  # Never reuse a stale success.
    command=[sys.executable,str(ROOT/"scripts/mg5_matrix2py_worker.py"),
             "--model-card",str(review.resolve()),
             "--momenta",str(inputs.resolve()),"--output",str(outputs.resolve()),
             "--alpha-s",str(alpha_s)]
    try:
        result=subprocess.run(command,cwd=work,capture_output=True,
                              text=True,timeout=60)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"MG5 Fortran worker timed out: {exc}") from exc
    transcript.write_text("$ "+" ".join(command)+"\n"+
                          result.stdout+"\n"+result.stderr)
    if result.returncode or not outputs.is_file():
        raise RuntimeError(
            "MadGraph initialisemodel/get_value did not return a numerical "
            "result (Fortran STOP may exit with code 0). "
            f"Worker exit={result.returncode}; see {transcript}. "
            "Likely missing ident_card.dat/working-directory/model input; "
            "do not report a physics PASS.")
    data=json.loads(outputs.read_text())
    if data.get("worker_status")!="ME_EVALUATED":
        raise RuntimeError(f"Worker result did not certify get_value: {data}")
    print(result.stdout,end="")
    return float(data["mg5_me2"])

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
    provenance=stage_ident_card(directory,work)
    print("Generated ident_card.dat lookup:",json.dumps(provenance,sort_keys=True))
    value=evaluate_in_worker(work,review,ps,args.alpha_s,logdir)
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
            "ew_source_audit":ew,"ident_card_provenance":provenance,
            "mass_card_review":str(review),
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
