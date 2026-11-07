#!/usr/bin/env python3
"""Standalone MG5 matrix2py individual-helicity worker; no file edits.

A separate process is required because legacy Fortran STOP can exit with 0.
Only writes a JSON result after all get_value(p,alpha_s,nhel) return.
"""
import argparse
import importlib
import json
from pathlib import Path
import sys

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--card",required=True,type=Path)
    ap.add_argument("--input",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--alpha-s",type=float,default=.118)
    args=ap.parse_args()
    work=Path.cwd()
    if not list(work.glob("matrix2py*.so")):
        raise RuntimeError("matrix2py extension missing in generated P* cwd")
    import numpy as np
    payload=json.loads(args.input.read_text())
    ps=payload["momenta"]
    labels=payload["helicity_configurations"]
    momenta=np.asfortranarray(np.array(ps,dtype=np.float64).T)
    if momenta.shape!=(4,4):
        raise RuntimeError(f"Unexpected P array: {momenta.shape}")
    sys.path.insert(0,str(work))
    module=importlib.import_module("matrix2py")
    print("Helicity worker: starting model init from",args.card,flush=True)
    module.initialisemodel(str(args.card.resolve()))
    print("Helicity worker: initialized; get_value nhel=-1 and 1..N",flush=True)
    total=float(module.get_value(momenta,args.alpha_s,-1))
    entries=[]
    for row in labels:
        idx=int(row["nhel"])
        value=float(module.get_value(momenta,args.alpha_s,idx))
        entries.append({"nhel":idx,"helicities":row["helicities"],
                        "me2":value})
    result={"status":"EVALUATED","summed_me2":total,
            "components":entries,"sum_components":sum(x["me2"] for x in entries),
            "card":str(args.card),"numpy":np.__version__}
    args.output.write_text(json.dumps(result,indent=2))
    print("Helicity worker: total",total,"individual_sum",
          result["sum_components"],flush=True)

if __name__=="__main__":
    main()
