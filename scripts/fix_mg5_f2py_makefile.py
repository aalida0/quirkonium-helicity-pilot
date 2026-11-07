#!/usr/bin/env python3
"""Safely redirect MG5 3.5.1's stale f2py3.10 launcher to THIS Python.

This changes ONLY the generated standalone SubProcesses/P*/makefile files.
It does not modify the MG5 installation, model UFO, Fortran matrix, SLHA cards,
or a system Python executable. Explicit --apply required; backups retained.
Run this script with the SAME isolated Python interpreter that will import the
compiled matrix2py module (NumPy C API must match).
"""
import argparse
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
CHANNELS=("MG5_UL_DL_WZ","MG5_UL_DL_WA")
BACKUP="makefile.before_quirkonium_f2py"

def replace_launcher(source,python_exe):
    """Return patched makefile and count of hard-coded launcher occurrences."""
    launcher=shlex.quote(str(python_exe))+" -m numpy.f2py"
    # Replace the observed hard-coded command, not every f2py reference.
    updated,n=re.subn(r"(?<![\w./-])f2py3\.10(?![\w./-])",
                      lambda _:launcher,source)
    if n==0:
        if launcher in source:
            return source,0
        raise ValueError("No f2py3.10 launcher found. Examine makefile before editing.")
    return updated,n

def discover(root):
    paths=[]
    for name in CHANNELS:
        hits=sorted((root/name/"SubProcesses").glob("P*/makefile"))
        if len(hits)!=1:
            raise RuntimeError(f"{name}: expected 1 generated P*/makefile; got {len(hits)}")
        paths.extend(hits)
    return paths

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    p.add_argument("--apply",action="store_true",
                   help="Back up and edit generated standalone makefiles")
    args=p.parse_args()
    py=Path(sys.executable).resolve()
    check=subprocess.run([str(py),"-m","numpy.f2py","-v"],
                         capture_output=True,text=True)
    if check.returncode:
        raise RuntimeError(f"{py} cannot run numpy.f2py -v: "+
                           check.stderr[-1200:])
    import numpy
    print("Selected Python:",py)
    print("Selected NumPy/f2py:",numpy.__version__,check.stdout.strip())
    print("Build and import must use the same interpreter/NumPy ABI.")
    paths=discover(args.root.resolve())
    pending=[]
    for path in paths:
        raw=path.read_text()
        fixed,n=replace_launcher(raw,py)
        if fixed!=raw: pending.append((path,raw,fixed))
        print(f"{path}: stale launchers={n};"+
              (" PATCH PREVIEW" if fixed!=raw else " already patched"))
    if not args.apply:
        print("DRY RUN: no files changed. Pass --apply to save makefile backups.")
        return
    for path,raw,fixed in pending:
        backup=path.with_name(BACKUP)
        if backup.exists():
            if backup.read_text()!=raw:
                raise RuntimeError(f"{backup} exists and differs: refusing overwrite")
        else:
            shutil.copy2(path,backup)
        path.write_text(fixed)
        print("Patched:",path)
        print("Backup:",backup)
    if not pending:
        print("Already patched for this Python; no changes necessary.")
    print("Done: run mg5_matrix2py_compare.py with",py)

if __name__=="__main__":
    main()
