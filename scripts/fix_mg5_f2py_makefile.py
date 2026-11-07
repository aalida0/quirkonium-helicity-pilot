#!/usr/bin/env python3
"""Fix MG5 3.5.1 standalone f2py3.10 without touching system Python.

Important:
  * Keep the virtualenv interpreter path: resolving its symlink points to
    /usr/bin/python3.10 and loses the venv site packages.
  * A generated makefile may construct "f2py3.10" from a make variable.
    In that case put a local launcher in the venv's bin directory, instead
    of assuming the literal name appears in the makefile.
  * The matrix2py builder separately puts this bin directory at the front
    of PATH when running make.

Run with .venv-mg5-f2py/bin/python and --apply. Only the generated
standalone makefiles (when the command is literal) and the venv bin shim
(when the command is constructed) can be changed. Backups are retained.
"""
import argparse
import os
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
    """Replace a *literal* f2py3.10 if it is present; otherwise raise."""
    launcher=shlex.quote(str(python_exe))+" -m numpy.f2py"
    updated,n=re.subn(r"(?<![\w./-])f2py3\.10(?![\w./-])",
                      lambda _:launcher,source)
    if n==0:
        if launcher in source:
            return source,0
        raise ValueError("No f2py3.10 launcher found. Make may expand a variable.")
    return updated,n

def shim_source(python_exe):
    """POSIX wrapper; calls *venv* Python, not resolved system executable."""
    return ("#!/bin/sh\nexec "+
            shlex.quote(str(python_exe))+' -m numpy.f2py "$@"\n')

def discover(root):
    paths=[]
    for name in CHANNELS:
        hits=sorted((root/name/"SubProcesses").glob("P*/makefile"))
        if len(hits)!=1:
            raise RuntimeError(f"{name}: expected 1 P*/makefile; got {len(hits)}")
        paths.extend(hits)
    return paths

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    p.add_argument("--apply",action="store_true",
                   help="Create a venv-local launcher and/or back up generated makefiles")
    args=p.parse_args()
    # Do NOT use .resolve(): the venv python symlink often points at /usr/bin.
    py=Path(os.path.abspath(sys.executable))
    if sys.prefix==sys.base_prefix:
        raise RuntimeError("Refusing to create a system-wide launcher. "
                           "Use .venv-mg5-f2py/bin/python for this script.")
    if py.parent != Path(sys.prefix)/"bin":
        raise RuntimeError(f"Interpreter {py} is not inside virtualenv {sys.prefix}/bin")
    import numpy
    version=subprocess.run([str(py),"-m","numpy.f2py","-v"],
                           capture_output=True,text=True)
    if version.returncode:
        raise RuntimeError(f"{py} cannot run numpy.f2py: "+version.stderr[-1200:])
    print("Selected virtualenv Python:",py)
    print("NumPy:",numpy.__version__,"f2py:",version.stdout.strip())
    if not version.stdout.strip().startswith(numpy.__version__):
        raise RuntimeError("Interpreter's NumPy and f2py version disagree; "
                           "do not mix build environments.")
    targets=discover(args.root.resolve())
    pending=[]
    needs_shim=False
    for path in targets:
        original=path.read_text()
        try:
            updated,count=replace_launcher(original,py)
        except ValueError:
            updated,count=original,0
            needs_shim=True
        if updated!=original:pending.append((path,original,updated))
        print(f"{path}: literal replacements={count}; "+
              ("venv-local shim needed" if updated==original and needs_shim
               else "patched Makefile" if updated!=original else "already patched"))
    shim=py.parent/"f2py3.10"
    expected_shim=shim_source(py)
    existing_compatible=False
    if needs_shim and shim.exists() and shim.read_text()!=expected_shim:
        # NumPy 1.26 may *already* install f2py3.10 as a valid venv script.
        # Do not overwrite or reject it just because it is not our shell shim.
        if not shim.is_file() or not os.access(shim,os.X_OK):
            raise RuntimeError(f"Existing venv launcher is not executable: {shim}")
        probe=subprocess.run([str(shim),"-v"],capture_output=True,
                             text=True,timeout=20)
        if probe.returncode or not probe.stdout.strip().startswith(numpy.__version__):
            raise RuntimeError(
                f"Existing venv launcher is incompatible, not overwriting {shim}. "
                f"Exit={probe.returncode} stdout={probe.stdout[-250:]} "
                f"stderr={probe.stderr[-250:]}")
        existing_compatible=True
        print("Verified existing compatible venv f2py3.10:",shim)
    print("Venv f2py3.10:",shim if needs_shim else "not needed")
    if not args.apply:
        print("DRY RUN: no changes. Add --apply to update local files.")
        return
    # Preflight backup conflicts before making any changes.
    for path,original,updated in pending:
        backup=path.with_name(BACKUP)
        if backup.exists() and backup.read_text()!=original:
            raise RuntimeError(f"Existing backup differs: {backup}; refusing.")
    if needs_shim and not shim.exists():
        shim.write_text(expected_shim)
        shim.chmod(0o755)
        print("Created venv-local launcher:",shim)
    elif needs_shim and existing_compatible:
        print("Using existing compatible venv-local f2py3.10:",shim)
    elif needs_shim:
        # Our previously generated shim has already been checked for content.
        shim.chmod(shim.stat().st_mode|0o111)
        print("Using existing matching local shim:",shim)
    for path,original,updated in pending:
        backup=path.with_name(BACKUP)
        if not backup.exists():shutil.copy2(path,backup)
        path.write_text(updated)
        print("Updated generated Makefile:",path)
        print("Backup:",backup)
    print("Done. Run the matrix2py comparison using exactly:",py)

if __name__=="__main__":
    main()
