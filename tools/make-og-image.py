#!/usr/bin/env python3
"""Generate og-image.png — the picture that represents the game when the URL is
shared on Bluesky, Discord, Mastodon, Slack or anywhere else that unfurls a link.

**It draws the card the way the site now draws it.** This used to letterbox one
of Helen's printed cards onto the sage. That was right while the site showed her
pictures; since the deck was re-set as text it showed something the site no
longer does — someone following the link arrived at a different-looking game.

So this composes the same card the browser composes: the cream panel with the
pebble stack, the locution name, the prompt and the aside, and the tinted panel
with the heading, the illustration and the credit.

**Nothing here is a second copy of anything.** The prompt comes out of
penguin-pebbling.js through make-search-index.py's parser, the colours out of the
stylesheet's own card tokens, the pebble geometry out of favicon.svg, the
illustration out of cards/art/, and the type out of the same woff2 the page is
set in — decompressed and pinned to a weight in memory, because Pillow cannot
read woff2 and a second copy of the font on disk is a second thing to keep in
step.

**Which card, and why that one.** The shortest prompt in the deck, at 70
characters: *"What brings you joy right now?"* A share card is looked at small,
and every Penguin Pebbling prompt runs past 157 characters — set large enough to
read, they do not fit. The game's name is on the card's own right panel, so
using an Infodumping card costs nothing in recognition and buys legibility.

PNG, not WebP: unfurlers are the least modern consumers of a site's images and
several still refuse WebP.

    python3 tools/make-og-image.py
    python3 tools/make-og-image.py --check   # report drift, write nothing
"""
import argparse
import importlib.util
import io
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is not installed. Run: python3 -m pip install --upgrade Pillow")
try:
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
except ImportError:
    sys.exit("fontTools is not installed. Run: python3 -m pip install --upgrade fonttools brotli")

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "og-image.png"
CSS = ROOT / "penguin-pebbling.css"
DECK_JS = ROOT / "penguin-pebbling.js"
FAVICON = ROOT / "favicon.svg"
ROMAN = ROOT / "fonts" / "atkinson-hyperlegible-next-roman-latin.woff2"
ITALIC = ROOT / "fonts" / "atkinson-hyperlegible-next-italic-latin.woff2"

W, H = 1200, 630
MARGIN = 34
RADIUS = 18
SPLIT = 1.25 / 2.25          # the card's wide-screen column split
CARD_SLUG = "infodumping"    # the shortest prompt in the deck lives here


# ---------------------------------------------------------------- sources


def deck():
    spec = importlib.util.spec_from_file_location(
        "make_search_index", ROOT / "tools" / "make-search-index.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.cards()


def chosen_card():
    """The shortest prompt of the chosen locution — deterministic, not a sample."""
    want = CARD_SLUG.replace("-", " ").title()
    hits = [c for c in deck() if c[0] == want]
    if not hits:
        sys.exit(f"no {want!r} cards found — has the deck changed?")
    return min(hits, key=lambda c: len(c[1]))


def footer_text():
    js = DECK_JS.read_text(encoding="utf-8")
    m = re.search(r"const FOOTER =\s*((?:\s*\"(?:[^\"\\]|\\.)*\"\s*\+?)+);", js)
    if not m:
        sys.exit("could not find FOOTER in penguin-pebbling.js")
    return "".join(re.findall(r"\"((?:[^\"\\]|\\.)*)\"", m.group(1))).encode().decode("unicode_escape")


def palette():
    css = CSS.read_text(encoding="utf-8")
    want = ["--card-cream", f"--card-tint-{CARD_SLUG}", "--card-ink",
            "--card-ink-panel", "--card-pebble", "--paper"]
    out = {}
    for name in want:
        m = re.search(re.escape(name) + r":\s*(#[0-9a-fA-F]{6})", css)
        if not m:
            sys.exit(f"{name} not found in the stylesheet — cannot match the card")
        out[name] = m.group(1)
    return out


def pebble_geometry():
    """The three ellipses out of favicon.svg, so there is one drawing of them."""
    svg = FAVICON.read_text(encoding="utf-8")
    els = re.findall(
        r'<ellipse cx="([\d.]+)" cy="([\d.]+)" rx="([\d.]+)" ry="([\d.]+)"', svg)
    if len(els) != 3:
        sys.exit(f"expected 3 ellipses in favicon.svg, found {len(els)}")
    return [tuple(float(v) for v in e) for e in els]


def font(path, weight, size):
    """Pillow cannot read woff2, and fontTools can. Decompress and pin in memory."""
    f = TTFont(path)
    if "fvar" in f:
        f = instancer.instantiateVariableFont(f, {"wght": weight})
    buf = io.BytesIO()
    f.flavor = None
    f.save(buf)
    buf.seek(0)
    return ImageFont.truetype(buf, size)


# ---------------------------------------------------------------- drawing


def wrap(draw, text, fnt, width):
    lines = []
    for para in text.split("\n"):
        words, line = para.split(), ""
        for word in words:
            trial = (line + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def tracked(draw, xy, text, fnt, fill, tracking):
    """Letterspacing, which the locution name has and Pillow does not do."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking


def tracked_width(draw, text, fnt, tracking):
    return sum(draw.textlength(c, font=fnt) + tracking for c in text) - tracking


def build():
    pal = palette()
    name, prompt, _aside = chosen_card()
    aside = footer_text()

    card = Image.new("RGBA", (W - MARGIN * 2, H - MARGIN * 2), pal["--card-cream"])
    cw, ch = card.size
    left_w = round(cw * SPLIT)
    d = ImageDraw.Draw(card)
    d.rectangle([left_w, 0, cw, ch], fill=pal[f"--card-tint-{CARD_SLUG}"])

    # ---- left panel ----------------------------------------------------
    f_name = font(ROMAN, 800, 31)
    f_prompt = font(ROMAN, 400, 33)
    f_aside = font(ITALIC, 400, 18)

    pad = 52
    inner = left_w - pad * 2

    peb_box, peb_col = 108, pal["--card-pebble"]

    # Centre pebbles + name + prompt in the space above the aside. On the page
    # the card is only as tall as its content; here it is a fixed 630, so the
    # same elements left at the top of a taller box read as an accident rather
    # than as the card.
    prompt_lines = wrap(d, prompt, f_prompt, inner)
    aside_lines = wrap(d, aside, f_aside, inner)
    block_h = peb_box * 0.86 + 62 + 47 * len(prompt_lines)
    aside_top = ch - 34 - 22 * len(aside_lines)
    y = max(40, (aside_top - block_h) / 2)
    layer = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for (cx, cy, rx, ry), opacity in zip(pebble_geometry(), (1.0, 0.74, 0.54)):
        s = peb_box / 64.0
        ox, oy = left_w / 2 - peb_box / 2, y
        ld.ellipse([ox + (cx - rx) * s, oy + (cy - ry) * s,
                    ox + (cx + rx) * s, oy + (cy + ry) * s],
                   fill=peb_col + "%02x" % round(opacity * 255))
    card.alpha_composite(layer)
    y += peb_box * 0.86

    label = name.upper()
    tw = tracked_width(d, label, f_name, 4)
    tracked(d, (left_w / 2 - tw / 2, y), label, f_name, pal["--card-ink"], 4)
    y += 62

    for line in prompt_lines:
        lw = d.textlength(line, font=f_prompt)
        d.text((left_w / 2 - lw / 2, y), line, font=f_prompt, fill=pal["--card-ink"])
        y += 47

    ay = aside_top
    for line in aside_lines:
        lw = d.textlength(line, font=f_aside)
        d.text((left_w / 2 - lw / 2, ay), line, font=f_aside, fill=pal["--card-ink"])
        ay += 22

    # ---- right panel ---------------------------------------------------
    f_small = font(ROMAN, 400, 19)
    right_x, right_w = left_w, cw - left_w
    ink_panel = pal["--card-ink-panel"]

    head = "Penguin Pebbling Game"
    hw = d.textlength(head, font=f_small)
    d.text((right_x + right_w / 2 - hw / 2, 34), head, font=f_small, fill=ink_panel)

    art_path = ROOT / "cards" / "art" / f"{CARD_SLUG}.webp"
    if not art_path.exists():
        sys.exit(f"missing {art_path} — run tools/make-card-art.py first")
    with Image.open(art_path) as art:
        art = art.convert("RGBA")
        target_h = ch - 150
        scale = target_h / art.height
        art = art.resize((round(art.width * scale), target_h), Image.LANCZOS)
        card.alpha_composite(art, (round(right_x + right_w / 2 - art.width / 2), 82))

    credit = "Autistic Realms & Stimpunks © 2026"
    crw = d.textlength(credit, font=f_small)
    d.text((right_x + right_w / 2 - crw / 2, ch - 44), credit, font=f_small, fill=ink_panel)

    # ---- round the corners, seat it on the page ------------------------
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], RADIUS, fill=255)
    card.putalpha(mask)

    canvas = Image.new("RGB", (W, H), pal["--paper"])
    canvas.paste(card, (MARGIN, MARGIN), card)
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()

    img = build()
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()

    if TARGET.exists() and TARGET.read_bytes() == data:
        print("og-image.png already matches the card")
        return 0
    if args.check:
        print("og-image.png is out of date with the card. Run without --check.")
        return 1
    TARGET.write_bytes(data)
    print(f"og-image.png written — {W}x{H}, {len(data):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
