# r/webdev (draft, not posted)

Post only on a **Saturday** with the **Showoff Saturday** flair. Keep it about the build: the sub bans commercial promotion and removes newsletter-style promo, so don't mention the newsletter. Reddit's 9:1 guideline also applies.

**Title:** [Showoff Saturday] A static site that tracks AI tool pricing pages with Python + GitHub Actions + Wayback CDX

**Body:**
I built a small tracker that logs dated price changes for 21 AI coding tools: https://licha69.github.io/aipricewatch/

How it's built:
- **Snapshots:** a Python script fetches each pricing page with urllib. It falls back to headless Chromium (Playwright) for pages that render prices in JS or block plain requests. It pulls the visible text and diffs it against the last snapshot.
- **No auto-publishing:** diffs are saved as JSON with `reviewed: false` and stay off the site until I check them.
- **History:** I used the Wayback Machine CDX API to list captures since 2024, then rendered them in Chromium. archive.org rate-limits hard (lots of 500s), so it runs slowly, one capture at a time.
- **Site:** a ~90-line Python generator that writes plain HTML. No JS framework, inline SVG logo, CSS bar chart, RSS with stable guids.
- **CI:** a daily GitHub Actions job snapshots, rebuilds, commits data to main and deploys gh-pages.

Lessons: some sites serve a Cloudflare bot check to datacenter IPs. Prices change with the visitor's location (I saw CAD from Canada). Pricing pages often hide numbers behind toggles. Repo: https://github.com/Licha69/aipricewatch. Feedback on the scraping approach is welcome.
