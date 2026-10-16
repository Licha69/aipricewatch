#!/usr/bin/env python3
"""Render quarterly Wayback captures with headless Chromium; save visible text."""
import sys, pathlib, re
from playwright.sync_api import sync_playwright
R=pathlib.Path(__file__).resolve().parent.parent
tool=sys.argv[1]; out=R/"data/wayback_rendered"/tool; out.mkdir(parents=True,exist_ok=True)
caps=[]  # (ts,url)
for f in sorted((R/"data/wayback"/tool).glob("*.txt")):
    first=f.read_text().split("\n",1)[0]; m=re.search(r"web/(\d+)/(.*)",first)
    if m: caps.append((m.group(1),m.group(2)))
caps+= [tuple(a.split(" ",1)) for a in sys.argv[2:]]
seen=set(); pick=[]
for ts,u in sorted(caps):
    q=(ts[:4],(int(ts[4:6])-1)//2)   # one per 2 months
    if q in seen: continue
    seen.add(q); pick.append((ts,u))
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    for ts,u in pick:
        f=out/f"{ts[:8]}.txt"
        if f.exists() and f.stat().st_size>400: continue
        pg.wait_for_timeout(4000)
        url=f"https://web.archive.org/web/{ts}/{u}"
        try:
            pg.goto(url,timeout=90000,wait_until="domcontentloaded"); pg.wait_for_timeout(8000)
            t=pg.inner_text("body")
            if "Internal Server Error" in t[:200] or len(t)<200: print(tool,ts,"bad"); continue
        except Exception as e: print(tool,ts,"err",str(e)[:80]); continue
        f.write_text("ARCHIVE "+url+"\n"+"\n".join(re.sub(r"\s+"," ",l).strip() for l in t.splitlines() if l.strip()))
        print(tool,ts,len(t),flush=True)
    b.close()
