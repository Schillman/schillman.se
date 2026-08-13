# schillman.se

The hub site at [schillman.se](https://schillman.se). Static files, no build step. Deployed on Netlify.

The Diablo IV Season 14 Farming Ledger at `d4.schillman.se` is a separate repo, [Schillman/farming-ledger](https://github.com/Schillman/farming-ledger).

## Files

| File | What it is |
|---|---|
| `index.html` | The homepage. Links the ledger and indexes the guides. |
| `guides.html` | The guide index, and the nav target on every page. A new guide gets added here and on the homepage. |
| `site.css` | Shared stylesheet and the single source of truth for the design tokens. The ledger keeps its own inline copy on purpose, because it has to work as one file saved to disk. |
| `season-14-death-awakening.html` | Guide: Pandemonium Ruptures, Realmwalkers, Deathtoll Chambers, the Corrupted Reaper, Glints of Hope, Pandemonium Fragments. |
| `war-plans.html` | Guide: the War Plans board, the seven activity trees, and which nodes to take first. |
| `escalations.html` | Guide: the Escalation chain and a full table of the Horadric Reserve affixes. |
| `about.html` | Who writes the site, why, and the editorial rules every page is held to. Carries the sourcing policy in public. |
| `contact.html` | How to reach me, what makes a correction actionable, and rights holder contact. |
| `privacy.html` | Privacy and cookie policy covering this domain and its subdomains. Required by the AdSense terms. |
| `ads.txt` | AdSense authorized seller record. Lives on the root domain and covers the subdomains too. |
| `robots.txt`, `sitemap.xml` | Crawl hints. Add every new page to the sitemap and bump its `lastmod`. |
| `.github/workflows/publish-queue.yml` | Releases one queued page every `INTERVAL_DAYS` (currently 2). See below. |

## Publishing a new guide

Guides get written in batches and published spread out, because bulk publishing
is a scaled content abuse signal on its own. The `queue` branch is a linear
extension of `main` holding one commit per unpublished page.

- A queued commit contains the page **and** its entries in `guides.html`,
  `index.html`, `sitemap.xml` and this README, so every commit is a valid site.
  Never add a link to a page that a later commit introduces: `check.py` fails on
  it, and until that commit lands it is a 404 for real visitors.
- Commit subjects on both branches start with `publish:`. The workflow measures
  the interval from the last such commit on `main`, so ordinary fixes pushed to
  `main` do not reset the clock.
- Order in `queue` is publish order. To change the interval, edit
  `INTERVAL_DAYS` in the workflow. To release the next page immediately, run the
  workflow manually with `force` checked.
- If you commit to `main` directly, rebase `queue` onto it, otherwise the
  fast forward is refused and the job fails loudly rather than publishing early.

## Rules that are not obvious from the code

- **`schillman.se` is the only site in AdSense, and it is what gets judged.** `d4.schillman.se` is not listed as a site at all; a subdomain inherits the root domain's approval, so the root is the only property that matters. Status on 12 August 2026: `Needs attention`, `Low value content`, ads.txt `Authorised`.
- **The rejection was about this domain being thin, nothing else.** At review time it was two days old, 5 pages, roughly 4,000 words, and carried no ad code at all because an earlier rule here forbade it. Moving ad code to the subdomain after the first strike was beside the point: the reviewer was never looking at the subdomain. Ad code now sits on every page of this domain, which is both the property under review and where AdSense expects to find it.
- **Content volume is the gate, not markup.** Google is judging whether this domain is a real site. That means substantive pages, an `about.html` and a `contact.html` that name a real person and a real route to them, and a publishing history rather than a single dump. New guides go up spread out over time, not ten in an afternoon, because bulk publishing is itself a scaled content abuse signal.
- Keep `privacy.html` accurate. It now states that ads run across the domain and its subdomains. If analytics or another ad provider is ever added, update that page and the date at the top of it in the same commit.
- **Every game mechanic, boss, node or currency named in a guide gets verified against a current source before it ships**, and each guide lists the sources it was checked against. Where a detail cannot be confirmed, say so on the page instead of smoothing it over. Community guides copy each other's typos: "Writhe and Rot" was wrong in the ledger for exactly that reason.
- No em dashes and no curly quotes in copy, matching the ledger.
- One accent color (ember `#ff5a36`). Any new text color gets its WCAG contrast checked against its real background, 4.5:1 for normal text and 3:1 for a boundary that is the only affordance on an interactive control.

## Checking a change

There is no build step and no test framework. Run `python3 check.py .` before pushing. It verifies that every `class` token resolves to a selector in `site.css`, every internal link resolves to a file that exists, there are no em dashes, curly quotes or unescaped `&`, tags are balanced, every colour token pair in use clears its WCAG threshold (ratios printed, not eyeballed), and no custom property is declared without being referenced.

It was validated by mutation: each of those seven checks was confirmed to fail on a deliberately broken copy of the site, not just to pass on the current one. If you add a check, do the same, otherwise you cannot tell it from a check that never fires.
