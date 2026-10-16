#!/usr/bin/env python3
"""Fetch each pricing page in tools.csv, extract text, diff vs last snapshot, log changes."""
import csv, json, re, sys, difflib, datetime, pathlib, urllib.request
from html.parser import HTMLParser
ROOT = pathlib.Path(__file__).resolve().parent.parent
SNAP, CHG = ROOT/"data/snapshots", ROOT/"data/changes"
class T(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in("script","style","noscript","svg"): s.skip+=1
    def handle_endtag(s,t):
        if t in("script","style","noscript","svg") and s.skip: s.skip-=1
    def handle_data(s,d):
        if not s.skip and d.strip(): s.out.append(re.sub(r"\s+"," ",d.strip()))
def slug(n): return re.sub(r"[^a-z0-9]+","-",n.lower()).strip("-")
def main():
    today=datetime.date.today().isoformat(); log=[]
    for r in csv.DictReader(open(ROOT/"tools.csv")):
        s=slug(r["tool"]); d=SNAP/s; d.mkdir(parents=True,exist_ok=True)
        try:
            req=urllib.request.Request(r["pricing_url"],headers={"User-Agent":"Mozilla/5.0 AIPriceWatchBot"})
            html=urllib.request.urlopen(req,timeout=30).read().decode("utf-8","ignore")
        except Exception as e:
            log.append({"tool":s,"status":"error","error":str(e)[:120]}); print(s,"ERR",e); continue
        p=T(); p.feed(html); text="\n".join(p.out)
        prev=sorted(d.glob("*.txt")); old=prev[-1].read_text() if prev else None
        (d/f"{today}.txt").write_text(text)
        if old is None: st="seeded"
        elif old==text: st="same"
        else:
            diff=[l for l in difflib.unified_diff(old.splitlines(),text.splitlines(),lineterm="",n=0) if l[:1] in "+-" and l[:3] not in("+++","---")]
            price=[l for l in diff if re.search(r"[$€£]\s?\d|/mo|month|year|credits|requests",l,re.I)]
            st="changed"
            (CHG/f"{today}-{s}.json").write_text(json.dumps({"tool":s,"date":today,"url":r["pricing_url"],"price_lines":price[:50],"all_lines":len(diff),"reviewed":False},indent=2))
        log.append({"tool":s,"status":st,"chars":len(text)}); print(s,st,len(text))
    (ROOT/"data/last_run.json").write_text(json.dumps({"date":today,"results":log},indent=2))
if __name__=="__main__": main()
