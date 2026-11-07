#!/usr/bin/env python3
"""Decisive fixed-width SLHA parser test for MG5_aMC 3.5.1 matrix2py.

Do not trust a 21-character formatted SLHA number in this workflow.
At identical original MSSM masses/kinematics, run:
  A: completely original card
  B: same card with *only* SMINPUTS[1] rewritten to compact 18-char .12E
  C: same card with *only* SMINPUTS[1] rewritten to unsafe 21-char .15E
Then, at the exact scalar M=500 GeV benchmark kinematics, compare the
historical long-format preview to the new compact preview. Neither model
source nor original SLHA cards are changed.

If A~B but C/A=(127.934/1.27934)^2, the old Fortran reader clipped the
exponent. That is a validation of a tool input bug, not proof that the
physical scalar model matches MSSM. A physical ME validation still needs
consistent model couplings and line-by-line diagram comparison.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mg5_threshold_preflight import parse_card, replace_card, format_slha_number
from mg5_matrix2py_compare import prepare, stage_ident_card, evaluate_in_worker
from mg5_discrepancy_audit import ps_at_relative_q

def alpha_long_and_compact(original):
    data,_=parse_card(original)
    key=("SMINPUTS",1)
    if key not in data:raise RuntimeError("Missing alpha_inv SMINPUTS[1]")
    value=data[key]
    compact,found=replace_card(original,{key:value})
    if found!={key}:raise RuntimeError("Failed to rewrite only SMINPUTS[1]")
    short=format_slha_number(value)
    long=f"{value:.15E}"
    assert len(long)>20 and len(short)<=20
    if compact.count(short)!=1:
        raise RuntimeError("Expected exactly one short-format alpha input")
    wide=compact.replace(short,long,1)
    return compact,wide,{"alpha_inv":value,"compact":short,
                          "long":long,"compact_length":len(short),
                          "long_length":len(long)}

def evaluate_variant(work,path,card,ps,folder):
    folder.mkdir(parents=True,exist_ok=True)
    if isinstance(card,str):
        target=folder/"param_card_experiment.dat"
        target.write_text(card)
        path=target
    return evaluate_in_worker(work,path,ps,.118,folder)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",type=Path,default=ROOT/"validation/local_logs")
    ap.add_argument("--mass",type=float,default=500.)
    ap.add_argument("--tanbeta",type=float,default=3.)
    ap.add_argument("--channel",choices=("Z","gamma","both"),default="both")
    args=ap.parse_args()
    base=args.root.resolve()
    results={"M":args.mass,"tanbeta":args.tanbeta,"channels":{}}
    channels=("Z","gamma") if args.channel=="both" else (args.channel,)
    for channel in channels:
        model,work,compact_review,b,ref_ps=prepare(channel,args.mass,args.tanbeta,base)
        stage_ident_card(model,work)
        original=model/"Cards/param_card.dat"
        text=original.read_text()
        short,long,format_info=alpha_long_and_compact(text)
        values,_=parse_card(text)
        orig_ps=ps_at_relative_q(
            values[("MASS",1000002)],values[("MASS",1000001)],
            values[("MASS",24)],
            values[("MASS",23)] if channel=="Z" else 0.,0.,0.)
        prefix=base/"threshold_benchmarks"/(
            f"M{args.mass:g}_tanbeta{args.tanbeta:g}_{channel}")/"slha_width_gate"
        variants=[
            ("original_raw",original,orig_ps),
            ("original_alpha_reformatted_short",short,orig_ps),
            ("original_alpha_reformatted_unsafe_long",long,orig_ps),
            ("review_compact",compact_review,ref_ps),
        ]
        old=model/"Cards/param_card_quirkonium_review.dat"
        if old.is_file():variants.append(("review_old_long",old,ref_ps))
        out={"alpha_format":format_info,"cases":{}}
        for label,card,ps in variants:
            folder=prefix/label
            path=card if isinstance(card,Path) else folder/"param_card_experiment.dat"
            try:
                value=evaluate_variant(work,path,card,ps,folder)
                item={"status":"EVALUATED","ME2":value,
                      "card":str(path)}
                print(f"{channel:>5} {label:<39} {value:.16e}",flush=True)
            except Exception as exc:
                item={"status":"ERROR","error":str(exc),"card":str(path)}
                print(f"{channel:>5} {label:<39} ERROR {exc}",flush=True)
            out["cases"][label]=item
        cases=out["cases"]
        def val(label):
            c=cases.get(label)
            return c.get("ME2") if c is not None else None
        base_val=val("original_raw")
        compact_val=val("original_alpha_reformatted_short")
        wide_val=val("original_alpha_reformatted_unsafe_long")
        if base_val and compact_val and wide_val:
            target=(format_info["alpha_inv"]/float(
                format_info["long"].split("E",1)[0]))**2
            out["same_numeric_alpha_reformat"]={
                "compact_over_original":compact_val/base_val,
                "unsafe_long_over_original":wide_val/base_val,
                "predicted_factor_if_exponent_omitted":target,
                "short_preserves_baseline":math.isclose(
                    compact_val,base_val,rel_tol=1.e-8,abs_tol=1.e-10),
                "long_matches_exponent_omission_signature":math.isclose(
                    wide_val/base_val,target,rel_tol=1.e-7)}
            print(channel,"FORMAT DIAG:",out["same_numeric_alpha_reformat"])
        if val("review_compact") is not None and val("review_old_long") is not None:
            out["preview_long_vs_short_ratio"]=(
                val("review_old_long")/val("review_compact")
                if val("review_compact") else None)
        results["channels"][channel]=out
    dest=base/"threshold_benchmarks"/(
        f"M{args.mass:g}_tanbeta{args.tanbeta:g}_slha_width_gate.json")
    dest.write_text(json.dumps(results,indent=2))
    print("Saved:",dest)
    print("Parser diagnosis is separate from full physical ME validation.")
if __name__=="__main__":main()
