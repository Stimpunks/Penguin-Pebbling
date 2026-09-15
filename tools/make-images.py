#!/usr/bin/env python3
"""Generate the web card images from the print masters.

`cards/print/*.png` are Helen's originals at 1748x1240 — roughly A5 landscape at
300dpi, and the resolution you want if you are printing a deck. They are also
~770 KB each, and the page draws one card at a time, so serving the masters
would spend 27 MB to show thirty-five pictures.

So the masters stay in the repository as the source of truth and this writes the
display copies next to them: WebP at 1280px wide, which is 2x the 640px the card
ever occupies inside the 680px column. Re-run after replacing any master.

Needs Pillow:  python3 -m pip install --upgrade Pillow
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is not installed. Run: python3 -m pip install --upgrade Pillow")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "cards" / "print"
OUT = ROOT / "cards"
WIDTH = 1280
QUALITY = 82


def main() -> int:
    masters = sorted(SRC.glob("*.png"))
    if not masters:
        sys.exit(f"No print masters found in {SRC}")

    written = skipped = 0
    for master in masters:
        target = OUT / (master.stem + ".webp")
        if target.exists() and target.stat().st_mtime >= master.stat().st_mtime:
            skipped += 1
            continue
        with Image.open(master) as im:
            im = im.convert("RGB")
            if im.width > WIDTH:
                height = round(im.height * WIDTH / im.width)
                im = im.resize((WIDTH, height), Image.LANCZOS)
            im.save(target, "WEBP", quality=QUALITY, method=6)
        written += 1

    before = sum(p.stat().st_size for p in masters)
    after = sum(p.stat().st_size for p in OUT.glob("*.webp"))
    print(f"{written} written, {skipped} already current")
    print(f"masters {before/1e6:.1f} MB -> web {after/1e6:.1f} MB "
          f"({after/before:.0%} of original)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
