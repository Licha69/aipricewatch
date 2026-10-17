# Show HN (draft, not posted)

**Title:** Show HN: AI Price Watch – dated, sourced price changes for 21 AI coding tools

**URL:** https://licha69.github.io/aipricewatch/

**First comment:**
I kept losing track of what Cursor, Copilot, Claude, Windsurf and the others actually cost, and when it changed. So I built a small site that saves each tool's official pricing page every day and keeps a price history. Every entry links to a Wayback Machine capture or the official page.

Some changes it has logged so far:
- Windsurf (ex-Codeium) Pro: $10/mo (Nov 2024) → $15 (Jan 2025) → $20 (Oct 2026)
- Replit Core: $15 → $20/mo (spring 2025)
- Claude Team cut its seat prices in Mar 2026: Standard $25 → $20/mo annual, Premium $150 → $100
- ChatGPT Pro was $200/mo in Sep 2025. Its pricing page now says "from $100" with 3 usage tiers
- Tabnine took its public prices down; the pricing page now redirects to a Tricentis contact form

How it works: a Python script fetches the pages (headless Chromium for the JS-heavy ones) and diffs the text. GitHub Actions runs it daily and rebuilds a plain static site on GitHub Pages. Flagged diffs aren't published until I check them against the source. Older history comes from Wayback CDX captures.

Limits: it's a beta, a few pages block bots, and some prices depend on your location (ChatGPT showed CAD from Canada). No affiliate links. Corrections are very welcome, with a link to the source if you have one.

Code: https://github.com/Licha69/aipricewatch
