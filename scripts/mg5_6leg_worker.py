#!/usr/bin/env python3
"""Isolated MG5_aMC matrix2py evaluation of many 6-leg phase-space points.

Runs inside the generated standalone SubProcesses/P* directory. A Fortran STOP
can return status zero, so an output JSON with a counted set is mandatory.
Never imports or modifies the analytic amplitude implementation.
"""
import argparse
import importlib
import json
import math
from pathlib import Path
import sys

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--card",required=True,type=Path)
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--alpha-s",type=float,default=.118)
    args=p.parse_args()
    import numpy as np
    work=Path.cwd()
    if not list(work.glob("matrix2py*.so")):
        raise RuntimeError("No generated 6-leg matrix2py extension in "+str(work))
    data=json.loads(args.input.read_text())
    cases=data["cases"]
    if not cases:
        raise RuntimeError("No phase-space points to evaluate")
    sys.path.insert(0,str(work))
    module=importlib.import_module("matrix2py")
    print("6-leg worker: initializing",args.card,flush=True)
    module.initialisemodel(str(args.card.resolve()))
    print("6-leg worker: model ready, points =",len(cases),flush=True)
    results=[]
    for i,case in enumerate(cases):
        legs=np.array(case["momenta"],dtype=np.float64)
        if legs.shape!=(6,4):
            raise RuntimeError(f"Case {i}: expected six [E,px,py,pz] rows")
        p4=np.asfortranarray(legs.T)
        value=float(module.get_value(p4,args.alpha_s,-1))
        if not math.isfinite(value) or value<0:
            raise RuntimeError(f"Case {i}: nonfinite/negative ME2={value}")
        results.append({"id":case["id"],"ME2":value})
    out={"status":"EVALUATED","n_requested":len(cases),
         "n_returned":len(results),"values":results,
         "card":str(args.card),"numpy":np.__version__}
    args.output.write_text(json.dumps(out,indent=2))
    print("6-leg worker: wrote",len(results),"evaluations",flush=True)

if __name__=="__main__":
    main()
