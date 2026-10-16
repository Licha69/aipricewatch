#!/usr/bin/env python3
"""Fetch one archived capture per month since 2024 for given pricing URLs (unique content digests)."""
import json, urllib.request, sys, pathlib, re, time
from html.parser import HTMLParser
sys.path.insert(0,str(pathlib.Path(__file__).parent)); from snapshot import T
OUT=pathlib.Path(__file__).resolve().parent.parent/"data/wayback"
URLS={"cursor":["cursor.com/pricing","www.cursor.com/pricing"],"github-copilot":["github.com/features/copilot/plans"],
"claude-claude-code":["claude.ai/pricing","www.anthropic.com/pricing","claude.com/pricing"],"chatgpt-codex":["openai.com/chatgpt/pricing","chatgpt.com/pricing"],
"windsurf":["codeium.com/pricing","windsurf.com/pricing"],"replit":["replit.com/pricing"],"lovable":["lovable.dev/pricing"],"bolt-new":["bolt.new/pricing"]}
def get(u,t=60):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"AIPriceWatch research"}),timeout=t).read().decode("utf-8","ignore")
        except Exception as e: err=e; time.sleep(5)
    raise err
for tool,urls in URLS.items():
    d=OUT/tool; d.mkdir(parents=True,exist_ok=True)
    for u in urls:
        try: rows=json.loads(get(f"https://web.archive.org/cdx/search/cdx?url={u}&output=json&from=2024&filter=statuscode:200&collapse=timestamp:6&fl=timestamp,digest"))[1:]
        except Exception as e: print(tool,u,"cdx err",e); continue
        print(tool,u,len(rows),"months")
        for ts,dg in rows:
            f=d/f"{ts[:8]}_{u.replace('/','_')}.txt"
            if f.exists(): continue
            try: h=get(f"https://web.archive.org/web/{ts}id_/https://{u}")
            except Exception as e: print(" fail",ts,e); continue
            p=T(); p.feed(h); f.write_text(f"ARCHIVE https://web.archive.org/web/{ts}/https://{u}\n"+"\n".join(p.out))
            time.sleep(1)
