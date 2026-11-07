#!/usr/bin/env python3
"""Pinpoint MG5 EW-input anomaly and verify card reconstruction fidelity.

Read-only for canonical generated MSSM cards and model source. Creates
temporary diagnostic SLHA copies and uses existing standalone matrix2py.

1. Compare the exact preflight review card against a reconstruction of all
   changed scalar SLHA entries, and separately the *old group-based* rebuild.
   A reconstructed case that differs cannot be used as a full-review control.
2. Evaluate exact review and reconstructed cards at identical kinematics.
3. Isolate SMINPUTS[1] (alpha_EM^-1) and MASS[24] (MW), independently and
   together, with original squark masses. Optionally include MASS[23].
4. Audit comments/source snippets for internal weak mixing and gauge couplings.

This is a diagnostic: temporary mixed MSSM spectra are not physical cards.
No modifications to original generated cards, matrix.f or analytic amplitudes.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mg5_parameter_isolation import (build_cases,card_data,on_shell_mass_tuple)
from mg5_threshold_preflight import replace_card
from mg5_matrix2py_compare import (prepare,stage_ident_card,evaluate_in_worker)
from mg5_discrepancy_audit import ps_at_relative_q

EW_KEYS=(("SMINPUTS",1),("MASS",24),("MASS",23))
CHECK_NAMES={
    ("SMINPUTS",1):"alpha_em_inverse",
    ("MASS",24):"mw",
    ("MASS",23):"mz",
}

def numeric_card_delta(original,review):
    a,b=card_data(original),card_data(review)
    removed={str(key):a[key] for key in a.keys()-b.keys()}
    added={str(key):b[key] for key in b.keys()-a.keys()}
    changed={str(key):{"original":a[key],"review":b[key]}
             for key in a.keys()&b.keys() if a[key]!=b[key]}
    return {"changed":changed,"added":added,"removed":removed}

def make_variant(original,review,keys):
    first,last=card_data(original),card_data(review)
    updates={key:last[key] for key in keys if key in last and key in first
             and last[key]!=first[key]}
    new,found=replace_card(original,updates)
    if found!=set(updates):
        raise RuntimeError(f"Card rewriting missed entries: {set(updates)-found}")
    return new

def make_cases(original,review):
    group_cases,_=build_cases(original,review)
    group_full=next(item[2] for item in group_cases if item[0]=="full_review")
    changed_keys={key for key,val in card_data(review).items()
                  if key in card_data(original) and
                  card_data(original)[key]!=val}
    all_changed=make_variant(original,review,changed_keys)
    cases={
        "original_exact":original,
        "full_review_exact":review,
        "full_review_group_rebuilt":group_full,
        "full_review_all_scalar_rebuilt":all_changed,
        "alpha_em_inverse_only":make_variant(original,review,{EW_KEYS[0]}),
        "mw_only":make_variant(original,review,{EW_KEYS[1]}),
        "mz_only":make_variant(original,review,{EW_KEYS[2]}),
        "alpha_and_mw_only":make_variant(original,review,set(EW_KEYS[:2])),
        "ew_group_only":make_variant(original,review,set(EW_KEYS)),
    }
    analysis={
       "review_vs_group_rebuilt":numeric_card_delta(group_full,review),
       "review_vs_all_scalar_rebuilt":numeric_card_delta(all_changed,review),
       "review_vs_original":numeric_card_delta(original,review),
       "text_group_diff":list(difflib.unified_diff(
           group_full.splitlines(),review.splitlines(),
           fromfile="group_rebuild",tofile="exact_review",lineterm=""))[:100],
       "text_all_scalar_diff":list(difflib.unified_diff(
           all_changed.splitlines(),review.splitlines(),
           fromfile="all_scalar_rebuild",tofile="exact_review",
           lineterm=""))[:100],
    }
    return cases,analysis

def source_ew_relations(model):
    source=model/"Source"/"MODEL"
    hits=[]
    expressions=re.compile(
        r"(MDL_)?(MW|MZ|SW|CW|EE|GW|G1|G2|VEV|VEVS|GSM|AEWM1)",re.I)
    for name in ("couplings.f","parameters.f","couplings.inc",
                 "param_read.inc","param_write.inc","input.inc"):
        p=source/name
        if not p.is_file():continue
        for lineno,line in enumerate(p.read_text(errors="replace").splitlines(),1):
            if expressions.search(line):
                hits.append({"file":str(p),"line":lineno,
                             "text":line.strip()[:220]})
                if len(hits)>=130:
                    return hits
    return hits

def diagnostic(channel,base,mass,tanbeta,probe):
    model,work,review,b,_=prepare(channel,mass,tanbeta,base)
    original=model/"Cards/param_card.dat"
    cases,diff=make_cases(original.read_text(),review.read_text())
    folder=base/"threshold_benchmarks"/f"M{mass:g}_tanbeta{tanbeta:g}_{channel}"/"ew_isolation"
    folder.mkdir(parents=True,exist_ok=True)
    result={"original_card":str(original),"exact_review_card":str(review),
            "differences":diff,"cases":{},
            "ew_model_source_lines":source_ew_relations(model)}
    if probe:
        stage_ident_card(model,work)
    for name,text in cases.items():
        digest=hashlib.sha256(text.encode()).hexdigest()
        canonical = original if name=="original_exact" else (
                    review if name=="full_review_exact" else None)
        root=folder/name
        root.mkdir(parents=True,exist_ok=True)
        card=canonical if canonical is not None else root/"test_param_card.dat"
        if canonical is None:
            card.write_text(text)
        mu,md,mw,mv=on_shell_mass_tuple(text,channel)
        ps=ps_at_relative_q(mu,md,mw,mv,0.,0.)
        val=None
        issue=None
        if probe:
            try:
                val=evaluate_in_worker(work,card,ps,.118,root)
            except Exception as error:
                issue=f"{type(error).__name__}: {error}"
        result["cases"][name]={
            "card_sha256":digest,"card":str(card),"mass":mu+md,
            "mu":mu,"md":md,"mw":mw,"mv":mv,
            "alpha_inverse":card_data(text).get(("SMINPUTS",1)),
            "me2":val,"error":issue,
        }
        print(f"{channel:>5} {name:<33} "
              f"alphaInv={result['cases'][name]['alpha_inverse']!s:<20} "
              f"MW={mw:<12g} Msum={mu+md:<12g} "
              + (f"ME2={val:.12g}" if val is not None else
                 f"ERROR={issue}" if issue else "NOT EVALUATED"),
              flush=True)
    orig=result["cases"]["original_exact"]["me2"]
    for name,data in result["cases"].items():
        data["ratio_to_original"]=(data["me2"]/orig
              if orig not in (0,None) and data["me2"] is not None else None)
    print("RECONSTRUCTION REVIEW ↔ GROUP:",diff["review_vs_group_rebuilt"])
    print("RECONSTRUCTION REVIEW ↔ ALL:",diff["review_vs_all_scalar_rebuilt"])
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mass",type=float,default=500.)
    p.add_argument("--tanbeta",type=float,default=3.)
    p.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    p.add_argument("--channel",choices=("Z","gamma","both"),default="both")
    p.add_argument("--probe",action="store_true",
                   help="Run actual compiled MG5 matrix2py for each temporary card")
    args=p.parse_args()
    base=args.root.expanduser().resolve()
    outcome={"scope":"card-reconstruction-and-ew-isolation",
             "mass":args.mass,"tanbeta":args.tanbeta,"channels":{}}
    channels=("Z","gamma") if args.channel=="both" else (args.channel,)
    for channel in channels:
        outcome["channels"][channel]=diagnostic(
            channel,base,args.mass,args.tanbeta,args.probe)
    filename=base/"threshold_benchmarks"/(
        f"M{args.mass:g}_tanbeta{args.tanbeta:g}_ew_isolation.json")
    filename.write_text(json.dumps(outcome,indent=2))
    print("Audit saved:",filename)
    print("Result is diagnostic; no model/analytic modification and no PASS claim.")
if __name__=="__main__":
    main()
