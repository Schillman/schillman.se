# schillman.se

The hub site at [schillman.se](https://schillman.se). Static files, no build step. Deployed on Netlify.

The Diablo IV Season 14 Farming Ledger at `d4.schillman.se` is a separate repo, [Schillman/farming-ledger](https://github.com/Schillman/farming-ledger).

## Shape of the site

The root is a game selector. Everything about one game lives in that game's own
directory, and site wide pages stay at the root.

```
/                              the hub, a game selector
/d4/                           Diablo IV section overview
/d4/guides.html                Diablo IV guide index
/d4/<slug>.html                the guides
/d4/ledger.html                reserved, not built yet, see below
/about.html /contact.html /privacy.html    site wide
```

Adding a second game is a directory, one more `.monument` block on the hub, and
its pages in the sitemap. It needs no new CSS: `site.css` has no Diablo specific
rule in it. There is deliberately no numbered register of games under the
monument: a one row list with an `01` in the margin is the launcher grid wearing
a different shape, and it made the page count itself.

`/d4/ledger.html` is a reserved slot. The Farming Ledger still lives at
`d4.schillman.se` and every "Ledger" nav item points there. When the ledger moves
onto this domain, that one href changes per page and its redirect goes in
`_redirects`. The nav item is deliberately a live external link rather than a
disabled placeholder, so it is never a dead end for a real visitor.

## Files

| File | What it is |
|---|---|
| `index.html` | The hub. The site's thesis, the Diablo IV monument, the register of what has a section and what earns one, and the editorial rules. |
| `d4/index.html` | Diablo IV section overview. The season in short, the three guides, the ledger, and how the ledger is built. |
| `d4/guides.html` | The guide index for Diablo IV. A new guide gets added here and on `d4/index.html`. |
| `site.css` | Shared stylesheet, the single source of truth for the design tokens, and the whole motion system. The ledger keeps its own inline copy on purpose, because it has to work as one file saved to disk. |
| `site.js` | Twenty lines of IntersectionObserver that add `.is-in` to `.reveal` sections. Everything else about the motion is CSS. |
| `d4/season-14-death-awakening.html` | Guide: Pandemonium Ruptures, Realmwalkers, Deathtoll Chambers, the Corrupted Reaper, Glints of Hope, Pandemonium Fragments. |
| `d4/helltides.html` | Guide: Aberrant Cinders and their expiry, Tortured Gift prices, the Threat meter, and the Helltide War Plan nodes. |
| `d4/war-plans.html` | Guide: the War Plans board, the seven activity trees, and which nodes to take first. |
| `d4/escalations.html` | Guide: the Escalation chain and a full table of the Horadric Reserve affixes. |
| `about.html` | Who writes the site, why, and the editorial rules every page is held to. Carries the sourcing policy in public. |
| `contact.html` | How to reach me, what makes a correction actionable, and rights holder contact. |
| `privacy.html` | Privacy and cookie policy covering this domain and its subdomains. Required by the AdSense terms. |
| `_redirects` | 301s from every pre-hub URL to its new home under `/d4/`. Not optional, see below. |
| `netlify.toml` | Turns Netlify's Pretty URLs post processing off, so there is one URL form per page. Leave it off. |
| `ads.txt` | AdSense authorized seller record. Lives on the root domain and covers the subdomains too. |
| `robots.txt`, `sitemap.xml` | Crawl hints. Add every new page to the sitemap and bump its `lastmod`. |
| `PRODUCT.md` | Durable product truth. Written by the redesign pass without an interview, so every fact in it is marked as inferred rather than confirmed. |
| `DESIGN.md` | The design system as built: tokens, components, motion, and the rules a new page has to keep. |
| `.github/workflows/publish-queue.yml` | Releases one queued page every `INTERVAL_DAYS` (currently 2). See below. |

## Redirects

Every Diablo IV page moved when the site became a hub, and those URLs are in a
sitemap Google has already crawled while the domain is under manual review. All
of them 301 from `_redirects`. Do not remove those rules, and add one any time a
page moves again. The extensionless convenience rules (`/d4/war-plans`) exist for
people typing or linking without the extension; nothing on the site links that
form and no canonical uses it.

## Motion

The motion system is all in `site.css`, in four layers: drifting embers, a staged
load sequence per page, scroll reveals, and hover and focus choreography. Cross
document transitions are the two line `@view-transition` declaration, no
JavaScript.

`.reveal` starts hidden and only `site.js` unhides it, so two guards keep that
from ever costing a reader content. `onerror` on each `<script src="/site.js">`
strips the `.js` class if the file fails to load, and an `@media print` block
pins every reveal visible, because print has no scrolling and no observer.
Both were mutation tested: without the `onerror` guard a missing `site.js`
leaves every section permanently invisible, and without the print block a
printed guide loses 89 percent of its text (5602 text drawing operators in the
PDF with it, 618 without).

`prefers-reduced-motion: reduce` switches all of it off wholesale, at the bottom
of `site.css`. That is a floor, not a dial: the ember field is removed from the
document, every animation and transition collapses, reveals render in their final
state, and view transitions stop animating. It was verified in a headless browser
under `--force-prefers-reduced-motion` and mutation tested by deleting the reduce
block and confirming the assertions go red. Motion you add goes into that block
in the same commit.

## Publishing a new guide

Guides get written in batches and published spread out, because bulk publishing
is a scaled content abuse signal on its own. The `queue` branch is a linear
extension of `main` holding one commit per unpublished page.

- Diablo IV pages go in `d4/`, and a queued commit contains the page **and** its
  entries in `d4/guides.html`, `d4/index.html`, `sitemap.xml` and this README, so
  every commit is a valid site. Never add a link to a page that a later commit
  introduces: `check.py` fails on it, and until that commit lands it is a 404 for
  real visitors.
- A queued page written before the hub split needs its canonical, its nav and
  its internal links moved to the `/d4/` form before it goes out. It needs a
  `_redirects` rule only if its old root URL was ever live. `helltides.html`
  was: it published on 13 August 2026, before the split, so it has one.
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

There is no build step and no test framework. Run `python3 check.py .` before pushing. It walks every directory, not just the root, and verifies that every `class` token resolves to a selector in `site.css`, every internal link resolves to a file that exists whether it is written absolute or relative, there are no em dashes, curly quotes or unescaped `&`, tags are balanced, every colour token pair in use clears its WCAG threshold (ratios printed, not eyeballed), and no custom property is declared without being referenced. Pages are reported by path, not basename, because `d4/guides.html` and a future `d4x/guides.html` are different files.

It was validated by mutation: each check was confirmed to fail on a deliberately broken copy of the site, not just to pass on the current one. The subdirectory walk and the relative link resolution were validated the same way, by confirming the previous version of `check.py` stays green on a mutation the current one catches. If you add a check, do the same, otherwise you cannot tell it from a check that never fires.

Any new colour pair goes into the `PAIRS` list in `check.py`, including a pair made of two colours that were already declared. That is what `--bloom` is for: the ember wash behind the hero and the monument is a real token rather than an inline `rgba()` stop, precisely so the text sitting over it gets computed instead of assumed.
