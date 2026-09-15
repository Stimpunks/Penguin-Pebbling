#!/usr/bin/env python3
"""Check text/background contrast against WCAG 2.1 AA.

A typeface chosen for legibility and a body size chosen for legibility are both
undone by grey-on-cream that the reader cannot resolve. This measures the pairs
the page actually uses rather than trusting that they look fine on this monitor.

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


def tokens():
    text = CSS.read_text(encoding="utf-8")
    block = text[text.index(":root {"):text.index("}", text.index(":root {"))]
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{3,6})\s*;", block))


# (label, foreground, background, is_large_text)
def pairs(t):
    P, W, S = t["--paper"], t["--paper-warm"], t["--paper-sunk"]
    return [
        ("body text on paper",        t["--ink"],        P, False),
        ("headings on paper",         t["--ink-strong"], P, True),
        ("secondary prose on paper",  t["--ink-soft"],   P, False),
        ("secondary on warm paper",   t["--ink-soft"],   W, False),
        ("faint labels on paper",     t["--ink-faint"],  P, False),
        ("faint labels on warm",      t["--ink-faint"],  W, False),
        ("links on paper",            t["--accent"],     P, False),
        ("button text on #e8e0d5",    t["--ink"],        "#e8e0d5", False),
        ("take-pebble on warm",       t["--focus"],      W, False),
        ("card locution on paper",    t["--focus"],      P, False),
        ("body on sunk hover",        t["--ink"],        S, False),
    ]


def main():
    t = tokens()
    bad = 0
    print(f"{'pair':32} {'ratio':>7}  need   verdict")
    for label, fg, bg, large in pairs(t):
        r = ratio(fg, bg)
        need = 3.0 if large else 4.5
        ok = r >= need
        bad += not ok
        print(f"{label:32} {r:6.2f}:1  {need:>4}   {'PASS' if ok else 'FAIL'}")
    print()
    if bad:
        print(f"{bad} pair(s) below WCAG AA.")
        return 1
    print("All pairs meet WCAG 2.1 AA.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
