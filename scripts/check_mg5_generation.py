#!/usr/bin/env python3
"""Postflight check: MadGraph can return to shell despite card errors.

This checks process-output existence and diagnostic text only. It is NOT
an independent validation of the numerical matrix element.
"""
import argparse
from pathlib import Path
import re

ERROR_PATTERNS=(
    re.compile(r"^\s*ERROR\s*:",re.I|re.M),
    re.compile(r"Error detected in sub-command",re.I),
    re.compile(r"command not executed",re.I),
    re.compile(r"not a valid pathname",re.I),
)
NAMES=("MG5_UL_DL_WZ","MG5_UL_DL_WA")

def assess(base, log_text):
    errors=[]
    for pattern in ERROR_PATTERNS:
        if pattern.search(log_text):
            errors.append(f"MadGraph log contains: {pattern.pattern}")
    results={}
    for name in NAMES:
        out=base/name
        mats=sorted((out/"SubProcesses").glob("P*/matrix*.f")) if out.exists() else []
        results[name]=[str(p) for p in mats]
        if not mats:
            errors.append(f"No generated Fortran matrix file: {out}/SubProcesses/P*/matrix*.f")
    return results,errors

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("log",type=Path,
                   help="Log from mg5_aMC reading madgraph/mssm_ew_procs.mg5")
    args=p.parse_args()
    if not args.log.is_file():
        p.error(f"Log not found: {args.log}")
    results,errors=assess(args.log.parent,args.log.read_text(errors="replace"))
    for name,files in results.items():
        print(f"{name}: generated matrix files={len(files)}")
        for item in files[:4]:print("  "+item)
    if errors:
        for err in errors: print("FAIL:",err)
        raise SystemExit(1)
    print("PASS: MG5 process generation produced both standalone matrix directories")
    print("NOTE: matrix-element numerical comparison remains unperformed.")
