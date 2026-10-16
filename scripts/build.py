#!/usr/bin/env python3
"""Plain static site generator -> dist/"""
import csv, json, re, pathlib, html, shutil, datetime
R=pathlib.Path(__file__).resolve().parent.parent; D=R/"dist"
import os
B=os.environ.get("BASE","/aipricewatch")
def verified(s): return any("unknown" not in b.lower() for a,b in prices.get(s,[]))
def slug(n): return re.sub(r"[^a-z0-9]+","-",n.lower()).strip("-")
e=html.escape
tools=[dict(r,slug=slug(r["tool"])) for r in csv.DictReader(open(R/"tools.csv"))]
prices=json.load(open(R/"data/prices.json"))
changes=sorted([json.load(open(p)) for p in (R/"data/changes").glob("*.json")],key=lambda c:c["date"],reverse=True)
CSS="body{font-family:system-ui,sans-serif;max-width:860px;margin:auto;padding:1rem;color:#222}nav a{margin-right:1rem}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:.4rem;text-align:left}.card{display:inline-block;border:1px solid #ddd;border-radius:8px;padding:.6rem;margin:.3rem;width:170px}.muted{color:#777}.box{background:#f4f6ff;padding:1rem;border-radius:8px}"
def page(path,title,body,lang="en"):
    p=D/path; p.parent.mkdir(parents=True,exist_ok=True)
    nav='<nav><a href="/en/">AI Price Watch</a><a href="/en/changes/">Changes</a><a href="/en/alternatives/">Alternatives</a><a href="/en/newsletter/">Newsletter</a><a href="/en/about/">About</a><a href="/fr/">FR</a></nav>'
    p.write_text((f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{e(title)}</title><link rel="alternate" type="application/rss+xml" href="/rss.xml"><style>{CSS}</style></head><body>{nav}<p style="background:#fff4d6;padding:.5rem;border-radius:6px"><b>Beta:</b> prices may lag behind official pages. Always check the official pricing page before buying.</p><h1>{e(title)}</h1>{body}<hr><p class="muted">Prices checked from official pages. Some links may be affiliate links. <a href="/en/about/">Disclosure</a></p></body></html>').replace('href="/','href="'+B+'/'))
def ptable(s):
    rows=prices.get(s)
    if not rows: return '<p class="muted">Current plans: unknown (not yet verified).</p>'
    return "<table><tr><th>Plan</th><th>Price</th></tr>"+"".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a,b in rows)+"</table>"
if D.exists(): shutil.rmtree(D)
last=json.load(open(R/"data/last_run.json")) if (R/"data/last_run.json").exists() else {"date":"never","results":[]}
stat={r["tool"]:r["status"] for r in last["results"]}
cards="".join(f'<a class="card" href="/en/tools/{t["slug"]}/"><b>{e(t["tool"])}</b><br><span class="muted">{"plans verified" if verified(t["slug"]) else "plans unknown"}</span></a>' for t in tools)
recent="".join(f'<li>{c["date"]} — <a href="/en/tools/{c["tool"]}/">{c["tool"]}</a>: {len(c["price_lines"])} price lines changed</li>' for c in changes[:10]) or "<li>No changes yet — first snapshots taken "+last["date"]+".</li>"
page("en/index.html","AI Price Watch",f'<p>Dated price and plan changes for AI coding and agent tools. Last check: {last["date"]}.</p><div class="box"><b>Weekly newsletter</b> — <a href="/en/newsletter/">sign up (coming soon)</a></div><h2>Latest changes</h2><ul>{recent}</ul><h2>Tools tracked ({len(tools)})</h2>{cards}')
for t in tools:
    s=t["slug"]; hist=[c for c in changes if c["tool"]==s]
    snaps=sorted(p.stem for p in (R/"data/snapshots"/s).glob("*.txt")) if (R/"data/snapshots"/s).exists() else []
    h="".join(f"<tr><td>{c['date']}</td><td>{e('; '.join(c['price_lines'][:5]))}</td></tr>" for c in hist) or '<tr><td colspan=2 class="muted">No changes recorded yet.</td></tr>'
    page(f"en/tools/{s}/index.html",f"{t['tool']} pricing",f'<p>Official page: <a href="{e(t["pricing_url"])}">{e(t["pricing_url"])}</a><br>Last snapshot status: {stat.get(s,"none")} · snapshots: {", ".join(snaps) or "none"}</p><h2>Current plans</h2>{ptable(s)}<h2>Price history</h2><table><tr><th>Date</th><th>Change</th></tr>{h}</table>')
ch="".join(f'<li>{c["date"]} <a href="/en/tools/{c["tool"]}/">{c["tool"]}</a><ul>'+"".join(f"<li><code>{e(l)}</code></li>" for l in c["price_lines"][:10])+"</ul></li>" for c in changes) or "<li>No changes recorded yet.</li>"
page("en/changes/index.html","Changes feed",f'<p><a href="/rss.xml">RSS</a></p><ul>{ch}</ul>')
alts={"cursor":["github-copilot","windsurf","zed","claude-claude-code"],"github-copilot":["cursor","amazon-q-developer","gemini-code-assist","tabnine"],"claude-claude-code":["chatgpt-codex","factory","warp","sourcegraph-amp"]}
name={t["slug"]:t["tool"] for t in tools}
for a,lst in alts.items():
    body="".join(f'<h2><a href="/en/tools/{x}/">{e(name[x])}</a></h2>{ptable(x)}' for x in [a]+lst)
    page(f"en/alternatives/{a}/index.html",f"{name[a]} alternatives",body)
page("en/alternatives/index.html","Alternatives","<ul>"+"".join(f'<li><a href="/en/alternatives/{a}/">{e(name[a])} alternatives</a></li>' for a in alts)+"</ul>")
page("en/newsletter/index.html","Weekly newsletter",'<p>One short email a week: what changed in AI tool pricing.</p><form onsubmit="alert(\'Coming soon\');return false"><input type="email" placeholder="you@example.com" required> <button>Subscribe</button></form><p class="muted">Placeholder — not connected to any provider yet.</p>')
page("en/about/index.html","About & disclosure","<p>AI Price Watch is run by Licha in Montreal. A script checks each official pricing page daily, and every change is reviewed by hand before it is published. Unverified prices are marked as unknown.</p><h2>Affiliate disclosure</h2><p>Some links may be affiliate or referral links (for example Bolt, Replit, Lovable). If you buy through them, we may earn a commission at no extra cost to you. This never changes what we report.</p>")
page("fr/index.html","AI Price Watch (FR)","<p>Version française à venir.</p>","fr")
(D/"index.html").write_text('<meta http-equiv="refresh" content="0;url='+B+'/en/">')
now=datetime.datetime.now(datetime.UTC).strftime("%a, %d %b %Y %H:%M:%S GMT")
items="".join(f'<item><title>{e(c["tool"])} pricing changed ({c["date"]})</title><link>https://aipricewatch.ca/en/tools/{c["tool"]}/</link><guid>{c["date"]}-{c["tool"]}</guid></item>' for c in changes[:50])
(D/"rss.xml").write_text(f'<?xml version="1.0"?><rss version="2.0"><channel><title>AI Price Watch</title><link>https://aipricewatch.ca/</link><description>AI tool price changes</description><lastBuildDate>{now}</lastBuildDate>{items}</channel></rss>')
print("built",len(list(D.rglob("*.html"))),"pages")
