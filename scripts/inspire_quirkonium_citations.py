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
# Independent journal bibliography confirms the 2025 paper cites the 2008
# paper: Forsyth et al., PRD 111 115021 (2025), reference [51], cites
# Burdman et al., PRD 78 075028 (2008), arXiv:0805.4667.
KNOWN_CITING_RELATIONS=(("scalar_2008","scalar_2025",
    "https://journals.aps.org/prd/abstract/10.1103/34xj-vz82 (ref. 51)"),)

def normalize_arxiv(value):
    return re.sub(r"v[0-9]+$","",str(value).strip(),flags=re.I)

def validate_citation_cross_checks(seeds):
    """Detect resolved-seed and pagination-success cases missing known edges.

    This is not a full citation audit: a false positive may reflect missing
    INSPIRE reference mapping. Either way, do NOT report graph complete.
    """
    issues=[]
    for label,item in seeds.items():
        meta=item.get("metadata",{})
        incoming=meta.get("citation_count")
        got=item.get("forward",{}).get("total")
        if isinstance(incoming,int) and isinstance(got,int):
            if incoming>=5 and (incoming-got)>max(5,0.2*incoming):
                issues.append({
                    "type":"COUNT_DISAGREEMENT","seed":label,
                    "metadata_citation_count":incoming,
                    "forward_search_total":got,
                    "reason":"INSPIRE count vs citing-query gap exceeds tolerance"})
        if "metadata" in item:
            expected=normalize_arxiv(item.get("arxiv",""))
            actual=[normalize_arxiv(a) for a in meta.get("arxiv",[])]
            if expected not in actual:
                issues.append({"type":"SEED_RESOLUTION_MISMATCH",
                    "seed":label,"requested":expected,
                    "resolved_ids":actual,"recid":meta.get("recid")})
    for cited,citing,source in KNOWN_CITING_RELATIONS:
        cited_item=seeds.get(cited,{})
        citing_item=seeds.get(citing,{})
        citing_id=citing_item.get("metadata",{}).get("recid")
        if not citing_id:continue
        hits=cited_item.get("forward",{}).get("items",[])
        ids={hit.get("recid") for hit in hits}
        if citing_id not in ids:
            issues.append({"type":"MISSING_DOCUMENTED_CITATION",
                "cited_seed":cited,"citing_seed":citing,
                "expected_citing_recid":citing_id,"source":source,
                "reason":"2025 paper's printed bibliography cites 2008 paper "
                         "but INSPIRE forward list omits it"})
    return issues


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
    evidence["citation_integrity_issues"]=validate_citation_cross_checks(
        evidence["seeds"])
    for issue in evidence["citation_integrity_issues"]:
        print("CITATION_INTEGRITY_WARNING:",json.dumps(issue))
    for issue in evidence["citation_integrity_issues"]:
        label=issue.get("seed") or issue.get("cited_seed")
        if label and label in evidence["seeds"]:
            evidence["seeds"][label]["status"]="INCONSISTENT"
    first=all(x["status"]=="COMPLETE" for x in evidence["seeds"].values())
    second=(args.depth==1 or (
        not evidence.get("unsearched_relevant_second_hops") and
        all(x["forward"]["complete"] for x in evidence["second_hop"].values())))
    evidence["complete_requested_scope"]=bool(
        first and second and not evidence["citation_integrity_issues"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(evidence,indent=2,ensure_ascii=False))
    print("Saved",args.output,"complete_requested_scope=",
          evidence["complete_requested_scope"])
    print("Even complete citation metadata does not establish that an observable is novel.")
    if not evidence["complete_requested_scope"]:raise SystemExit(2)

if __name__=="__main__":
    main()
