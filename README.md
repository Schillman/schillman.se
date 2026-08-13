# schillman.se

The hub site at [schillman.se](https://schillman.se). Static files, no build step. Deployed on Netlify.

The Diablo IV Season 14 Farming Ledger is a page of this site at `/d4/ledger.html`.
It is still developed in its own repo, [Schillman/farming-ledger](https://github.com/Schillman/farming-ledger),
because it is also a standalone single file tool; this copy is the deployed one.

## Shape of the site

The root is a game selector. Everything about one game lives in that game's own
directory, and site wide pages stay at the root.

```
/                              the hub, a game selector
/d4/                           Diablo IV section overview
/d4/guides.html                Diablo IV guide index
/d4/<slug>.html                the guides
/d4/ledger.html                the Season 14 Farming Ledger, see below
/about.html /contact.html /privacy.html    site wide
```

Adding a second game is a directory, one more `.monument` block on the hub, and
its pages in the sitemap. It needs no new CSS: `site.css` has no Diablo specific
rule in it. There is deliberately no numbered register of games under the
monument: a one row list with an `01` in the margin is the launcher grid wearing
a different shape, and it made the page count itself.

`/d4/ledger.html` is the one page on the site that does not use `site.css`, and
that is deliberate rather than an oversight. It is a single file tool people save
to disk and use with the network off while playing, so it carries its own inline
`<style>` and its own inline scripts, including an inline SVG sprite for its
icons. Those glyphs are Phosphor Icons 2.1.1, MIT licensed and lifted verbatim
from the `@phosphor-icons/web@2.1.1` package the page used to fetch from a CDN
at runtime, which meant that saved to disk with the network off every icon
rendered as nothing. Regular weight for the four interface icons, duotone for
the thirteen category icons, matching the classes the page used, so it looks
exactly as it did. The attribution comment beside the sprite is a licence
obligation, not a nicety. The category icons are data driven, so a symbol that
does not exist is a content bug `check.py` cannot see: after touching the sprite,
confirm every `icon` value in `DATA` still resolves to a `<symbol>`. Its site chrome (breadcrumb, section nav, footer) is therefore a copy of
the matching rules from `site.css` rather than a link to it, and every link in
that chrome is absolute so it still goes somewhere from a `file://` copy.

Keeping a copy honest is `check.py`'s job: class tokens resolve against
`site.css` **plus any inline `<style>` in the page being checked**, so the
ledger's own hundred classes are checked against its own stylesheet and a class
with no rule anywhere still fails. The page is not exempted from anything.

It also implements the receiving half of a progress handoff. The old page at
`d4.schillman.se` links here with `#import=<base64url of the {itemId: boolean}
map>`. That fragment is fully decoded and validated into a local object before a
single key is written, and it is cleared with `replaceState` first, so a
malformed link cannot half apply, cannot clear a season of progress, and cannot
re-import on reload. The merge is last write wins per item key, because the old
page offers "Send my progress again".

## Files

| File | What it is |
|---|---|
| `index.html` | The hub. The site's thesis, the Diablo IV monument, the register of what has a section and what earns one, and the editorial rules. |
| `d4/index.html` | Diablo IV section overview. The season in short, the guide list, the ledger, and how the ledger is built. |
| `d4/guides.html` | The guide index for Diablo IV. A new guide gets added here and on `d4/index.html`. |
| `d4/ledger.html` | The Season 14 Farming Ledger. The one page with its own inline styles and scripts, because it has to work as a single file saved to disk. See below before editing it. |
| `site.css` | Shared stylesheet, the single source of truth for the design tokens, and the whole motion system. The ledger keeps its own inline copy on purpose, because it has to work as one file saved to disk. |
| `site.js` | Twenty lines of IntersectionObserver that add `.is-in` to `.reveal` sections. Everything else about the motion is CSS. |
| `d4/season-14-death-awakening.html` | Guide: Pandemonium Ruptures, Realmwalkers, Deathtoll Chambers, the Corrupted Reaper, Glints of Hope, Pandemonium Fragments. |
| `d4/helltides.html` | Guide: Aberrant Cinders and their expiry, Tortured Gift prices, the Threat meter, and the Helltide War Plan nodes. |
| `d4/war-plans.html` | Guide: the War Plans board, the seven activity trees, and which nodes to take first. |
| `d4/escalations.html` | Guide: the Escalation chain and a full table of the Horadric Reserve affixes. |
| `d4/mythic-uniques.html` | Guide: Mythic Uniques 3.0, the four acquisition routes and their costs, the Crafted tag, Pandemonium Fragment sources. |
| `d4/leveling.html` | Guide: the Season 14 experience meta, the Hellwyrm method, and the Paragon curve to 300. |
| `d4/undercity.html` | Guide: the Undercity timer and Attunement, the full Tribute table, Bargains, and rune farming. |
| `d4/gems.html` | Guide: the gem cost ladder, per socket effects, fragment farming, and the Horadric tier. |
| `d4/obols.html` | Guide: Purveyor slot prices, the cheapest legal slot strategy, the obol cap, and income sources. |
| `d4/solo-self-found.html` | Guide: SSF restrictions and the separate economy, the Tower leaving beta, and leaderboard reward tiers. |
| `about.html` | Who writes the site, why, and the editorial rules every page is held to. Carries the sourcing policy in public. |
| `contact.html` | How to reach me, what makes a correction actionable, and rights holder contact. |
| `privacy.html` | Privacy and cookie policy covering this domain and its subdomains. Required by the AdSense terms. |
| `_redirects` | 301s from every pre-hub URL to its new home under `/d4/`. Not optional, see below. |
| `netlify.toml` | Turns Netlify's Pretty URLs post processing off, so there is one URL form per page. Leave it off. |
| `ads.txt` | AdSense authorized seller record. Lives on the root domain and covers the subdomains too. |
| `robots.txt`, `sitemap.xml` | Crawl hints. Add every new page to the sitemap and bump its `lastmod`. |
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

`.reveal` starts hidden and only `site.js` unhides it, so three guards keep that
from ever costing a reader content, one per way it can go wrong.

- **The file 404s.** `onerror` on each `<script src="/site.js">` strips the
  `.js` class, and the hidden start state goes with it.
- **The file serves 200 and does not parse.** `onerror` never fires for that,
  so `check.py` runs `node --check site.js` instead. This is the door the other
  two guards leave open.
- **Print, and PDF snapshots.** There is no scrolling and no observer, so an
  `@media print` block pins every reveal visible and kills the transition so a
  page cannot be captured mid fade.

All three are mutation tested. Without `onerror` a missing `site.js` leaves
every section permanently invisible; with a deliberate syntax error `check.py`
exits 1 on `SyntaxError`; without the print block a printed guide loses about 89
percent of its text (5602 text drawing operators in the PDF with it, 618
without).

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

There is no build step and no test framework. Run both of these before pushing:

```
python3 check.py .
node test_handoff.mjs
```

`check.py` is the structural pass. It walks every directory, not just the root, and verifies that every `class` token resolves to a selector in `site.css` or in the checked page's own inline `<style>`, every internal link resolves to a file that exists whether it is written relative, root absolute, or as a full URL on this site's own origin (which is how the ledger writes its chrome, and how every canonical is written), there are no em dashes, curly quotes or unescaped `&`, tags are balanced, every colour token pair in use clears its WCAG threshold (ratios printed, not eyeballed), `site.js` parses under `node --check`, and no custom property is declared without being referenced. The class check and the `&` check run on the markup with `<script>` bodies blanked out, because a `class="..."` built by string concatenation and an `&&` in a filter are JavaScript, not authoring mistakes, and the noise from scanning them is exactly what gets a file exempted. Pages are reported by path, not basename, because `d4/guides.html` and a future `d4x/guides.html` are different files.

`test_handoff.mjs` is the one unit test in the repo, and it exists because
`/d4/ledger.html` has one function that takes input from a stranger's link and
whose failure mode is destroying a season of someone's progress. It covers the
handoff decoder and the merge: the accepted shapes, the base64url alphabet and
padding, and every malformed shape that has to be rejected before anything is
written. It carries no copy of the code under test. It slices the pure block out
of `d4/ledger.html` between the sentinel comments in that file and evaluates it,
so breaking the page turns the test red. No browser, no server, no dependencies.
If you move or rename those sentinels, the test fails loudly rather than passing
on nothing. The rest of that page needs a DOM and is not covered.

It was validated by mutation: each check was confirmed to fail on a deliberately broken copy of the site, not just to pass on the current one. The subdirectory walk and the relative link resolution were validated the same way, by confirming the previous version of `check.py` stays green on a mutation the current one catches. If you add a check, do the same, otherwise you cannot tell it from a check that never fires.

Any new colour pair goes into the `PAIRS` list in `check.py`, including a pair made of two colours that were already declared. That is what `--bloom` is for: the ember wash behind the hero and the monument is a real token rather than an inline `rgba()` stop, precisely so the text sitting over it gets computed instead of assumed.
