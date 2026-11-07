#!/usr/bin/env python3
"""Construct on-shell threshold PS points, audit MG5 standalone cards and targets.

Read-only by default. --write-cards writes matched *copies*; --apply additionally
backs up and replaces generated Cards/param_card.dat. Does NOT evaluate an ME.
Requires the two standalone folders from madgraph/mssm_ew_procs.mg5.
"""
import argparse
import json
import math
import re
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import (Setup,MW,MZ,S2,ALPHA_W,
                                         helicities,splitting)
NAMES={"Z":"MG5_UL_DL_WZ","gamma":"MG5_UL_DL_WA"}

def momenta(b):
    M=b.M
    ew=(M*M+MW*MW-b.mv*b.mv)/(2*M)
    ev=M-ew
    p=math.sqrt(max(0.,ew*ew-MW*MW))
    return [(b.mu,0.,0.,0.),(b.md,0.,0.,0.),
            (ew,0.,0.,p),(ev,0.,0.,-p)]

def validate_ps(ps,masses):
    for k,m in zip(ps,masses):
        inv=k[0]**2-sum(x*x for x in k[1:])
        assert abs(inv-m*m)<1e-9*max(1.,m*m),(inv,m)
    for i in range(4):
        assert abs(ps[0][i]+ps[1][i]-ps[2][i]-ps[3][i])<1e-9

def parse_card(s):
    block=None; values={}; widths={}
    for line in s.splitlines():
        data=line.split("#",1)[0].strip()
        if not data:continue
        chunks=data.split()
        if chunks[0].upper()=="BLOCK":
            block=chunks[1].upper();continue
        if chunks[0].upper()=="DECAY" and len(chunks)>=3:
            block=None
            widths[int(chunks[1])]=float(chunks[2].replace("D","E"))
            continue
        if block and len(chunks)>=2 and re.fullmatch(r"-?\d+",chunks[0]):
            try:values[(block,int(chunks[0]))]=float(chunks[1].replace("D","E"))
            except ValueError:pass
    return values,widths

def replace_card(text,updates):
    block=None;found=set();out=[]
    for line in text.splitlines(keepends=True):
        prefix,sep,comment=line.partition("#")
        b=re.match(r"^\s*BLOCK\s+(\S+)",prefix,re.I)
        if b:
            block=b.group(1).upper();out.append(line);continue
        d=re.match(r"^(\s*DECAY\s+(-?\d+)\s+)(\S+)(.*)$",prefix,re.I)
        if d:
            block=None;key=("DECAY",int(d.group(2)))
            if key in updates:
                found.add(key)
                prefix=d.group(1)+f"{updates[key]:.15E}"+d.group(4)
                out.append(prefix+("#"+comment if sep else "\n"))
            else:out.append(line)
            continue
        if block:
            m=re.match(r"^(\s*(-?\d+)\s+)(\S+)(.*)$",prefix)
            if m:
                key=(block,int(m.group(2)))
                if key in updates:
                    found.add(key)
                    prefix=m.group(1)+f"{updates[key]:.15E}"+m.group(4)
                    out.append(prefix+("#"+comment if sep else "\n"))
                    continue
        out.append(line)
    return "".join(out),found

def reference(b):
    ts,long=helicities(b)
    m2=sum(x*x for x in ts)+(0 if long is None else long*long)
    return {"analytic_fixed_color_helicity_sum":m2,
            "candidate_MG5_color_averaged_if_denominator_3":m2/3,
            "transverse_sum":sum(x*x for x in ts),
            "longitudinal_sum":0 if long is None else long*long}

def run():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    p.add_argument("--mass",type=float,default=500.)
    p.add_argument("--tanbeta",type=float,default=3.)
    p.add_argument("--write-cards",action="store_true")
    p.add_argument("--apply",action="store_true",
                   help="Back up and activate matched param cards")
    args=p.parse_args()
    if args.apply and not args.write_cards:p.error("--apply requires --write-cards")
    if args.mass<=MW+MZ or args.tanbeta<=0:p.error("unphysical mass/tanbeta")
    delta=splitting(args.mass,args.tanbeta)
    report={"M_GeV":args.mass,"tanbeta":args.tanbeta,"delta_GeV":delta,
            "inputs":{"MW":MW,"MZ":MZ,"alphaW":ALPHA_W,"sin2thetaW":S2},
            "channels":{}}
    folder=args.root/"threshold_benchmarks"
    folder.mkdir(parents=True,exist_ok=True)
    for V,name in NAMES.items():
        out=args.root/name
        mats=sorted((out/"SubProcesses").glob("P*/matrix.f"))
        if len(mats)!=1:raise RuntimeError(f"{name}: expected 1 matrix.f; got {len(mats)}")
        card=out/"Cards/param_card.dat"
        if not card.is_file():raise RuntimeError(f"{name}: no parameter card: {card}")
        b=Setup(args.mass,delta,V)
        ps=momenta(b)
        validate_ps(ps,[b.mu,b.md,MW,b.mv])
        check_sa=mats[0].parent/"check_sa.f"
        matrix_text=mats[0].read_text(errors="replace")
        fragments=re.findall(r"\bIDEN\s*(?:\([^)]*\))?[^\n]{0,80}",
                             matrix_text,re.I)
        prior,prior_width=parse_card(card.read_text())
        gf=math.pi*ALPHA_W/(math.sqrt(2)*MW**2)
        updates={("MASS",1000002):b.mu,("MASS",1000001):b.md,
                 ("MASS",23):MZ,("MASS",24):MW,
                 ("SMINPUTS",1):1/(ALPHA_W*S2),("SMINPUTS",2):gf,
                 ("DECAY",23):0.,("DECAY",24):0.,
                 ("DECAY",1000001):0.,("DECAY",1000002):0.,
                 ("MINPAR",3):args.tanbeta,("HMIX",2):args.tanbeta}
        matched,found=replace_card(card.read_text(),updates)
        required={("MASS",1000002),("MASS",1000001),("MASS",23),
                  ("SMINPUTS",1),("SMINPUTS",2)}
        if not required.issubset(found):
            raise RuntimeError(f"{card} lacks required entries {required-found}")
        stem=f"M{args.mass:g}_tanbeta{args.tanbeta:g}_{V}"
        target=folder/stem
        target.mkdir(exist_ok=True)
        psfile=target/"PS.input"
        psfile.write_text("".join(" ".join(f"{v:.16E}" for v in k)+"\n" for k in ps))
        payload={"model_dir":str(out),"matrix_file":str(mats[0]),
                 "check_sa":str(check_sa),"check_sa_exists":check_sa.is_file(),
                 "check_sa_has_READPS":("READPS" in check_sa.read_text(errors="replace")
                                        if check_sa.is_file() else False),
                 "IDEN_source_fragments":fragments[:8],
                 "default_MASS":{str(i):prior.get(("MASS",i))
                                 for i in (1000001,1000002,23,24)},
                 "default_SMINPUTS":{str(i):prior.get(("SMINPUTS",i))
                                     for i in (1,2)},
                 "default_widths":{str(i):prior_width.get(i)
                                    for i in (23,24,1000001,1000002)},
                 "matched_up_squark_mass_GeV":b.mu,
                 "matched_down_squark_mass_GeV":b.md,
                 "missing_optional_card_entries":[str(x) for x in updates if x not in found],
                 "PS_input":str(psfile),**reference(b)}
        if args.write_cards:
            dest=card.with_name("param_card_quirkonium_matched.dat")
            dest.write_text(matched)
            payload["matched_card"]=str(dest)
            if args.apply:
                backup=card.with_name("param_card_before_quirkonium.dat")
                if backup.exists():raise RuntimeError(
                    f"{backup} already exists. Stop; do not overwrite backup.")
                shutil.copy2(card,backup)
                shutil.copy2(dest,card)
                payload["applied"]=True
                payload["backup"]=str(backup)
        report["channels"][V]=payload
        print(f"{V}: expected |M|²_fixed_color={payload['analytic_fixed_color_helicity_sum']:.12g}, "
              f"MG5 target *if* color denominator=3: "
              f"{payload['candidate_MG5_color_averaged_if_denominator_3']:.12g}")
        print(f"  PS.input: {psfile}; READPS supported? {payload['check_sa_has_READPS']}")
    output=folder/f"M{args.mass:g}_tanbeta{args.tanbeta:g}_preflight.json"
    output.write_text(json.dumps(report,indent=2))
    print("Saved manifest:",output)
    print("Status: PREPARED only; MadGraph numerical matrix element NOT EVALUATED.")
    if not args.write_cards:
        print("Model cards unmodified (read-only). Add --write-cards to create copies.")
    elif not args.apply:
        print("Matched cards created but NOT activated. Use --apply to back up and activate.")
if __name__=="__main__":run()
