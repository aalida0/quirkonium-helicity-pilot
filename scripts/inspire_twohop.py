#!/usr/bin/env python3
"""INSPIRE two-hop citation graph audit. Python 3.10+ standard library.

Fetches complete first-hop citing/cited edges and relevance-selected second-hop
edges. Run --expand-all for all second-hop records (can be expensive).
Writes exact hits/page coverage, unresolved references and failures. It does
NOT validate full-text overlap or prove publication novelty.
"""
import argparse
from datetime import datetime,timezone
import hashlib,json,re,sys,time
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen
BASE="https://inspirehep.net/api"
SEEDS={
 "Fok_Kribs":("arxiv","1106.3101"),
 "Forsyth_2025":("arxiv","2504.02940"),
 "Burdman_2008":("arxiv","0805.4667"),
 "Cheung_Keung_Yuan":("doi","10.1016/j.nuclphysb.2008.11.029"),
 "Kahawala_Kats":("doi","10.1007/JHEP09(2011)099"),
 "Li_2018":("doi","10.1103/PhysRevD.97.015010"),
 "Forsyth_erratum":("doi","10.1103/lwnc-cmpn")}
FIELDS="titles,authors.full_name,dois,arxiv_eprints,citation_count,abstracts"
def title(m):return next((t.get("title","") for t in m.get("titles",[])),"")
def score(m):
 s=(title(m)+" "+" ".join(a.get("value","") for a in m.get("abstracts",[]))).lower()
 weights={"quirk":12,"squirk":12,"helicit":8,"polariz":8,
          "angular":4,"wz":5,"bound state":3,"spin correlat":5}
 return sum(w for k,w in weights.items() if k in s)
def refids(m):
 found=set();unresolved=[]
 for e in m.get("references",[]):
  r=e.get("reference",{})
  link=r.get("record") or e.get("record") or {}
  url=link.get("$ref","") if isinstance(link,dict) else str(link)
  match=re.search(r"/literature/(\d+)",url)
  if match:found.add(match.group(1))
  else:unresolved.append({"title":r.get("title"),
       "arxiv":r.get("arxiv_eprint"),"texkey":r.get("texkey")})
 return found,unresolved
class Api:
 def __init__(self,root,delay):
  self.dir=root/"raw_api";self.dir.mkdir(parents=True,exist_ok=True)
  self.delay=delay;self.last=0.;self.log=[]
 def get(self,url):
  if not url.startswith(BASE+"/") or urlparse(url).netloc!="inspirehep.net":
   raise ValueError("Unexpected INSPIRE API host")
  cache=self.dir/(hashlib.sha256(url.encode()).hexdigest()+".json")
  if cache.exists():return json.loads(cache.read_text())
  for attempt in range(4):
   time.sleep(max(0.,self.delay-(time.monotonic()-self.last)))
   self.last=time.monotonic()
   try:
    with urlopen(Request(url,headers={"Accept":"application/json",
       "User-Agent":"Quirkonium-INSPIRE-twohop-audit/1.0"}),timeout=40) as r:
     data=json.load(r)
    cache.write_text(json.dumps(data,indent=2))
    self.log.append({"url":url,"status":200})
    return data
   except HTTPError as exc:
    self.log.append({"url":url,"status":exc.code})
    if exc.code not in (429,500,502,503,504) or attempt==3:raise
   except (URLError,TimeoutError) as exc:
    self.log.append({"url":url,"error":str(exc)})
    if attempt==3:raise
   time.sleep(min(20,2**attempt*2))
 def record(self,key,value):return self.get(BASE+"/"+key+"/"+value)
 def search(self,query,limit):
  page=1;results=[];total=None
  while True:
   args=urlencode({"q":query,"size":100,"page":page,"fields":FIELDS})
   result=self.get(BASE+"/literature?"+args)
   h=result.get("hits",{})
   if total is None:
    total=h.get("total",0)
    if isinstance(total,dict):total=total.get("value",0)
   hits=h.get("hits",[]);results.extend(hits)
   if limit and len(results)>=limit:
    return results[:limit],total,len(results)<total,page
   if not hits or len(results)>=total:return results,total,False,page
   if page>=100 or len(results)>=9900:return results,total,True,page
   page+=1
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--output",default="validation/inspire_audit")
 p.add_argument("--delay",type=float,default=.45)
 p.add_argument("--min-score",type=int,default=10)
 p.add_argument("--max-secondary",type=int,default=0)
 p.add_argument("--max-per-query",type=int,default=0)
 p.add_argument("--expand-all",action="store_true")
 a=p.parse_args();root=Path(a.output)
 root.mkdir(parents=True,exist_ok=True)
 api=Api(root,a.delay);registry={};seedids=set()
 frontier=set();edges=[];queries=[];errors=[]
 def keep(item):
  rid=str(item.get("id",""))
  meta=item.get("metadata",{})
  if rid:registry[rid]={"title":title(meta),"score":score(meta),
    "arxiv":[v.get("value") for v in meta.get("arxiv_eprints",[])],
    "doi":[v.get("value") for v in meta.get("dois",[])],
    "authors":[v.get("full_name") for v in meta.get("authors",[])]}
  return rid
 for label,(kind,key) in SEEDS.items():
  try:
   recid=keep(api.record(kind,key))
   if recid:seedids.add(recid)
   queries.append({"seed":label,"recid":recid,"status":"OK"})
  except Exception as exc:errors.append({"seed":label,"error":str(exc)})
 try:
  query="find e thesis and title Characterizing Quirky Signals"
  items,total,trunc,pages=api.search(query,100)
  queries.append({"query":query,"total":total,"pages":pages,"truncated":trunc})
  for x in items:
   if "characterizing quirky signals" in title(x.get("metadata",{})).lower():
    seedids.add(keep(x))
 except Exception as exc:errors.append({"thesis":"Characterizing Quirky Signals","error":str(exc)})
 for rid in sorted(seedids):
  try:
   rec=api.record("literature",rid)
   refs,missing=refids(rec.get("metadata",{}))
   (root/("unresolved_refs_"+rid+".json")).write_text(json.dumps(missing,indent=2))
   for dst in refs:
    edges.append({"from":rid,"to":dst,"depth":1,"type":"reference"})
    frontier.add(dst)
   query="refersto:recid:"+rid
   items,total,trunc,pages=api.search(query,a.max_per_query)
   for x in items:
    src=keep(x)
    edges.append({"from":src,"to":rid,"depth":1,"type":"citing"})
    frontier.add(src)
   queries.append({"seed_recid":rid,"references":len(refs),
    "unresolved":len(missing),"forward_total":total,
    "forward_retrieved":len(items),"pages":pages,"truncated":trunc})
  except Exception as exc:errors.append({"seed_recid":rid,"error":str(exc)})
 for rid in sorted(frontier):
  if rid not in registry:
   try:keep(api.record("literature",rid))
   except Exception as exc:errors.append({"recid":rid,"error":str(exc)})
 ranked=sorted(frontier-seedids,
          key=lambda r:(-registry.get(r,{}).get("score",0),r))
 selected=ranked if a.expand_all else [r for r in ranked
             if registry.get(r,{}).get("score",0)>=a.min_score]
 if a.max_secondary and len(selected)>a.max_secondary:
  queries.append({"second_hop_truncated":len(selected)-a.max_secondary})
  selected=selected[:a.max_secondary]
 for rid in selected:
  try:
   refs,missing=refids(api.record("literature",rid).get("metadata",{}))
   for dst in refs:edges.append({"from":rid,"to":dst,"depth":2,"type":"reference"})
   items,total,trunc,pages=api.search("refersto:recid:"+rid,a.max_per_query)
   for x in items:edges.append({"from":keep(x),"to":rid,"depth":2,"type":"citing"})
   queries.append({"second_hop_recid":rid,"references":len(refs),
    "unresolved":len(missing),"forward_total":total,
    "forward_retrieved":len(items),"pages":pages,"truncated":trunc})
  except Exception as exc:errors.append({"second_hop_recid":rid,"error":str(exc)})
 audit={"utc":datetime.now(timezone.utc).isoformat(),"seeds":SEEDS,
        "resolved_seed_recids":sorted(seedids),"records":registry,
        "edges":edges,"second_hop_expanded":selected,"queries":queries,
        "errors":errors,"api_log":api.log}
 (root/"inspire_audit.json").write_text(json.dumps(audit,indent=2))
 with (root/"CITATION_RESULTS.md").open("w") as f:
  f.write("# INSPIRE two-hop audit\n\nUTC: "+audit["utc"]+"\n\n"+
    f"Resolved seeds: {len(seedids)}; records: {len(registry)}; "+
    f"edges: {len(edges)}; expanded second hop: {len(selected)}; errors: {len(errors)}.\n\n")
  f.write("## Query accounting\n\n"+json.dumps(queries,indent=2)+"\n\n")
  f.write("## Ranked source candidates\n\n")
  for rid in sorted(registry,key=lambda r:-registry[r]["score"])[:100]:
   f.write("- https://inspirehep.net/literature/"+rid+" ; "+
      registry[rid]["title"]+" ; score="+str(registry[rid]["score"])+"\n")
  if errors:f.write("\n## Errors\n\n"+json.dumps(errors,indent=2)+"\n")
  f.write("\nNote: metadata does NOT establish full-text equation-level novelty.\n")
 print("Saved audit to",root,"; error count",len(errors))
 return 2 if errors or any(x.get("truncated") for x in queries) else 0
if __name__=="__main__":sys.exit(main())
