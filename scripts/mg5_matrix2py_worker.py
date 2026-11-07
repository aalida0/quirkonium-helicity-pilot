#!/usr/bin/env python3
"""Isolated worker for the MG5_aMC 3.5 standalone matrix2py extension.

This must be a subprocess: an MG5/Fortran STOP can terminate a Python
interpreter with exit status 0, before get_value is ever reached. The parent
must require a fresh structured result file to certify numerical evaluation.
Never write model/SLHA inputs or create fake ident_card.dat content.
"""
import argparse
import importlib
import json
import os
from pathlib import Path
import sys

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-card",type=Path,required=True)
    p.add_argument("--momenta",type=Path,required=True,
                   help="JSON list of four [E,px,py,pz] vectors")
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--alpha-s",type=float,default=.118)
    a=p.parse_args()
    work=Path.cwd()
    ext=list(work.glob("matrix2py*.so"))
    if not ext:
        raise RuntimeError(f"Cannot find compiled matrix2py.so in {work}")
    if not a.model_card.is_file():
        raise RuntimeError(f"Model card missing: {a.model_card}")
    import numpy as np
    data=json.loads(a.momenta.read_text())
    if len(data)!=4 or any(len(row)!=4 for row in data):
        raise ValueError("Expected four 4-vectors [E,px,py,pz]")
    p4=np.asfortranarray(np.array(data,dtype=np.float64).T)
    sys.path.insert(0,str(work))
    module=importlib.import_module("matrix2py")
    initialise=getattr(module,"initialisemodel",None)
    evaluate=getattr(module,"get_value",None)
    if not callable(initialise) or not callable(evaluate):
        raise RuntimeError("matrix2py lacks documented initialisemodel/get_value")
    print(f"WORKER: cwd={work}",flush=True)
    print(f"WORKER: starting initialisemodel({a.model_card})",flush=True)
    initialise(str(a.model_card))
    print("WORKER: model initialized; calling get_value",flush=True)
    value=float(evaluate(p4,float(a.alpha_s),-1))
    print(f"WORKER: raw MG5 ME2={value:.16e}",flush=True)
    # If a Fortran STOP occurs before this write, parent detects missing proof.
    payload={"worker_status":"ME_EVALUATED","mg5_me2":value,
             "momentum_shape":list(p4.shape),"alpha_s":a.alpha_s,
             "model_card":str(a.model_card),"working_directory":str(work),
             "matrix2py_module":str(ext[0]),"numpy":np.__version__}
    a.output.write_text(json.dumps(payload,indent=2))
if __name__=="__main__":
    main()
