#!/usr/bin/env python3
"""Structural + a11y checks for schillman.se. Exits non-zero on any failure.

Checks:
  1. every class= token used in HTML markup has a matching selector, in
     site.css or in that page's own inline <style>
  2. every internal href or src, absolute or relative, resolves to a real file
  3. no em dash, no curly quotes
  4. no unescaped & in markup (must be part of an entity)
  5. HTML parses and tags are balanced
  6. WCAG contrast for the declared foreground/background pairs
 6b. a token a page copies inline still has site.css's value
  7. site.js parses (node --check)
  8. no custom property declared without being referenced

The site is no longer flat: everything Diablo IV lives under /d4/ and a second
game gets its own directory beside it. So the walk is recursive, and pages are
reported by their path relative to the root rather than by basename, because
d4/guides.html and a future d4x/guides.html are different files.
"""
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
FAILURES = []


def fail(msg):
    FAILURES.append(msg)


def rel(path):
    """Path as written in the tree, so d4/guides.html is not just guides.html."""
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


# ---------- markup vs script ----------
# The class check and the & check are both about HTML markup. A class="..." or
# an && inside a <script> is JavaScript source, not an authoring mistake: the
# ledger builds its rows by string concatenation ('<li class="item'+cls+'"') and
# writes && in every filter. Scanning those produces tokens like item'+cls+' and
# a failure per boolean operator, which is exactly the noise that gets a file
# exempted, and an exempted file is unchecked. So those two checks run on the
# markup with script bodies blanked out. This is the same reasoning that already
# exempts site.js from the & scan, applied to the inline scripts doing that job.
# Newlines are preserved so reported line numbers still point at the real line.
# Everything else (links, em dashes, curly quotes, tag balance) still runs on
# the whole file, because those are wrong in a script too.
SCRIPT_BLOCK = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)
STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)


def markup_only(src):
    return SCRIPT_BLOCK.sub(lambda m: "\n" * m.group(0).count("\n"), src)


def selectors_in(text):
    return set(re.findall(r"\.([A-Za-z][\w-]*)", text))


# ---------- 1. class coverage ----------
# Resolved against site.css PLUS any inline <style> in the page being checked.
# The ledger has to keep working as a single file saved to disk with the network
# off, so it carries its own styles instead of linking site.css. Checking it
# against site.css alone would fail on ~100 real classes and checking nothing at
# all would be worse, so the page's own stylesheet counts for that page only. A
# class with no rule anywhere still fails, which is the whole point.
css = open(os.path.join(ROOT, "site.css"), encoding="utf-8").read()
css_classes = selectors_in(css)

html_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = sorted(d for d in dirnames
                         if not d.startswith(".") and d != "node_modules")
    for name in sorted(filenames):
        if name.endswith(".html"):
            html_files.append(os.path.join(dirpath, name))
html_files.sort()
if not html_files:
    fail("no html files found")

for f in html_files:
    src = open(f, encoding="utf-8").read()
    known = css_classes.union(*(selectors_in(block)
                                for block in STYLE_BLOCK.findall(src))) \
        if STYLE_BLOCK.search(src) else css_classes
    for attr in re.findall(r'class="([^"]*)"', markup_only(src)):
        for tok in attr.split():
            if tok not in known:
                fail(f"{rel(f)}: class '{tok}' has no selector in site.css "
                     f"or in this page's inline <style>")

# ---------- 2. internal links ----------
# Three forms have to resolve. An absolute href is rooted at the publish
# directory; a relative one is rooted at the directory of the page it sits in,
# and that is the form that silently breaks when a page moves into /d4/. A href
# ending in "/" is a directory, and Netlify serves its index.html.
#
# The third form is a full URL on this site's own origin. Canonicals have always
# been written that way, and the ledger writes its whole site chrome that way on
# purpose: it is a single file people save to disk, where a root relative href
# resolves against file:/// and goes nowhere. A link is internal because of where
# it points, not because of how it is spelled, so the origin is stripped and what
# is left is resolved like any other absolute href. Without this the ledger is
# the one page on the site whose internal links nothing checks, which is exactly
# where a hand copied URL rots unnoticed.
EXTERNAL = re.compile(r"^(?:[A-Za-z][\w+.-]*:|//)")
# The lookahead is what stops this matching https://schillman.se.example.com/.
OWN_ORIGIN = re.compile(r"^https://(?:www\.)?schillman\.se(?=/|$)")


def resolve(page, href):
    """Filesystem path an internal reference points at, or None if external."""
    href = href.split("#", 1)[0].split("?", 1)[0]
    if OWN_ORIGIN.match(href):
        # A bare "https://schillman.se" is the site root, the same as "/".
        href = OWN_ORIGIN.sub("", href) or "/"
    if not href or EXTERNAL.match(href):
        return None
    if href.startswith("/"):
        target = os.path.join(ROOT, href.lstrip("/"))
    else:
        target = os.path.join(os.path.dirname(page), href)
    if href.endswith("/") or os.path.isdir(target):
        target = os.path.join(target, "index.html")
    return os.path.normpath(target)


for f in html_files:
    src = open(f, encoding="utf-8").read()
    for attr in re.findall(r'(?:href|src)="([^"]*)"', src):
        target = resolve(f, attr)
        if target is None:
            continue
        if not os.path.isfile(target):
            fail(f"{rel(f)}: internal link '{attr}' -> missing {rel(target)}")

# ---------- 3 & 4. copy hygiene ----------
BAD_CHARS = {"—": "em dash", "‘": "curly quote", "’": "curly quote",
             "“": "curly quote", "”": "curly quote"}
ENTITY = re.compile(r"&(?:[A-Za-z][A-Za-z0-9]*|#\d+|#x[0-9A-Fa-f]+);")

# site.js is scanned for typographic junk in its comments but not for bare "&",
# because JavaScript writes "&&" legitimately and HTML entities mean nothing in
# it. Everything else is scanned for both.
ENTITY_EXEMPT = {os.path.normpath(os.path.join(ROOT, "site.js"))}

for f in html_files + [os.path.join(ROOT, "site.css"),
                       os.path.join(ROOT, "site.js")]:
    src = open(f, encoding="utf-8").read()
    name = rel(f)
    for ch, label in BAD_CHARS.items():
        if ch in src:
            line = src[: src.index(ch)].count("\n") + 1
            fail(f"{name}:{line}: {label} found")
    if os.path.normpath(f) in ENTITY_EXEMPT:
        continue
    src = markup_only(src) if f.endswith(".html") else src
    spans = {m.start() for m in ENTITY.finditer(src)}
    for m in re.finditer(r"&", src):
        if m.start() not in spans:
            line = src[: m.start()].count("\n") + 1
            ctx = src[m.start():m.start() + 40].replace("\n", " ")
            fail(f"{name}:{line}: unescaped & -> {ctx!r}")

# ---------- 5. tag balance ----------
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Balance(HTMLParser):
    def __init__(self, name):
        super().__init__(convert_charrefs=True)
        self.name = name
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            fail(f"{self.name}: stray </{tag}> at line {self.getpos()[0]}")
        elif self.stack[-1][0] != tag:
            fail(f"{self.name}: </{tag}> at line {self.getpos()[0]} closes "
                 f"<{self.stack[-1][0]}> opened at line {self.stack[-1][1]}")
            self.stack.pop()
        else:
            self.stack.pop()


for f in html_files:
    p = Balance(rel(f))
    p.feed(open(f, encoding="utf-8").read())
    p.close()
    for tag, line in p.stack:
        fail(f"{rel(f)}: <{tag}> opened at line {line} never closed")

# ---------- 6. WCAG contrast ----------
TOKENS = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6});", css))


def lum(hexcolor):
    r, g, b = (int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = f(r), f(g), f(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = lum(TOKENS[fg]), lum(TOKENS[bg])
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


# (fg, bg, minimum, what it is)
PAIRS = [
    ("ink", "bg", 4.5, "body text on page"),
    ("ink", "surface", 4.5, "body text on panel"),
    ("ink", "surface-hi", 4.5, "body text on raised panel"),
    ("ink-dim", "bg", 4.5, "secondary text on page"),
    ("ink-dim", "surface", 4.5, "secondary text on panel"),
    ("ink-dim", "surface-hi", 4.5, "chip label on raised panel"),
    ("accent-hi", "bg", 4.5, "link on page"),
    ("accent-hi", "surface", 4.5, "link/card title on panel"),
    ("gold", "bg", 4.5, "section label on page"),
    ("gold", "surface", 4.5, "table head on panel"),
    ("accent-ink", "accent", 4.5, "cta button text"),
    ("gold-dim", "bg", 3.0, "bullet marker + nav pill outline vs page"),
    ("gold-dim", "surface", 3.0, "nav pill outline vs its own fill, note border"),
    ("accent", "surface-hi", 3.0, "current-page nav outline"),
    ("accent-hi", "bg", 3.0, "focus ring on page"),
    ("accent-hi", "surface", 3.0, "focus ring on panel"),
    # Added with the hub redesign.
    # --bloom is the ember wash: --bg with --accent over it at 16%. It is a real
    # declared token precisely so that the text sitting on top of the hero glow
    # and the monument panel gets computed rather than assumed.
    ("ink", "bloom", 4.5, "monument body text over the ember bloom"),
    ("ink-dim", "bloom", 4.5, "hero lede over the ember bloom"),
    ("gold", "bloom", 4.5, "monument eyebrow over the ember bloom"),
    ("accent-hi", "bloom", 4.5, "season line and links over the ember bloom"),
    ("gold-dim", "bloom", 3.0, "hairline rule over the ember bloom"),
    ("gold", "surface-hi", 4.5, "label on raised panel"),
    ("accent-hi", "surface-hi", 4.5, "title or link on raised panel"),
    ("gold-dim", "surface-hi", 3.0, "crumb divider vs raised panel"),
    ("accent", "surface", 3.0, "ember hairline tracing a hovered card edge"),
    ("accent", "bg", 3.0, "hero rule and ember sparks vs page"),
]
# --border is deliberately absent: it draws decorative panel outlines on cards,
# chips and tables that are already identified by their fill and their text, so
# WCAG 1.4.11 does not apply to it. Every boundary that IS the affordance for an
# interactive control (nav pills, focus rings) is listed above and must pass.

print("WCAG contrast:")
for fg, bg, minimum, what in PAIRS:
    r = ratio(fg, bg)
    ok = r >= minimum
    print(f"  {'PASS' if ok else 'FAIL'}  {r:5.2f}:1  (needs {minimum}:1)  "
          f"--{fg} on --{bg}  [{what}]")
    if not ok:
        fail(f"contrast {r:.2f}:1 below {minimum}:1 for --{fg} on --{bg} ({what})")

# ---------- 6b. copied tokens have not drifted ----------
# The ledger carries its own copy of the design tokens, because it has to work as
# one file saved to disk with the network off and cannot link site.css. That copy
# is the only reason the ratios above describe it at all: a value that quietly
# drifted would leave check 6 reporting contrast for a colour the page does not
# use, which is worse than not checking it. Names a page does not share are its
# own business. Names it does share have to mean the same thing.
for f in html_files:
    src = open(f, encoding="utf-8").read()
    for block in STYLE_BLOCK.findall(src):
        for tok, val in re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6});", block):
            if tok in TOKENS and val.lower() != TOKENS[tok].lower():
                fail(f"{rel(f)}: inline --{tok} is {val} but site.css says "
                     f"{TOKENS[tok]}, and contrast is computed from site.css")

# ---------- 7. site.js parses ----------
# The onerror attribute on each <script src="/site.js"> only fires when the file
# fails to LOAD. A file that serves 200 and then fails to PARSE never runs, the
# inline setter has already put .js on the root element, and every .reveal
# section is permanently invisible with nothing left to catch it. Same outcome,
# different door. So the syntax gets checked here, the way the ledger repo runs
# node --check on its inline blocks.
sitejs = os.path.join(ROOT, "site.js")
if os.path.isfile(sitejs):
    if shutil.which("node") is None:
        fail("site.js: node not found, cannot syntax check it. Install node, or "
             "check it by hand before pushing.")
    else:
        proc = subprocess.run(["node", "--check", sitejs],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            lines = proc.stderr.strip().splitlines() or ["unknown error"]
            detail = next((ln for ln in lines if "Error" in ln), lines[0])
            fail(f"site.js: does not parse -> {detail.strip()}")

# ---------- 8. unused tokens ----------
all_src = css + "".join(open(f, encoding="utf-8").read() for f in html_files)
for tok in re.findall(r"--([\w-]+):", css):
    if all_src.count(f"var(--{tok})") == 0:
        fail(f"site.css: token --{tok} is declared but never referenced")

# ---------- report ----------
print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S):")
    for m in FAILURES:
        print("  -", m)
    sys.exit(1)
print("all checks passed")
