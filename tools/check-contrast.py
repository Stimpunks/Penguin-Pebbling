#!/usr/bin/env python3
"""Check text/background contrast against WCAG 2.1 AA, in BOTH themes.

A typeface chosen for legibility and a body size chosen for legibility are both
undone by colours the reader cannot resolve. This measures the pairs the page
actually uses rather than trusting that they look fine on this monitor.

**It checks light and dark.** A dark mode that fails AA is the ordinary way this
goes wrong: the light palette gets designed carefully and the dark one gets
eyeballed at night, when everything looks fine because your pupils are wide.

The palette is deliberately low-stimulation, which is about SURFACES — paper,
panel and sunk sit within a few percent of each other, and there is no pure white
or pure black anywhere. It is not about text. Text contrast stays high, and this
is what says so.

AA is 4.5:1 for normal text and 3:1 for large text (>= 24px, or >= 18.66px bold).
Run:  python3 tools/check-contrast.py
"""
import re
import sys
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "penguin-pebbling.css"


def srgb(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexcolor):
    h = hexcolor.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b)


def ratio(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def tokens_in(block):
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{3,8})\s*;", block))


def themes():
    text = CSS.read_text(encoding="utf-8")

    # Anchor on the palette's own first declaration, not on the first ":root {"
    # in the file. The card art palette and the card inks are in :root blocks of
    # their own above this one, and "the first :root" quietly became the wrong
    # one the moment they were added.
    light_start = text.index(":root {\n  color-scheme: light dark;")
    light = tokens_in(text[light_start:text.index("\n}", light_start)])

    # The toggle's block is the authority for dark; the prefers-color-scheme block
    # must agree with it, and that is checked below rather than assumed.
    dark_start = text.index(':root[data-theme="dark"] {')
    dark = tokens_in(text[dark_start:text.index("\n}", dark_start)])

    media_start = text.index(':root:not([data-theme="light"]) {')
    media = tokens_in(text[media_start:text.index("\n  }", media_start)])

    return light, dark, media


LOCS = ["id", "pp", "ss", "pb", "dp"]


def pairs(t):
    P, W, S = t["--paper"], t["--paper-warm"], t["--paper-sunk"]
    out = [
        ("body text on paper",        t["--ink"],        P, False),
        ("headings on paper",         t["--ink-strong"], P, True),
        ("body on panel",             t["--ink"],        W, False),
        ("body on sunk",              t["--ink"],        S, False),
        ("secondary prose on paper",  t["--ink-soft"],   P, False),
        ("secondary on panel",        t["--ink-soft"],   W, False),
        ("faint labels on paper",     t["--ink-faint"],  P, False),
        ("faint labels on panel",     t["--ink-faint"],  W, False),
        ("faint labels on sunk",      t["--ink-faint"],  S, False),
        ("links on paper",            t["--accent"],     P, False),
        ("links on panel",            t["--accent"],     W, False),
        ("button text on btn face",   t["--ink"],        t["--btn-face"], False),
        ("button text on btn hover",  t["--ink"],        t["--btn-face-hover"], False),
        ("card locution on paper",    t["--focus"],      P, False),
    ]
    for k in LOCS:
        bg = t[f"--loc-{k}-bg"]
        out.append((f"locution {k}: name",  t[f"--loc-{k}-name"], bg, False))
        out.append((f"locution {k}: body",  t["--ink-soft"],      bg, False))
    return out


CARD_LOCS = ["infodumping", "parallel-play", "support-swapping",
             "penguin-pebbling", "deep-pressure"]


def card_tokens():
    """The re-set deck's own colours, which do not vary by theme.

    The card is Helen's artwork and stays bright in dark mode — dimming it would
    misrepresent the work — so these are one set of pairs, not two.
    """
    text = CSS.read_text(encoding="utf-8")
    start = text.index("/* card-art:palette")
    block = text[start:text.index("/* /card-art:palette */")]
    t = tokens_in(block)
    ink_start = text.index(":root {\n  --card-ink:")
    t.update(tokens_in(text[ink_start:text.index("\n}", ink_start)]))
    return t


def card_pairs(t):
    """Every text/background pair on the re-set card.

    These did not exist while the prompt was lettered into a picture, and that is
    the point: nothing measured Helen's #b28a5e on her cream, which is 2.57:1. As
    real text it is this site's responsibility, so it is measured here.
    """
    cream = t["--card-cream"]
    out = [
        ("prompt on card cream",   t["--card-ink"], cream, False),
        ("locution name on cream", t["--card-ink"], cream, True),
        ("aside on card cream",    t["--card-ink"], cream, False),
    ]
    for k in CARD_LOCS:
        out.append((f"panel text on {k}", t["--card-ink-panel"], t[f"--card-tint-{k}"], False))
    return out


def check(name, t):
    print(f"\n── {name} " + "─" * (56 - len(name)))
    bad = 0
    for label, fg, bg, large in pairs(t):
        r = ratio(fg, bg)
        need = 3.0 if large else 4.5
        ok = r >= need
        bad += not ok
        print(f"  {label:28} {r:6.2f}:1  need {need:>4}   {'PASS' if ok else 'FAIL'}")
    return bad


def main():
    light, dark, media = themes()

    drift = {k for k in set(dark) | set(media) if dark.get(k) != media.get(k)}
    missing = set(light) - set(dark) - {"--font"}
    missing = {k for k in missing if k.startswith(("--paper", "--ink", "--line", "--accent",
                                                  "--focus", "--btn", "--card", "--loc", "--shadow"))}

    bad = check("LIGHT", light) + check("DARK", dark)

    # The re-set card is one set of colours in both themes, so it is checked once.
    ct = card_tokens()
    print("\n── CARD (both themes) " + "─" * 35)
    for label, fg, bg, large in card_pairs(ct):
        r = ratio(fg, bg)
        need = 3.0 if large else 4.5
        ok = r >= need
        bad += not ok
        print(f"  {label:28} {r:6.2f}:1  need {need:>4}   {'PASS' if ok else 'FAIL'}")

    print()
    if drift:
        print(f"MISMATCH: the data-theme block and the prefers-color-scheme block "
              f"disagree on {', '.join(sorted(drift))}")
        bad += len(drift)
    if missing:
        print(f"MISSING in dark: {', '.join(sorted(missing))}")
        bad += len(missing)

    if bad:
        print(f"\n{bad} problem(s).")
        return 1
    print("Both themes and the card meet WCAG 2.1 AA, and the two dark blocks agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
