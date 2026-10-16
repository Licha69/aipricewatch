#!/usr/bin/env python3
"""Plain static site generator -> dist/. BASE env sets the URL prefix (default /aipricewatch)."""
import csv, json, re, os, pathlib, html, shutil, datetime, email.utils
R=pathlib.Path(__file__).resolve().parent.parent; D=R/"dist"
B=os.environ.get("BASE","/aipricewatch"); SITE=os.environ.get("SITE","https://licha69.github.io")+B
e=html.escape
def slug(n): return re.sub(r"[^a-z0-9]+","-",n.lower()).strip("-")
tools=[dict(r,slug=slug(r["tool"])) for r in csv.DictReader(open(R/"tools.csv"))]
name={t["slug"]:t["tool"] for t in tools}
prices=json.load(open(R/"data/prices.json")); status_over=prices.get("_status",{})
hist=sorted(json.load(open(R/"data/history.json")),key=lambda x:(x["date"],x["tool"]),reverse=True)
# only reviewed auto-flagged changes are public
changes=[c for c in (json.load(open(p)) for p in (R/"data/changes").glob("*.json")) if c.get("reviewed") is True]
last=json.load(open(R/"data/last_run.json")) if (R/"data/last_run.json").exists() else {"date":"never","results":[]}
UNSURE=re.compile(r"unknown|unverified|not checked|confirm",re.I)
def badge(s):
    rows=[r for r in prices.get(s,[]) if r[0]!="note"]
    if not rows or all(UNSURE.search(b) for a,b in rows): return "plans unknown"
    if status_over.get(s)=="partial" or any(UNSURE.search(a+" "+b) for a,b in prices.get(s,[])): return "partly verified"
    return "plans verified"
CSS="""body{font-family:system-ui,sans-serif;max-width:860px;margin:auto;padding:1rem;color:#222;line-height:1.5}
nav{display:flex;flex-wrap:wrap;gap:.25rem 1rem}nav a{display:inline-block;padding:.5rem .25rem;min-height:24px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:.4rem;text-align:left;vertical-align:top}
.cards{display:flex;flex-wrap:wrap;gap:.5rem}.card{display:block;border:1px solid #ddd;border-radius:8px;padding:.6rem;width:170px;max-width:100%}
.muted{color:#595959}.box{background:#f4f6ff;padding:1rem;border-radius:8px}.beta{background:#fff4d6;padding:.5rem;border-radius:6px}
a{word-break:break-word}"""
NAV=f'<nav aria-label="Main"><a href="/en/">AI Price Watch</a><a href="/en/changes/">Changes</a><a href="/en/alternatives/">Alternatives</a><a href="/en/newsletter/">Newsletter</a><a href="/en/about/">About</a></nav>'
def fix(s): return s.replace('href="/','href="'+B+'/')
def page(path,title,body,lang="en"):
    p=D/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(fix(f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)}</title><link rel="alternate" type="application/rss+xml" title="AI Price Watch" href="/rss.xml"><style>{CSS}</style></head><body><header>{NAV}<p class="beta"><b>Beta:</b> prices may lag behind official pages. Always check the official pricing page before buying.</p></header><main><h1>{e(title)}</h1>{body}</main><footer><hr><p class="muted">Prices come from official pricing pages and Wayback Machine captures. No affiliate links on this site yet. <a href="/en/about/">About &amp; method</a></p></footer></body></html>'))
def tbl(head,rows): return '<div class="tw"><table><tr>'+"".join(f"<th>{h}</th>" for h in head)+"</tr>"+"".join("<tr>"+"".join(f"<td>{c}</td>" for c in r)+"</tr>" for r in rows)+"</table></div>"
def ptable(s):
    rows=prices.get(s)
    if not rows: return '<p class="muted">Current plans: unknown (not yet verified).</p>'
    return tbl(["Plan","Price"],[(e(a),e(b)) for a,b in rows])
def src(u): return f'<a href="{e(u)}">{e("Wayback capture" if "web.archive.org" in u else ("repo snapshot (no archive capture)" if "github.com/Licha69" in u else "official page"))}</a>' if u.startswith("http") else e(u)
def hrow(x,with_tool=False):
    t=f'<a href="/en/tools/{x["tool"]}/">{e(name[x["tool"]])}</a>: ' if with_tool else ""
    return f'{t}{e(x["change"])} <span class="muted">(seen between {x["previous_capture"]} and {x["date"]})</span> Source: {src(x["source"])} · previous capture: {src(x["previous_source"])}'
if D.exists(): shutil.rmtree(D)
cards="".join(f'<a class="card" href="/en/tools/{t["slug"]}/"><b>{e(t["tool"])}</b><br><span class="muted">{badge(t["slug"])}</span></a>' for t in tools)
recent="".join(f'<li>{x["date"]}: {hrow(x,True)}</li>' for x in hist[:8]) or "<li>No changes recorded yet.</li>"
page("en/index.html","AI Price Watch",f'<p>Dated price and plan changes for AI coding and agent tools. Last automatic check: {last["date"]}.</p><div class="box"><b>Weekly newsletter</b>: <a href="/en/newsletter/">coming soon</a></div><h2>Latest changes</h2><ul>{recent}</ul><h2>Tools tracked ({len(tools)})</h2><div class="cards">{cards}</div>')
for t in tools:
    s=t["slug"]; hh=[x for x in hist if x["tool"]==s]; cc=[c for c in changes if c["tool"]==s]
    rows=[(x["date"],hrow(x)) for x in hh]+[(c["date"],e("; ".join(c["price_lines"][:5]))) for c in cc]
    h=tbl(["Date","Change"],rows) if rows else '<p class="muted">No changes recorded yet.</p>'
    page(f"en/tools/{s}/index.html",f"{t['tool']} pricing",f'<p>Official page: <a href="{e(t["pricing_url"])}">{e(t["pricing_url"])}</a><br><span class="muted">Status: {badge(s)}</span></p><h2>Current plans</h2>{ptable(s)}<h2>Price history</h2>{h}')
page("en/changes/index.html","Changes feed",'<p><a href="/rss.xml">RSS feed</a></p><ul>'+("".join(f'<li>{x["date"]}: {hrow(x,True)}</li>' for x in hist) or "<li>No changes recorded yet.</li>")+"</ul>")
alts={"cursor":["github-copilot","windsurf","zed","claude-claude-code"],"github-copilot":["cursor","amazon-q-developer","gemini-code-assist","tabnine"],"claude-claude-code":["chatgpt-codex","factory","warp","sourcegraph-amp"]}
for a,lst in alts.items():
    page(f"en/alternatives/{a}/index.html",f"{name[a]} alternatives","".join(f'<h2><a href="/en/tools/{x}/">{e(name[x])}</a></h2>{ptable(x)}' for x in [a]+lst))
page("en/alternatives/index.html","Alternatives","<ul>"+"".join(f'<li><a href="/en/alternatives/{a}/">{e(name[a])} alternatives</a></li>' for a in alts)+"</ul>")
page("en/newsletter/index.html","Weekly newsletter",'<p>One short email a week: what changed in AI tool pricing.</p><p><b>Signup is not open yet.</b> Until then, follow the <a href="/rss.xml">RSS feed</a>.</p>')
page("en/about/index.html","About & method","<p>AI Price Watch is run by Licha in Montreal. A script saves the text of each official pricing page every day and flags differences. Flagged differences are not published automatically: an entry appears in the price history only after it has been checked against the official page or a Wayback Machine capture, and each entry links its source. Prices the site could not confirm are marked unknown or partly verified.</p><h2>Affiliate disclosure</h2><p>There are no affiliate or referral links on this site right now. If we add any, each one will be labelled right next to the link.</p>")
page("fr/index.html","AI Price Watch (FR)","<p>Version française à venir.</p>","fr")
(D/"index.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>AI Price Watch</title><link rel="canonical" href="{SITE}/en/"><meta http-equiv="refresh" content="0;url={B}/en/"></head><body><p><a href="{B}/en/">Go to AI Price Watch</a></p></body></html>')
def rfc(d): return email.utils.format_datetime(datetime.datetime.fromisoformat(d).replace(hour=12,tzinfo=datetime.timezone.utc))
items="".join(f'<item><title>{e(name[x["tool"]])} pricing change ({x["date"]})</title><link>{SITE}/en/tools/{x["tool"]}/</link><guid isPermaLink="false">aipricewatch:{x["date"]}:{x["tool"]}</guid><pubDate>{rfc(x["date"])}</pubDate><description>{e(x["change"])}</description></item>' for x in hist)
now=email.utils.format_datetime(datetime.datetime.now(datetime.timezone.utc))
(D/"rss.xml").write_text(f'<?xml version="1.0" encoding="utf-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>AI Price Watch</title><link>{SITE}/en/</link><atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/><description>Dated price changes of AI coding and agent tools</description><language>en</language><lastBuildDate>{now}</lastBuildDate>{items}</channel></rss>')
(D/".nojekyll").write_text("")
print("built",len(list(D.rglob("*.html"))),"pages,",len(hist),"history items")
