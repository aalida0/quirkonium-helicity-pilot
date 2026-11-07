#!/usr/bin/env python3
"""Attempt a *real* MadGraph5 standalone check at the prepared threshold point.

Requires scripts/mg5_threshold_preflight.py --write-cards --apply first.
Runs only when generated check_sa.f implements READPS. Otherwise stops and
prints an actionable diagnostic; never substitutes a random RAMBO point.
This saves raw MG5 results, which MUST still be parsed and compared.
"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def patch_readps(raw):
    """Change only the documented standalone READPS and NPSPOINTS flags."""
    pattern=r"(PARAMETER\s*\(\s*READPS\s*=\s*)\.FALSE\."
    fixed,n=re.subn(pattern,lambda x:x.group(1)+".TRUE.",raw,flags=re.I)
    if n==0 and not re.search(r"PARAMETER\s*\(\s*READPS\s*=\s*\.TRUE\.",
                              raw,re.I):
        raise RuntimeError("This check_sa.f has no documented READPS flag. "
                           "Please inspect it; do not use random RAMBO values.")
    pattern=r"(PARAMETER\s*\(\s*NPSPOINTS\s*=\s*)\d+"
    fixed,nps=re.subn(pattern,lambda x:x.group(1)+"1",fixed,flags=re.I)
    if nps==0:
        raise RuntimeError("This check_sa.f has no NPSPOINTS parameter; "
                           "the exact PS.input calling convention must be inspected.")
    return fixed

def run(args):
    base=Path(args.root).expanduser().resolve()
    stem=f"M{args.mass:g}_tanbeta{args.tanbeta:g}"
    manifest=base/"threshold_benchmarks"/f"{stem}_preflight.json"
    if not manifest.exists():
        raise RuntimeError("Missing manifest; run mg5_threshold_preflight.py "
                           f"--mass {args.mass} --tanbeta {args.tanbeta} "
                           "--write-cards --apply")
    data=json.loads(manifest.read_text())
    for V,item in data["channels"].items():
        if not item.get("applied"):
            raise RuntimeError(f"{V}: matched card not activated. "
                               "Run preflight --write-cards --apply first.")
        pp=Path(item["matrix_file"]).parent
        code=pp/"check_sa.f"
        if not code.is_file():raise RuntimeError(
            f"{V}: {code} missing. Need MG5 version-specific driver.")
        orig=code.read_text()
        fixed=patch_readps(orig)
        backup=pp/"check_sa_before_quirkonium.f"
        if not backup.exists():shutil.copy2(code,backup)
        if fixed!=orig:code.write_text(fixed)
        ps=Path(item["PS_input"])
        shutil.copy2(ps,pp/"PS.input")
        dest=manifest.parent/f"{stem}_{V}"
        dest.mkdir(exist_ok=True)
        log=dest/"madgraph_check.log"
        print(f"{V}: compiling with make check in {pp}")
        compilation=subprocess.run(["make","check"],cwd=pp,capture_output=True,
                                   text=True,timeout=180)
        (dest/"compile.log").write_text(compilation.stdout+"\n"+compilation.stderr)
        if compilation.returncode:
            raise RuntimeError(f"{V} make check failed; inspect {dest/'compile.log'}")
        executable=pp/"check"
        if not executable.is_file():
            raise RuntimeError(f"{V}: make check exited 0 but no check binary")
        result=subprocess.run([str(executable)],cwd=pp,capture_output=True,
                              text=True,timeout=60)
        log.write_text(result.stdout+"\n"+result.stderr)
        if result.returncode or re.search(r"^\s*(ERROR|FATAL)\s*[: ]",
                                          result.stdout+"\n"+result.stderr,
                                          re.I|re.M):
            raise RuntimeError(f"{V}: ./check failed, see {log}")
        print(f"{V}: ./check completed; full raw stdout at {log}")
        for line in (result.stdout+"\n"+result.stderr).splitlines():
            if re.search("matrix|squared|result|amplitude",line,re.I):
                print(" ",line[:400])
    print("ME numerical agreement: STILL UNVERIFIED. "
          "Read raw check logs and compare to the threshold reference; "
          "confirm parameter card and color averaging.")
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",default=str(ROOT/"validation/local_logs"))
    p.add_argument("--mass",type=float,default=500.)
    p.add_argument("--tanbeta",type=float,default=3.)
    run(p.parse_args())
