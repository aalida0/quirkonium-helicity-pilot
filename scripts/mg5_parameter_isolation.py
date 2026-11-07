#!/usr/bin/env python3
"""Isolate the cause of huge MG5/analytic amplitude mismatches.

A reproducible model-input diagnostic: generate transient copies of the two
MSSM_SLHA2 cards and evaluate both generated standalone matrix elements at
consistent on-shell kinematics. No edits to the original MG5 card, UFO,
matrix.f or our analytic model.

Factor categories:
  squarks: MASS 1000001,1000002 (incoming & exchanged squarks)
  ew:      SMINPUTS[1], MASS[23],[24] (electroweak sector)
  widths:  DECAY[23],[24],[1000001],[1000002]
  other:   MINPAR[3], HMIX[2] (tanbeta, if changed/present)

Cases: original; each one-factor modification; full review; full-minus each
factor. This distinguishes sensitivity to one group vs parameter interactions.
At q=0, initial scalar masses equal the parameter-card masses and outgoing
EW bosons are precisely on shell, with consistent four-momentum conservation.

CAUTION: some interposed MSSM cards are physically inconsistent. They are
diagnostic of generated amplitudes, NOT physical model benchmarks.

Run from repo root:
.venv-mg5-f2py/bin/python scripts/mg5_parameter_isolation.py
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mg5_matrix2py_compare import prepare,stage_ident_card,evaluate_in_worker
from mg5_threshold_preflight import parse_card,replace_card
from mg5_discrepancy_audit import ps_at_relative_q

GROUPS={
    "squarks":{("MASS",1000001),("MASS",1000002)},
    "ew":{("MASS",23),("MASS",24),("SMINPUTS",1)},
    "widths":{("DECAY",23),("DECAY",24),
              ("DECAY",1000001),("DECAY",1000002)},
    "other":{("MINPAR",3),("HMIX",2)},
}

def card_data(text):
    entries,widths=parse_card(text)
    return {**entries,**{("DECAY",k):v for k,v in widths.items()}}

def changed_group_updates(original,review,groups):
    """Build only entries that actually exist in original and review cards."""
    src=card_data(original)
    dest=card_data(review)
    allowed=set().union(*(GROUPS[g] for g in groups)) if groups else set()
    return {key:dest[key] for key in allowed
            if key in src and key in dest and src[key]!=dest[key]}

def on_shell_mass_tuple(card,channel):
    p=card_data(card)
    codes=(("MASS",1000002),("MASS",1000001),("MASS",24))
    missing=[key for key in codes if key not in p]
    if missing:raise ValueError(f"Card lacks external masses {missing}")
    mu,md,mw=(p[k] for k in codes)
    mv=0. if channel=="gamma" else p[("MASS",23)]
    if min(mu,md,mw)<=0 or mv<0:raise ValueError("Nonphysical masses in card")
    return mu,md,mw,mv

def build_cases(original,review):
    names=list(GROUPS)
    candidates={"original":set(),"full_review":set(names)}
    for name in names:
        candidates[f"{name}_only"]={name}
        candidates[f"full_except_{name}"]=set(names)-{name}
    cases=[]
    seen=set()
    for label,groups in candidates.items():
        updates=changed_group_updates(original,review,groups)
        changed_text,found=replace_card(original,updates)
        if found!=set(updates):
            raise ValueError(f"Failed to patch original card: {set(updates)-found}")
        digest=hashlib.sha256(changed_text.encode()).hexdigest()
        cases.append((label,sorted(groups),changed_text,digest,sorted(
            (str(key),val) for key,val in updates.items())))
        seen.add(digest)
    return cases,len(seen)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mass",type=float,default=500.)
    parser.add_argument("--tanbeta",type=float,default=3.)
    parser.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    parser.add_argument("--channel",choices=("Z","gamma","both"),default="both")
    args=parser.parse_args()
    base=args.root.resolve()
    report={"mass_reference":args.mass,"tanbeta_reference":args.tanbeta,
            "scope":"diagnostic_nonphysical_intermediate_cards",
            "channels":{}}
    for channel in ("Z","gamma") if args.channel=="both" else (args.channel,):
        model,work,review,b,ps=prepare(channel,args.mass,args.tanbeta,base)
        stage_ident_card(model,work)
        original=model/"Cards/param_card.dat"
        original_text=original.read_text()
        review_text=review.read_text()
        cases,unique=build_cases(original_text,review_text)
        directory=base/"threshold_benchmarks"/(
                  f"M{args.mass:g}_tanbeta{args.tanbeta:g}_{channel}")/"parameter_isolation"
        directory.mkdir(parents=True,exist_ok=True)
        print(f"\n{channel}: {len(cases)} cases, {unique} unique cards",flush=True)
        results={}
        cache={}
        for label,groups,card_text,digest,updates in cases:
            if digest in cache:
                entry=dict(cache[digest])
                entry["reused_from"]=cache[digest]["label"]
            else:
                case_dir=directory/label
                case_dir.mkdir(exist_ok=True)
                card=case_dir/"param_card_diagnostic.dat"
                card.write_text(card_text)
                try:
                    mu,md,mw,mv=on_shell_mass_tuple(card_text,channel)
                    momenta=ps_at_relative_q(mu,md,mw,mv,0.,0.)
                    val=evaluate_in_worker(work,card,momenta,.118,case_dir)
                    entry={"status":"EVALUATED","value":val,
                           "mu":mu,"md":md,"mw":mw,"mv":mv}
                except Exception as exc:
                    entry={"status":"ERROR","error":str(exc)}
                cache[digest]={**entry,"label":label}
            results[label]={**entry,"groups":groups,
                            "card_sha256":digest,"changed_entries":updates}
            val=entry.get("value")
            print(f"  {label:<30} "+(f"{val:.12e}" if val is not None
                  else f"ERROR {entry.get('error')}"),flush=True)
        report["channels"][channel]={"original_card":str(original),
                                     "review_card":str(review),
                                     "cases":results}
    outfile=base/"threshold_benchmarks"/(
            f"M{args.mass:g}_tanbeta{args.tanbeta:g}_parameter_isolation.json")
    outfile.write_text(json.dumps(report,indent=2))
    print("\nSaved:",outfile)
    print("This is an input-dependence diagnostic, not proof of a physical MSSM spectrum.")
if __name__=="__main__":
    main()
