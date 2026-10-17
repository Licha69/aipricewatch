#!/usr/bin/env python3
"""Plain static site generator -> dist/. BASE env sets the URL prefix (default /aipricewatch)."""
import hashlib, csv, json, re, os, pathlib, html, shutil, datetime, email.utils
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
CSS="""*{box-sizing:border-box}body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;color:#1a2233;background:#f7f8fb;line-height:1.55}
.wrap{max-width:920px;margin:auto;padding:0 1rem}header{background:#fff;border-bottom:1px solid #e3e6ee}
.top{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.25rem 1rem;padding:.4rem 0}
.logo{display:inline-flex;align-items:center;gap:.5rem;font-weight:800;color:#1a2233;text-decoration:none;min-height:44px;font-size:1.1rem}
nav{display:flex;flex-wrap:wrap;gap:.25rem .75rem}nav a{display:inline-block;padding:.6rem .35rem;min-height:24px;color:#1d4ed8;text-decoration:none;font-weight:600}nav a:hover{text-decoration:underline}
a{color:#1d4ed8;word-break:break-word}h1,h2{line-height:1.2;color:#0f172a}h2{margin-top:2rem}
.hero{padding:2rem 0 1rem}.hero h1{font-size:clamp(1.8rem,5vw,2.6rem);margin:.2rem 0 .6rem}.hero p{font-size:1.1rem;color:#3b4557;max-width:40rem}
.beta{background:#fff7e0;border:1px solid #f2d27a;padding:.5rem .75rem;border-radius:8px;margin:.75rem 0;color:#3d2e00}
.tw{overflow-x:auto;background:#fff;border:1px solid #e3e6ee;border-radius:10px}table{border-collapse:collapse;width:100%}
td,th{padding:.55rem .7rem;text-align:left;vertical-align:top;border-bottom:1px solid #eceff5}th{background:#f1f4fa;font-size:.9rem;color:#334155}tr:last-child td{border-bottom:0}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:.6rem}.card{display:block;background:#fff;border:1px solid #e3e6ee;border-radius:10px;padding:.75rem;text-decoration:none;color:#1a2233}
.card:hover{border-color:#1d4ed8}.card b{display:block}.pill{display:inline-block;margin-top:.3rem;font-size:.8rem;padding:.1rem .5rem;border-radius:99px;background:#e7f6ec;color:#14532d}.pill.part{background:#fff1d6;color:#5c3b00}.pill.unk{background:#eceff5;color:#334155}
.muted{color:#4b5563}.box{background:#eef3ff;border:1px solid #cbd8ff;padding:1rem;border-radius:10px}
.bars{background:#fff;border:1px solid #e3e6ee;border-radius:10px;padding:1rem}.bar{margin:.6rem 0}.bar .lbl{display:flex;flex-wrap:wrap;justify-content:space-between;gap:.5rem;font-size:.95rem}
.track{height:12px;background:#eceff5;border-radius:99px;overflow:hidden;margin-top:.25rem}.fill{height:100%;border-radius:99px;background:#b91c1c}.fill.down{background:#15803d}
.up{color:#b91c1c;font-weight:700}.dn{color:#15803d;font-weight:700}ul.feed{padding-left:1.1rem}ul.feed li{margin:.5rem 0}
footer{margin-top:2.5rem;border-top:1px solid #e3e6ee;background:#fff}footer p{margin:0;padding:1rem 0}"""
LOGO='<svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true"><rect width="28" height="28" rx="7" fill="#1d4ed8"/><path d="M6 19l5-6 4 3 7-8" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="22" cy="8" r="2" fill="#fbbf24"/></svg>'
NAV=f'<nav aria-label="Main"><a href="/en/changes/">Changes</a><a href="/en/alternatives/">Alternatives</a><a href="/en/newsletter/">Newsletter</a><a href="/en/about/">About</a></nav>'
def fix(s): return s.replace('href="/','href="'+B+'/')
def page(path,title,body,lang="en",hero=False):
    p=D/path; p.parent.mkdir(parents=True,exist_ok=True)
    desc="Every AI coding tool price change, dated and sourced. Tracking "+str(len(tools))+" tools: Cursor, Copilot, Claude, ChatGPT, Windsurf and more."
    url=SITE+"/"+path.replace("index.html","")
    og=f'<meta name="description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:site_name" content="AI Price Watch"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.svg" type="image/svg+xml">'
    p.write_text(fix(f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)}</title>{og}<link rel="alternate" type="application/rss+xml" title="AI Price Watch" href="/rss.xml"><style>{CSS}</style></head><body><header><div class="wrap top"><a class="logo" href="/en/">{LOGO}<span>AI Price Watch</span></a>{NAV}</div></header><div class="wrap"><p class="beta"><b>Beta:</b> prices may lag behind official pages. Always check the official pricing page before buying.</p><main>{"" if hero else "<h1>"+e(title)+"</h1>"}{body}</main></div><footer><div class="wrap"><p class="muted">Prices come from official pricing pages and Wayback Machine captures. No affiliate links on this site yet. <a href="/en/about/">About &amp; method</a> · <a href="/rss.xml">RSS</a></p></div></footer></body></html>'))
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
cards="".join(f'<a class="card" href="/en/tools/{t["slug"]}/"><b>{e(t["tool"])}</b><br><span class="pill {dict(zip(["plans verified","partly verified","plans unknown"],["","part","unk"]))[badge(t["slug"])]}">{badge(t["slug"])}</span></a>' for t in tools)
recent="".join(f'<li>{x["date"]}: {hrow(x,True)}</li>' for x in hist[:8]) or "<li>No changes recorded yet.</li>"
big=sorted([x for x in hist if "from" in x],key=lambda x:-abs(x["to"]-x["from"])/x["from"])[:6]
mx=max([abs(x["to"]-x["from"])/x["from"] for x in big] or [1])
bars="".join(f'<div class="bar"><div class="lbl"><span><a href="/en/tools/{x["tool"]}/">{e(name[x["tool"]])}</a> {e(x["plan"])} <span class="muted">({x["date"]})</span></span><span class="{"up" if x["to"]>x["from"] else "dn"}">${x["from"]:g} → ${x["to"]:g} ({(x["to"]-x["from"])/x["from"]*100:+.0f}%)</span></div><div class="track" role="img" aria-label="{(x["to"]-x["from"])/x["from"]*100:+.0f} percent"><div class="fill{"" if x["to"]>x["from"] else " down"}" style="width:{abs(x["to"]-x["from"])/x["from"]/mx*100:.0f}%"></div></div></div>' for x in big)
page("en/index.html","AI Price Watch",f'<section class="hero"><h1>Every AI coding tool price change, dated and sourced</h1><p>We track the pricing pages of {len(tools)} AI coding and agent tools every day and log each real change with a link to the official page or a Wayback Machine capture.</p><p class="muted">Last automatic check: {last["date"]} · <a href="/en/changes/">All changes</a> · <a href="/rss.xml">RSS</a></p></section><h2>Biggest recent price changes</h2><div class="bars">{bars}<p class="muted" style="margin:.5rem 0 0">Same plan, before vs after. Red = pricier, green = cheaper. Monthly USD as shown on the page.</p></div><h2>Latest changes</h2><ul class="feed">{recent}</ul><h2>Tools tracked ({len(tools)})</h2><div class="cards">{cards}</div><h2>Newsletter</h2><div class="box"><b>Weekly email:</b> coming soon. Until then, follow the <a href="/rss.xml">RSS feed</a>.</div>',hero=True)
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
items="".join(f'<item><title>{e(name[x["tool"]])} pricing change ({x["date"]})</title><link>{SITE}/en/tools/{x["tool"]}/</link><guid isPermaLink="false">aipricewatch:{x["date"]}:{x["tool"]}:{hashlib.sha1(x["change"].encode()).hexdigest()[:8]}</guid><pubDate>{rfc(x["date"])}</pubDate><description>{e(x["change"])}</description></item>' for x in hist)
now=email.utils.format_datetime(datetime.datetime.now(datetime.timezone.utc))
(D/"rss.xml").write_text(f'<?xml version="1.0" encoding="utf-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>AI Price Watch</title><link>{SITE}/en/</link><atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/><description>Dated price changes of AI coding and agent tools</description><language>en</language><lastBuildDate>{now}</lastBuildDate>{items}</channel></rss>')
(D/".nojekyll").write_text("")
(D/"favicon.svg").write_text(LOGO.replace(' aria-hidden="true"',' xmlns="http://www.w3.org/2000/svg"'))
og=R/"assets/og.png"
if og.exists(): shutil.copy(og,D/"og.png")
print("built",len(list(D.rglob("*.html"))),"pages,",len(hist),"history items")
