# Product

<!-- impeccable:product-schema 1 -->

<!-- Every fact below is INFERRED from the written brief, README.md and the
     existing pages. No interview took place: this session had no structured
     question tool and no browser to serve a decision page, so the ask round
     could not run. Facts marked (inferred) should be confirmed by Sebastian
     before later work treats them as settled. -->

## Platform

web

## Stack

Static HTML and one shared stylesheet, no build step, no framework, no bundler,
no package.json. Deployed on Netlify from `main`. Constrains everything: no
external JS libraries, no CDN dependencies, same origin or inline only.

## Users

Seasonal Diablo IV players in the middle of a season, alt tabbed out of the game
with an hour to spend and a decision to make about where it goes. They arrive
from search on a specific mechanic question ("what does Writhe and Rot do", "how
do Escalation affixes stack") or return deliberately for the farming checklist.
(inferred) A second audience is the site owner himself, who uses the ledger for
his own grind.

## Product Purpose

Guides tell you what is strong. They are bad at telling you what you personally
have already done. This site is the second half of that: tools built around
state, not advice, plus the written explanations behind the terse checklist
lines. Success is a player who spends the session farming rather than reading.

## Positioning

Verified sourcing, stated in public. Every named boss, node, currency or
activity is checked against a current primary source before it ships, each guide
lists what it was checked against and the date it was checked, and where a
figure cannot be confirmed the page says so instead of smoothing it over.
Community guides copy each other's typos ("Writhe and Rot" got miscopied as
"Wither and Rot" across the community, including into this site's own ledger).
Being the page that admits its gaps is the differentiator.

## Operating Context

- The site is under active Google AdSense manual review. Status on 12 August
  2026: `Needs attention`, `Low value content`, ads.txt `Authorised`. The
  rejection was about the domain being thin. Content volume and publishing
  history are the gate.
- Old URLs are in a live sitemap that Google has crawled. A broken or missing
  redirect during review is a real cost, not a tidiness issue.
- Pages are written in batches and published spread out by a GitHub Actions
  workflow that fast forwards `main` by one commit from the `queue` branch every
  `INTERVAL_DAYS`, because bulk publishing is itself a scaled content abuse
  signal.
- There is no test framework. `python3 check.py .` is the whole gate, and it was
  validated by mutation rather than trusted.

## Capabilities and Constraints

- Pages currently shipped on `main`: homepage, guide index, about, contact,
  privacy, and three guides (Season 14 Death Awakening, War Plans, Escalations).
  A fourth, Helltides, plus five more, sit unpublished on `queue`.
- The Season 14 Farming Ledger is a separate single file app, today at
  `d4.schillman.se`, moving to a `/d4/ledger` slot on this domain. It is 48
  items across 13 categories, ticked into `localStorage`, exported and imported
  through the clipboard.
- The site is expanding from one game to many: Diablo IV is the only game today
  and the structure must make a second game a matter of adding a card and a
  directory.
- Netlify Pretty URLs is deliberately off (`pretty_urls = false` in
  `netlify.toml`) so that links, canonicals and the sitemap all agree on one URL
  form per page.
- AdSense script must stay in the `<head>` of every page.

## Brand Commitments

- Name: schillman.se. Author: Sebastian Schillman, a platform engineer in
  Sweden. One person, no team, no sponsor.
- One accent colour, ember `#ff5a36`. Gold is for framing and labels only and is
  never a second accent.
- No em dash characters and no curly quotes, anywhere, in copy or comments.
- Voice: plain, specific, slightly dry, willing to say "I could not confirm
  this". No hype, no tier lists, no leaderboard posturing.
- Independent fan site. Not affiliated with, sponsored by or endorsed by
  Blizzard Entertainment, and the disclaimer stays on every page.
- No affiliate links, no sponsored placements, no paid rankings.

## Evidence on Hand

- Three published guides carrying real verified prose, real source lists and
  real "last checked" dates. These are the site's proof and must not be
  rewritten.
- `check.py`: a working seven-check gate whose output is real and quotable.
- A real ledger with real numbers (48 items, 13 categories).
- What does not exist and must not be invented: traffic numbers, user counts,
  testimonials, review quotes, any second game's content, and any game mechanic
  not verified against a current source.

## Product Principles

1. State over advice. The thing a player cannot get elsewhere is a record of
   what they have already done.
2. Sourced or labelled unsourced. An honest gap beats a confident guess, because
   a reader can work around a gap.
3. Static, permanent, cheap. No account, no server, no build step, so a page
   still works years from now and offline.
4. One URL per page, and every old URL keeps working. Search is how people
   arrive.
5. The structure carries the next game without a rewrite.

## Accessibility & Inclusion

- WCAG contrast is computed with the relative luminance formula, never
  eyeballed: 4.5:1 for normal text, 3:1 for large text and for any boundary that
  is the only affordance on an interactive control. `check.py` enforces it over
  the declared token pairs.
- `prefers-reduced-motion: reduce` must fully neutralise motion, not soften it.
  Someone with a vestibular disorder gets a static, usable site. This is a floor,
  not a preference.
