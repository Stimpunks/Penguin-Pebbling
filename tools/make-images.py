#!/usr/bin/env python3
"""Generate the web copies of the five locution cards from the print masters.

`cards/print/*.png` are Helen's originals at 1748x1240 — roughly A5 landscape at
300dpi, and the resolution you want if you are printing a deck. They are also
~770 KB each, so the masters stay in the repository as the source of truth and
this writes display copies next to them: WebP at 1280px wide.

**Only the five locution cards, since the deck was re-set as text.** This used to
convert all thirty-five masters, because the game drew the thirty prompt cards as
pictures. It does not any more: the prompt, the locution name and the aside are
text, and the only artwork on a card is the illustration that
tools/make-card-art.py cuts out — one per locution, not one per card. The thirty
prompt-card WebPs went on being regenerated, and deployed, and referenced by
nothing, for as long as nobody looked. They are gone.

The five that remain are the whole cards shown on locutions.html, which is still
a page of pictures and is right to be: there the card IS the subject.

The thirty prompt masters stay in `cards/print/`. They are the printable deck and
the source tools/make-card-art.py cuts the illustrations out of — deleting a
derivative is not deleting an original.

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
    masters = sorted(SRC.glob("*-locution.png"))
    if len(masters) != 5:
        sys.exit(f"Expected 5 locution masters in {SRC}, found {len(masters)}. "
                 f"Fix this rather than publishing a short set.")

    # A prompt-card WebP here is a leftover from before the re-set: nothing links
    # one, and leaving it would quietly ship 1.5 MB and confuse the next reader
    # into thinking the game still fetches them.
    stale = [p for p in OUT.glob("*.webp") if not p.stem.endswith("-locution")]
    for p in stale:
        p.unlink()

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
    print(f"{written} written, {skipped} already current"
          + (f", {len(stale)} stale removed" if stale else ""))
    print(f"5 locution masters {before/1e6:.1f} MB -> web {after/1e6:.1f} MB "
          f"({after/before:.0%} of original)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
