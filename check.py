#!/usr/bin/env python3
"""Structural + a11y checks for schillman.se. Exits non-zero on any failure.

Checks:
  1. every class= token used in HTML has a matching selector in site.css
  2. every internal href resolves to a file that exists
  3. no em dash, no curly quotes
  4. no unescaped & (must be part of an entity)
  5. HTML parses and tags are balanced
  6. WCAG contrast for the declared foreground/background pairs
"""
import glob
import os
import re
import sys
from html.parser import HTMLParser

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
FAILURES = []


def fail(msg):
    FAILURES.append(msg)


# ---------- 1. class coverage ----------
css = open(os.path.join(ROOT, "site.css"), encoding="utf-8").read()
css_classes = set(re.findall(r"\.([A-Za-z][\w-]*)", css))

html_files = sorted(glob.glob(os.path.join(ROOT, "*.html")))
if not html_files:
    fail("no html files found")

for f in html_files:
    src = open(f, encoding="utf-8").read()
    for attr in re.findall(r'class="([^"]*)"', src):
        for tok in attr.split():
            if tok not in css_classes:
                fail(f"{os.path.basename(f)}: class '{tok}' has no selector in site.css")

# ---------- 2. internal links ----------
for f in html_files:
    src = open(f, encoding="utf-8").read()
    for href in re.findall(r'href="(/[^"]*)"', src):
        target = href.lstrip("/") or "index.html"
        if not os.path.exists(os.path.join(ROOT, target)):
            fail(f"{os.path.basename(f)}: internal link '{href}' -> missing {target}")

# ---------- 3 & 4. copy hygiene ----------
BAD_CHARS = {"—": "em dash", "‘": "curly quote", "’": "curly quote",
             "“": "curly quote", "”": "curly quote"}
ENTITY = re.compile(r"&(?:[A-Za-z][A-Za-z0-9]*|#\d+|#x[0-9A-Fa-f]+);")

for f in html_files + [os.path.join(ROOT, "site.css")]:
    src = open(f, encoding="utf-8").read()
    name = os.path.basename(f)
    for ch, label in BAD_CHARS.items():
        if ch in src:
            line = src[: src.index(ch)].count("\n") + 1
            fail(f"{name}:{line}: {label} found")
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
    p = Balance(os.path.basename(f))
    p.feed(open(f, encoding="utf-8").read())
    p.close()
    for tag, line in p.stack:
        fail(f"{os.path.basename(f)}: <{tag}> opened at line {line} never closed")

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

# ---------- 7. unused tokens ----------
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
