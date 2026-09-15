#!/usr/bin/env python3
"""Publish the deck's text at /search-index.json, for readers that cannot run the game.

The thirty prompts live in penguin-pebbling.js and are drawn into the page by
script. That is fine for a browser and invisible to everything else: an archiver,
a search engine, or our own site mirror fetching the page gets the game's
furniture — headings, filter labels, "Press Draw a card to begin" — and not one
word of the deck. The page looks mirrored and its substance is missing.

Star Stuff hit this first, with field guides that build their entries
client-side, and the fix there is the one used here: the site publishes its own
extracted text, and `static_content.py` appends whatever the static render did
not already contain. The shape below is that contract —

    {"v": 1,
     "pages": [[filename, title], ...],
     "recs":  [[page_index, fragment, heading, text], ...]}

— and the knowledge system's sync reads it by `entry_index` in its SITES map.

Only index.html needs this. Every other page's prose is in its own HTML, so a
fetch of <main> already gets it.

Generated from penguin-pebbling.js so the index cannot drift from the deck:
re-run after changing a prompt.

    python3 tools/make-search-index.py
    python3 tools/make-search-index.py --check   # report drift, write nothing
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK_JS = ROOT / "penguin-pebbling.js"
OUT = ROOT / "search-index.json"

CARD = re.compile(
    r"\{\s*locution:\s*\"(?P<loc>[^\"]+)\",\s*"
    r"name:\s*\"(?P<name>[^\"]+)\",\s*"
    r"image:\s*\"(?P<image>[^\"]+)\",\s*"
    r"prompt:\s*\"(?P<prompt>(?:[^\"\\]|\\.)*)\",\s*"
    r"aside:\s*(?P<aside>null|\"(?:[^\"\\]|\\.)*\")\s*\}"
)


def cards():
    js = DECK_JS.read_text(encoding="utf-8")
    found = []
    for m in CARD.finditer(js):
        prompt = json.loads('"%s"' % m.group("prompt"))
        aside = None if m.group("aside") == "null" else json.loads(m.group("aside"))
        found.append((m.group("name"), prompt, aside))
    return found


def build():
    found = cards()
    if len(found) != 30:
        sys.exit(f"Expected 30 cards in {DECK_JS.name}, parsed {len(found)}. "
                 f"The deck or the regex changed — fix this before publishing a short index.")
    recs = []
    for name, prompt, aside in found:
        text = prompt if not aside else f"{prompt}\n\n{aside}"
        recs.append([0, "#game", name, text.replace("\n", " ").strip()])
    return {
        "v": 1,
        "pages": [["index.html", "Penguin Pebbling"]],
        "recs": recs,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()

    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"

    if OUT.exists() and OUT.read_text(encoding="utf-8") == text:
        print(f"search-index.json already matches the deck ({len(data['recs'])} prompts)")
        return 0
    if args.check:
        print("search-index.json is out of date with penguin-pebbling.js. Run without --check.")
        return 1
    OUT.write_text(text, encoding="utf-8")
    print(f"search-index.json written — {len(data['recs'])} prompts, "
          f"{sum(len(r[3]) for r in data['recs'])} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
