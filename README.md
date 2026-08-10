# schillman.se

The hub site at [schillman.se](https://schillman.se). Static files, no build step. Deployed on Netlify.

The Diablo IV Season 14 Farming Ledger at `d4.schillman.se` is a separate repo, [Schillman/farming-ledger](https://github.com/Schillman/farming-ledger).

## Files

| File | What it is |
|---|---|
| `index.html` | The homepage. Links the ledger and indexes the guides. |
| `site.css` | Shared stylesheet and the single source of truth for the design tokens. The ledger keeps its own inline copy on purpose, because it has to work as one file saved to disk. |
| `season-14-death-awakening.html` | Guide: Pandemonium Ruptures, Realmwalkers, Deathtoll Chambers, the Corrupted Reaper, Glints of Hope, Pandemonium Fragments. |
| `war-plans.html` | Guide: the War Plans board, the seven activity trees, and which nodes to take first. |
| `escalations.html` | Guide: the Escalation chain and a full table of the Horadric Reserve affixes. |
| `privacy.html` | Privacy and cookie policy covering this domain and its subdomains. Required by the AdSense terms. |
| `ads.txt` | AdSense authorized seller record. Must live on the root domain even though the ads run on the subdomain. |
| `robots.txt`, `sitemap.xml` | Crawl hints. Add every new page to the sitemap and bump its `lastmod`. |

## Rules that are not obvious from the code

- **No ad code anywhere on this domain.** The homepage is a hub, and AdSense rejects ads on navigation pages with little content. Ads run only on `d4.schillman.se`. This was the reason for the first policy strike, and `privacy.html` now states in writing that schillman.se carries no advertising, so adding any means editing that page too.
- Keep `privacy.html` accurate. If analytics or another ad provider is ever added, update that page and the date at the top of it in the same commit.
- **Every game mechanic, boss, node or currency named in a guide gets verified against a current source before it ships**, and each guide lists the sources it was checked against. Where a detail cannot be confirmed, say so on the page instead of smoothing it over. Community guides copy each other's typos: "Writhe and Rot" was wrong in the ledger for exactly that reason.
- No em dashes and no curly quotes in copy, matching the ledger.
- One accent color (ember `#ff5a36`). Any new text color gets its WCAG contrast checked against its real background, 4.5:1 for normal text and 3:1 for a boundary that is the only affordance on an interactive control.

## Checking a change

There is no build step and no test framework. Run `python3 check.py .` before pushing. It verifies that every `class` token resolves to a selector in `site.css`, every internal link resolves to a file that exists, there are no em dashes, curly quotes or unescaped `&`, tags are balanced, every colour token pair in use clears its WCAG threshold (ratios printed, not eyeballed), and no custom property is declared without being referenced.

It was validated by mutation: each of those seven checks was confirmed to fail on a deliberately broken copy of the site, not just to pass on the current one. If you add a check, do the same, otherwise you cannot tell it from a check that never fires.
