#!/usr/bin/env python3
"""Generate favicon.ico and icon-maskable.png from apple-touch-icon.png.

Two gaps, both cheap, both derived from one source so the three pebbles cannot
end up being three different drawings.

**favicon.ico** is the fallback for browsers that do not take the SVG, and for
everything that fetches /favicon.ico without being told to — feed readers, link
unfurlers, bookmark managers, the odd crawler. It was a 404 until now. Three
sizes in one file: 16 for the tab, 32 for the bookmark bar, 48 for Windows.

**icon-maskable.png** is the Android home-screen icon. Android crops an installed
icon to whatever shape the launcher uses — circle, squircle, teardrop — and an
icon that does not declare `purpose: "maskable"` gets shrunk into a white
rounded square rather than filling the shape. A maskable icon has to keep
everything that matters inside the safe zone: a circle of 80% of the icon's
width, because the corners are what the crop takes. The pebbles are scaled to
58% and centred, which leaves them inside that circle even on the most
aggressive mask.

The background is sampled from the source's own corner rather than named here,
so if the icon is ever redrawn on a different ground this follows it instead of
framing it in the old colour.

apple-touch-icon.png is the source because it is already the rasterised brand
mark at a decent size; favicon.svg is the same drawing in vector, and deriving
from the raster keeps one lineage rather than reproducing the geometry in Python
and letting the two drift.

Re-run after changing apple-touch-icon.png:  python3 tools/make-icons.py
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is not installed. Run: python3 -m pip install --upgrade Pillow")

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "apple-touch-icon.png"
ICO = ROOT / "favicon.ico"
MASKABLE = ROOT / "icon-maskable.png"

ICO_SIZES = [(16, 16), (32, 32), (48, 48)]
MASK_PX = 512
# Android's safe zone is a circle of 80% of the width. 58% leaves the drawing
# inside it with room to spare, which is the right way round to be wrong.
MASK_SCALE = 0.58


def main() -> int:
    if not SOURCE.exists():
        sys.exit(f"Missing source icon: {SOURCE}")

    with Image.open(SOURCE) as src:
        src = src.convert("RGB")

        src.save(ICO, format="ICO", sizes=ICO_SIZES)

        ground = src.getpixel((0, 0))
        canvas = Image.new("RGB", (MASK_PX, MASK_PX), ground)
        side = round(MASK_PX * MASK_SCALE)
        art = src.resize((side, side), Image.LANCZOS)
        offset = (MASK_PX - side) // 2
        canvas.paste(art, (offset, offset))
        canvas.save(MASKABLE, format="PNG", optimize=True)

    print(f"favicon.ico        {ICO.stat().st_size:>6,} bytes  "
          f"({', '.join(f'{w}x{h}' for w, h in ICO_SIZES)})")
    print(f"icon-maskable.png  {MASKABLE.stat().st_size:>6,} bytes  "
          f"({MASK_PX}x{MASK_PX}, art at {MASK_SCALE:.0%} on #{'%02x%02x%02x' % ground})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
