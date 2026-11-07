#!/usr/bin/env python3
"""Source-audited INSPIRE-HEP citation graph for charged quirkonium pilot.

Run from a networked workstation: python scripts/inspire_quirkonium_citations.py
This is a metadata graph, NOT a full-text novelty certification. Every
incomplete seed or truncated paginated response is reported explicitly.
"""
import argparse
import json
import re
import time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[1]
API="https://inspirehep.net/api"
SEEDS={"scalar_2008":"0805.4667","fermionic_2011":"1106.3101",
       "spin_bound_states_2011":"1103.3503","scalar_2025":"2504.02940"}
RELEVANT=re.compile(r"quirk|squirk|polariz|helicit|angular|diboson|spin",re.I)

def fetch_json(url,timeout=20):
    last=None
    for retry in range(3):
        try:
            request=Request(url,headers={"Accept":"application/json",
                            "User-Agent":"QuirkoniumHelicityPilot/1.0"})
            with urlopen(request,timeout=timeout) as response:
                return json.load(response)
        except (HTTPError,URLError,TimeoutError,ValueError) as error:
            last=error
            if retry<2:time.sleep(retry+1)
    raise RuntimeError(f"GET {url} failed: {last}")

def small_record(hit):
    meta=hit.get("metadata",{})
    titles=meta.get("titles") or []
    arxiv=meta.get("arxiv_eprints") or []
    doi=meta.get("dois") or []
    return {"recid":str(hit.get("id",meta.get("control_number",""))),
            "title":titles[0].get("title","") if titles else "",
            "arxiv":[x.get("value") for x in arxiv if x.get("value")],
            "doi":[x.get("value") for x in doi if x.get("value")],
            "citation_count":meta.get("citation_count")}

def references(record):
    out=[]
    for item in record.get("metadata",{}).get("references",[]):
        desc=item.get("reference") or {}
        identity=item.get("record") or {}
        title=desc.get("title")
        out.append({"record_url":identity.get("$ref",""),
                    "title":title.get("title","") if isinstance(title,dict) else "",
                    "arxiv":desc.get("arxiv_eprint"),
                    "label":desc.get("label")})
    return out

def citations(recid,max_pages):
    hits=[];errors=[];total=None;pages=0
    for n in range(1,max_pages+1):
        url=f"{API}/literature?"+urlencode(
              {"q":f"refersto:recid:{recid}","size":100,"page":n})
        try:data=fetch_json(url)
        except Exception as error:
            errors.append(str(error));break
        raw=data.get("hits",{})
        total=raw.get("total")
        if isinstance(total,dict):total=total.get("value")
        batch=raw.get("hits",[])
        hits.extend(small_record(x) for x in batch)
        pages+=1
        if not batch or (total is not None and len(hits)>=total):break
        if len(batch)<100:break
        time.sleep(.35)
    unique=list({item["recid"]:item for item in hits}.values())
    return {"recid":str(recid),"total":total,"page_count":pages,
            "page_limit":max_pages,"items":unique,"errors":errors,
            "complete":not errors and total is not None and len(hits)>=total}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depth",type=int,choices=(1,2),default=1)
    ap.add_argument("--max-pages",type=int,default=10)
    ap.add_argument("--max-second-hop",type=int,default=12)
    ap.add_argument("--output",type=Path,default=
        ROOT/"validation/local_logs/inspire_quirkonium_citation_graph.json")
    args=ap.parse_args()
    if args.max_pages<=0 or args.max_second_hop<0:
        ap.error("page limits must be positive")
    evidence={"generated_utc":datetime.now(timezone.utc).isoformat(),
              "depth_requested":args.depth,"source":API,
              "seeds":{},"second_hop":{},
              "scope":"citation_metadata_only_NOT_novelty_certification"}
    relevant={}
    for label,arxiv in SEEDS.items():
        entry={"arxiv":arxiv,"status":"INCOMPLETE"}
        try:
            record=fetch_json(f"{API}/arxiv/{quote(arxiv)}")
            if not record.get("id"):raise ValueError("Seed lacks INSPIRE recid")
            entry["metadata"]=small_record(record)
            entry["backward"]=references(record)
            entry["forward"]=citations(record["id"],args.max_pages)
            entry["status"]="COMPLETE" if entry["forward"]["complete"] else "INCOMPLETE"
            for hit in entry["forward"]["items"]:
                if RELEVANT.search(hit["title"]):
                    relevant[hit["recid"]]=hit
        except Exception as err:entry["error"]=str(err)
        evidence["seeds"][label]=entry
        print(label,entry["status"],"first-hop",
              len(entry.get("forward",{}).get("items",[])))
    if args.depth==2:
        for recid,hit in list(relevant.items())[:args.max_second_hop]:
            evidence["second_hop"][recid]={"seed":hit,
                  "forward":citations(recid,args.max_pages)}
        evidence["unsearched_relevant_second_hops"]=[
            hit for recid,hit in list(relevant.items())[args.max_second_hop:]]
    first=all(x["status"]=="COMPLETE" for x in evidence["seeds"].values())
    second=(args.depth==1 or (
        not evidence.get("unsearched_relevant_second_hops") and
        all(x["forward"]["complete"] for x in evidence["second_hop"].values())))
    evidence["complete_requested_scope"]=bool(first and second)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(evidence,indent=2,ensure_ascii=False))
    print("Saved",args.output,"complete_requested_scope=",
          evidence["complete_requested_scope"])
    print("Even complete citation metadata does not establish that an observable is novel.")
    if not evidence["complete_requested_scope"]:raise SystemExit(2)

if __name__=="__main__":
    main()
