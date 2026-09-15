#!/usr/bin/env python3
"""Generate og-image.png — the picture that represents the game when the URL is
shared on Bluesky, Discord, Mastodon, Slack or anywhere else that unfurls a link.

Social cards want 1200x630 (1.91:1). The cards are 1748x1240 (1.41:1), so a
width-fit crop would cut off the "Penguin Pebbling Game" title at the top and the
"Autistic Realms & Stimpunks" credit at the bottom — the two things a share image
most needs to keep. It is letterboxed on the site's sage instead, which keeps the whole
card and reads as deliberate rather than cropped.

PNG, not WebP: unfurlers are the least modern consumers of a site's images and
several still refuse WebP.

Re-run after changing the source card:  python3 tools/make-og-image.py
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is not installed. Run: python3 -m pip install --upgrade Pillow")

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "cards" / "print" / "penguin-pebbling-locution.png"
TARGET = ROOT / "og-image.png"
W, H = 1200, 630
PAPER = "#eaf1ef"   # --paper-warm; the share card sits on the site's own sage
PAD = 24


def main() -> int:
    if not SOURCE.exists():
        sys.exit(f"Missing source card: {SOURCE}")

    canvas = Image.new("RGB", (W, H), PAPER)
    with Image.open(SOURCE) as card:
        card = card.convert("RGB")
        scale = (H - PAD * 2) / card.height
        size = (round(card.width * scale), round(card.height * scale))
        card = card.resize(size, Image.LANCZOS)
        canvas.paste(card, ((W - size[0]) // 2, (H - size[1]) // 2))

    canvas.save(TARGET, "PNG", optimize=True)
    print(f"wrote {TARGET.relative_to(ROOT)}  {W}x{H}  {TARGET.stat().st_size/1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
