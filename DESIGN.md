---
name: schillman.se
description: Farming tools and verified guides for the games one person actually plays.
colors:
  bg: "#110d0f"
  surface: "#1c161a"
  surface-hi: "#241c21"
  border: "#332830"
  border-soft: "#241b20"
  ink: "#eee6e1"
  ink-dim: "#a89892"
  accent: "#ff5a36"
  accent-hi: "#ff7a52"
  accent-ink: "#1c0d07"
  gold: "#c9a15a"
  gold-dim: "#8a7040"
  bloom: "#371915"
typography:
  display:
    fontFamily: "Cinzel, serif"
    fontSize: "clamp(38px, 7.2vw, 76px)"
    fontWeight: 600
    lineHeight: 1.02
    letterSpacing: "-0.01em"
  heading:
    fontFamily: "Barlow Condensed, system-ui, sans-serif"
    fontSize: "26px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.01em"
  label:
    fontFamily: "Barlow Condensed, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.2em"
  body:
    fontFamily: "Barlow, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  longform:
    fontFamily: "Barlow, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: "normal"
  mono:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.92em"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
rounded:
  marker: "2px"
  sm: "4px"
  md: "8px"
  lg: "14px"
  pill: "99px"
  dot: "50%"
spacing:
  xs: "6px"
  sm: "10px"
  md: "18px"
  lg: "28px"
  xl: "44px"
  xxl: "56px"
components:
  monument:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "40px 44px"
  monument-cta:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "11px 22px"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "24px"
  nav-pill:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-dim}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "5px 12px"
  nav-pill-current:
    backgroundColor: "{colors.surface-hi}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "5px 12px"
  chip:
    backgroundColor: "{colors.surface-hi}"
    textColor: "{colors.ink-dim}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "5px 12px"
  note:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-dim}"
    rounded: "{rounded.md}"
    padding: "16px 18px"
---

# Design

Recorded from the built site on the `redesign` branch, not from intention.
`site.css` is the only stylesheet and the only source of truth; this file
describes what is in it.

## Overview

A near-black ember world for a fan site about a game set in hell. One saturated
accent carries every interactive element; gold is framing and labels only and is
never a second accent. Display type is Cinzel, used for the site's few real
headlines and for the game name on the hub. Everything else is Barlow for
reading and Barlow Condensed, tracked out and uppercased, for labels, stats and
buttons.

Two levels of chrome. The hub at `/` is a game selector and owns `.hero` and
`.monument`. Every game section (`/d4/` today) reuses the shared page furniture
and identifies itself with a `.topbar__crumb`: the wordmark, a hairline, the
game name. Nothing in the stylesheet is Diablo specific, so a
second game needs a directory and a monument, not a new system.

The single game state is a design decision, not a gap. The hub gives its one
entry a full width monument and then says nothing else about it. A card grid
with one card reads as three missing cards. A numbered register under the
monument was built and then cut for the same reason: a one row list with an `01`
in the margin is the same grid in a different shape, and it made the page count
itself. The monument is the whole answer, and a second game is a second
monument.

## Colors

Dark is not a style choice here. The scene is a player alt tabbed out of a
full screen game at night, and a light page in that context is a flashbang.

- `bg` is the page. `surface` is a panel, `surface-hi` a raised element inside
  one (chips, current nav pill).
- `accent` `#ff5a36` is the only accent. It fills primary buttons, draws the
  hairline that traces a hovered card, marks the current nav pill, and colours
  the ember sparks. `accent-hi` is its text-safe form: links, card titles, the
  emphasised words in a headline, and the focus ring.
- `gold` is section labels and table heads. `gold-dim` is hairline rules,
  bullet markers and the nav pill outline. Gold never fills a button and never
  marks state.
- `bloom` is `bg` with `accent` composited over it at 16 percent. It is declared
  as a real token rather than written as an inline `rgba()` stop so that
  `check.py` can compute contrast against it, because it is the effective
  background under the hero glow and behind the monument.

Every pair in use is in the `PAIRS` list in `check.py` with its threshold, and
the ratios are printed on every run. Adding a colour, or a new combination of
two existing colours, means adding a pair there in the same commit. `border` is
deliberately absent: it draws decorative panel outlines, and every boundary that
IS the affordance for a control is listed and must clear 3:1.

## Typography

- **Cinzel** for the hub headline, the game name on the monument, guide titles
  and card titles. Roman capitals, which is the game's own register. Nothing
  else uses it.
- **Barlow Condensed**, 600, uppercase, tracked 0.08em to 0.28em, for every
  label, stat, button, nav pill, table head and section eyebrow. This is the
  workhorse and it is what makes the site look built rather than written.
- **Barlow** for all reading. `1.6` line height in general, `1.7` in `.longform`
  where a guide is actually read.

Measure is capped: `70ch` for prose, `48ch` for the monument argument, `58ch`
for the hero lede. A page that ignores the cap looks wrong immediately.

## Layout

- `.app` is the page container at `920px`. `.app--narrow` at `760px` is for
  reading (every guide page). `.app--wide` at `1080px` is the hub only.
- One spacing rhythm: `44px` between sections, `18px` to `28px` inside them,
  more space above a heading than below it.
- Four breakpoints. `min-width:860px` turns the monument into its two column
  grid and the hub's editorial rules into two columns; `max-width:859px` stacks
  the monument as name, action, argument. `max-width:640px` tightens the monument
  padding. `min-width:860px and max-height:820px` tightens the hero's vertical
  rhythm on short laptops so the primary action stays in the first viewport, and
  it never touches the headline scale.
- Tables always sit inside `.table-scroll` so a wide table scrolls itself
  instead of scrolling the page.

## Elevation and depth

Depth comes from three quiet layers, never from a drop shadow on a hover state.

1. A fixed noise overlay on `body::before` at 3.5 percent, over everything.
2. Two page scale radial gradients on `body`: the ember bloom at top left, a
   fainter gold at top right.
3. `--shadow-panel`, one inset white hairline plus a soft dark cast, on panels
   only.

The monument adds a fourth: a radial `bloom` wash pinned outside its top right
corner, which brightens on hover. It never sits under text that has not been
contrast checked against `bloom`.

## Shapes

Three radii carry the form language: `14px` on panels, `8px` on buttons and
callouts, a full pill on chips and nav. `4px` exists only on the focus ring, and
two decorative values exist only as marks, `2px` on the square bullet and `50%`
on the ember spark. Rules are always `1px` and always a gradient that fades to
transparent at one end, which is the site's signature line.

## Components

- **`.monument`** The hub's game entry. A whole panel that is one link. Two
  plates side by side above `860px`: name, season and action on the left, the
  argument and stats on the right, divided by a hairline. DOM order is the
  mobile order (name, argument, action) and the desktop grid moves the action
  back without touching it.
- **`.topbar__crumb`** Wordmark, gold divider, game name, then a hairline that
  draws itself to the container edge. The only thing that says you are inside a
  section rather than on a different site.
- **`.sitenav`** Pills. The outline is the affordance, so it is `gold-dim` and
  must clear 3:1 against both the page and its own fill. An ember wash sweeps in
  from the leading edge on hover and on keyboard focus, identically.
- **`.card`, `.guide-list`** Both lift on hover and both grow an ember mark from
  the leading edge: the card an ember hairline across its top, the guide row an
  ember bar down its left. Same gesture, two surfaces.
- **`.facts`, `.cover-list`, `.note`, `.sources`, `table`** The guide furniture.
  Unchanged from before the hub split, because the guide prose was not rewritten.

## Motion

Four layers, all in `site.css`, all switched off wholesale under
`prefers-reduced-motion: reduce`.

1. **Ambient embers.** Fourteen 2 to 4px sparks drifting up a fixed, aria-hidden
   layer. Transform and opacity only, so the field stays on the compositor.
2. **Load sequence.** A staged entrance per page: mark, rule drawing left to
   right, title, lede, then the monument rising with its sigil breathing. Gated
   on the `.js` class, so with scripting off the page is simply visible.
3. **Scroll reveals.** `.reveal` sections fade and rise in as they enter the
   viewport, staggered by `--i`. One IntersectionObserver in `site.js`, with two
   guards so a hidden start state can never cost a reader content: `onerror` on
   the script tag drops the `.js` class if the file fails to load, `check.py`
   runs `node --check` on it so a file that loads but does not parse fails the
   build instead of the page, and `@media print` pins every reveal visible with
   its transition off.
4. **Choreography.** Hover and focus share every gesture: the nav wash, the card
   hairline, the guide bar, the CTA ring, the prose underline growing from the
   leading edge. All left to right, quiet to lit, one grammar.

Cross document transitions are the `@view-transition` declaration plus a named
`page` on `.app` and a named `mark` on the wordmark, so the wordmark holds still
while the page swaps. No JavaScript. Browsers without it simply navigate.

Easing is two curves: `--ease` for anything arriving, `--ease-soft` for anything
changing in place.

## Do's and don'ts

- **Do** add a new colour pair to `PAIRS` in `check.py` before shipping it, even
  when both colours already exist.
- **Do** put any new motion into the `prefers-reduced-motion` block in the same
  commit. It is a floor, not a dial.
- **Do** keep content visible without JavaScript. Anything hidden at rest is
  gated on `.js`.
- **Don't** introduce a second accent. Gold is framing and labels.
- **Don't** add a fourth structural radius or a second easing pair.
- **Do** treat the type ramp as the one part of this system that is looser than
  it should be. It carries about twenty literal sizes inherited from before the
  hub split, the design detector flags every one of them as advisory, and
  tightening it means changing the look of three verified guide pages. It is a
  real debt, deliberately not paid here.
- **Don't** put text over the ember bloom without a `bloom` pair in `PAIRS`.
- **Don't** use Cinzel below 20px or for anything that is not a title.
- **Don't** add an external font, script or stylesheet beyond the Google Fonts
  link and the AdSense tag that are already on every page.
