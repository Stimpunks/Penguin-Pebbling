#!/usr/bin/env python3
"""Cut the illustrations out of Helen's prompt cards, so the rest can be text.

The deck is being re-set: the prompt, the locution name and the aside are real
text in the page, and only the drawings stay as pictures. This is the tool that
separates the two.

**The saving is that the artwork does not vary per card.** All six Infodumping
cards carry the same penguin, the same speech bubble and the same cream ellipse;
only the words differ. So thirty pictures reduce to six — one pebble stack, which
is the same on every card in the deck, and one illustration per locution — and
the thirty prompts become thirty strings that were already in
penguin-pebbling.js.

Two different treatments, for a reason:

**The ellipse is masked to transparency.** It is a clean geometric shape, so an
inscribed ellipse over the detected bounding box lands on the artwork's own edge,
and the locution tint behind it then comes from CSS. Nothing has to match a
sampled colour for the join to be invisible.

**The pebbles keep their cream.** They are watercolour with soft edges, and
keying a background out from under a soft edge leaves a halo. A plain rectangle
on the exact cream of the panel is seamless instead — which is why this tool also
writes that cream into the stylesheet rather than leaving somebody to type it.

Geometry is detected, not hard-coded: the panel split is the first column that is
mostly locution tint, the ellipse is the cream inside that panel, and the pebbles
are whatever is not cream in the top of the left one. If Helen ever redraws a
card, this finds the new positions instead of cropping where the old ones were.

    python3 tools/make-card-art.py
    python3 tools/make-card-art.py --check   # report drift, write nothing
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is not installed. Run: python3 -m pip install --upgrade Pillow")

ROOT = Path(__file__).resolve().parent.parent
PRINT = ROOT / "cards" / "print"
OUT = ROOT / "cards" / "art"
CSS = ROOT / "penguin-pebbling.css"

# id -> the card the artwork is taken from. Any of the six would do; -1 is the
# one that exists for every locution.
LOCUTIONS = {
    "infodumping": "infodumping-1.png",
    "parallel-play": "parallel-play-1.png",
    "support-swapping": "support-swapping-1.png",
    "penguin-pebbling": "penguin-pebbling-1.png",
    "deep-pressure": "deep-pressure-1.png",
}
PEBBLE_SOURCE = "parallel-play-1.png"

ELLIPSE_W = 560     # output width; ~2x the widest it is ever displayed
# One height for all five. The detected boxes differ by under 1%, and
# normalising lets the markup carry exact width/height attributes — so the
# space is reserved correctly before the image lands and nothing shifts.
ELLIPSE_H = 770
PEBBLE_W = 200
SUPERSAMPLE = 4     # for a smooth alpha edge on the ellipse mask

MARK_OPEN = "/* card-art:palette — written by tools/make-card-art.py */"
MARK_CLOSE = "/* /card-art:palette */"


def near(c, t, tol):
    return sum(abs(a - b) for a, b in zip(c, t)) <= tol


def analyse(im):
    """Return (split_x, cream, tint, ellipse_bbox) for one prompt card."""
    W, H = im.size
    px = im.load()
    cream = px[int(W * 0.05), int(H * 0.5)]
    tint = px[int(W * 0.97), int(H * 0.5)]

    split = None
    for x in range(0, W, 4):
        hits = sum(near(px[x, y], tint, 14) for y in range(0, H, 4))
        if hits > (H / 4) * 0.5:
            split = x
            break
    if split is None:
        sys.exit("could not find the panel split — has the card layout changed?")

    # The ellipse is the one large pale region inside the tinted panel. Find its
    # colour by frequency rather than by sampling a fixed point: the illustration
    # sits in the middle of it and differs per locution, so any point you pick in
    # advance lands on a penguin on some card and on the tint on another.
    from collections import Counter
    tally = Counter()
    for x in range(split, W, 3):
        for y in range(0, H, 3):
            c = px[x, y]
            if sum(c) > 600 and not near(c, tint, 40):
                tally[c] += 1
    if not tally:
        sys.exit("could not find the cream ellipse in the tinted panel")
    ell_cream = tally.most_common(1)[0][0]

    # Bound the ellipse by row and column DENSITY, not by the outermost matching
    # pixel. A bare min/max is one stray pixel away from being wrong, and it was:
    # anti-aliasing along the "Penguin Pebbling Game" heading matches the cream
    # closely enough to drag the top of the box up over the text, which then gets
    # cut out as if it were part of the drawing. A real row of the ellipse has
    # hundreds of cream pixels; a row of stray ones has a handful.
    from collections import defaultdict
    rows, cols = defaultdict(int), defaultdict(int)
    for x in range(split, W, 2):
        for y in range(0, H, 2):
            if near(px[x, y], ell_cream, 10):
                rows[y] += 1
                cols[x] += 1
    if not rows:
        sys.exit("could not find the cream ellipse in the tinted panel")
    rmax, cmax = max(rows.values()), max(cols.values())
    ys = [y for y, n in rows.items() if n >= rmax * 0.25]
    xs = [x for x, n in cols.items() if n >= cmax * 0.25]
    return split, cream, tint, (min(xs), min(ys), max(xs), max(ys))


def ellipse_cut(im, box, width):
    crop = im.crop(box).convert("RGBA")
    w, h = crop.size
    mask = Image.new("L", (w * SUPERSAMPLE, h * SUPERSAMPLE), 0)
    ImageDraw.Draw(mask).ellipse(
        (0, 0, w * SUPERSAMPLE - 1, h * SUPERSAMPLE - 1), fill=255)
    crop.putalpha(mask.resize((w, h), Image.LANCZOS))
    return crop.resize((width, ELLIPSE_H), Image.LANCZOS)


def build():
    """Everything this tool would write: {path: bytes} plus the palette."""
    import io
    files, palette = {}, {}

    for slug, name in LOCUTIONS.items():
        src = PRINT / name
        if not src.exists():
            sys.exit(f"missing print master: {src}")
        with Image.open(src) as im:
            im = im.convert("RGB")
            split, cream, tint, box = analyse(im)
            art = ellipse_cut(im, box, ELLIPSE_W)
        buf = io.BytesIO()
        art.save(buf, format="WEBP", quality=88, method=6)
        files[f"{slug}.webp"] = buf.getvalue()
        palette[slug] = tint
        palette.setdefault("cream", cream)

    with Image.open(PRINT / PEBBLE_SOURCE) as im:
        im = im.convert("RGB")
        W, H = im.size
        px = im.load()
        split, cream, _, _ = analyse(im)
        xs, ys = [], []
        for x in range(int(split * 0.12), int(split * 0.90), 2):
            for y in range(int(H * 0.02), int(H * 0.22), 2):
                if not near(px[x, y], cream, 26):
                    xs.append(x)
                    ys.append(y)
        box = (min(xs), min(ys), max(xs), max(ys))
        peb = im.crop(box)
        peb = peb.resize((PEBBLE_W, round(peb.height * PEBBLE_W / peb.width)), Image.LANCZOS)
    buf = io.BytesIO()
    peb.save(buf, format="WEBP", quality=90, method=6)
    files["pebbles.webp"] = buf.getvalue()

    return files, palette


def css_block(palette):
    hexa = lambda c: "#%02x%02x%02x" % tuple(c)
    lines = [MARK_OPEN, ":root {", f"  --card-cream: {hexa(palette['cream'])};"]
    for slug in LOCUTIONS:
        lines.append(f"  --card-tint-{slug}: {hexa(palette[slug])};")
    lines += ["}", MARK_CLOSE]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()

    files, palette = build()
    block = css_block(palette)
    css = CSS.read_text(encoding="utf-8")
    if MARK_OPEN not in css or MARK_CLOSE not in css:
        sys.exit(f"{CSS.name} has no {MARK_OPEN} … {MARK_CLOSE} block to write into")
    start = css.index(MARK_OPEN)
    end = css.index(MARK_CLOSE) + len(MARK_CLOSE)
    current = css[start:end]

    stale = [n for n, data in files.items()
             if not (OUT / n).exists() or (OUT / n).read_bytes() != data]
    if current != block:
        stale.append(f"{CSS.name} palette block")

    if not stale:
        print(f"card art already matches the print masters "
              f"({len(files)} images, {len(LOCUTIONS)} locutions)")
        return 0
    if args.check:
        print("out of date: " + ", ".join(stale))
        print("Run without --check.")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    for n, data in files.items():
        (OUT / n).write_bytes(data)
    CSS.write_text(css[:start] + block + css[end:], encoding="utf-8")
    total = sum(len(d) for d in files.values())
    print(f"card art written — {len(files)} images, {total:,} bytes total")
    for n, d in sorted(files.items()):
        print(f"  cards/art/{n:<24} {len(d):>7,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
