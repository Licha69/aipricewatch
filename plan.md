# AI Price Watch — Launch Plan (draft, 2026-10-16)
Owner: Licha (Montreal, solo). Goal: dated, sourced price/plan changes for AI coding & agent tools + weekly newsletter. EN first, FR later (use /en/ and /fr/ paths from day one).

## Names (RDAP checked 2026-10-16, not bought)
- aipricewatch.com — taken
- aipricewatch.ca — looks free (CIRA RDAP 404)
- aipricewatch.io — looks free (RDAP 404)
- codetoolprices.com — looks free (Verisign RDAP 404)
- aitoolprices.com, agentprices.com, pricedrift.ai — taken
Pick: aipricewatch.ca (Canadian, fits bilingual). Confirm at a registrar before buying.

## First 21 tools
See tools.csv (all pricing URLs return 200 except Replit 403 = bot block, page exists).

## Site structure
- /tools/<tool>: current plans, price-history table, dated changes with source + archive link
- /changes: feed of all changes, newest first (+ RSS)
- /alternatives/<tool>: cheaper/similar tools side by side
- /newsletter, /about (method, disclosure)

## $0 stack
- Astro static site on GitHub Pages or Cloudflare Pages
- GitHub Actions cron: daily fetch of pricing pages (Playwright for JS pages), save text snapshot, diff, open a PR for review
- Data as JSON/CSV in the repo; Wayback Machine as proof
- Newsletter: Buttondown or Kit free tier
Accounts needed: GitHub, Cloudflare (optional), newsletter tool. Domain (~$15/yr) is the only later cost.

## Affiliate/referral programs (verify terms before joining)
- Bolt: 15% of payments, up to $50/referral — https://support.bolt.new/account/referral-program
- Replit: $20 credits each (credits, not cash) — https://replit.com/refer
- Lovable affiliates — https://lovable.dev/affiliates (rate not checked)
Sponsors later, once the list has readers.

## 2-week checklist
Week 1
1. Pick name; claim GitHub repo
2. Write snapshot + diff script for 5 tools
3. Expand to 21; backfill history from Wayback
4. Build tool page + changes feed templates
5. Write 3 alternatives pages (Cursor, Copilot, Claude Code)
Week 2
6. Set up newsletter + signup form; disclosure page
7. Write issue #1 ("What changed this month")
8. Buy domain, deploy
9. Share on X, Reddit, Hacker News, dev Discords (follow rules)
10. Apply to affiliate programs; send issue #1; review weekly
