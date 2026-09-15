#!/usr/bin/env python3
"""Publish /llms.txt — a short, curated map of this site for language models.

`llms.txt` is a convention, not a ratified standard: markdown at the site root
naming the pages that matter, in the order they matter. It is not robots.txt and
controls nothing — listing a page does not open it and omitting one does not
protect it. Access policy lives in robots.txt; this is an index and an
invitation.

It earns its place here for the same reason `search-index.json` does, and the
reason is unusually stark on this site: **the thirty card prompts are the game,
they live in penguin-pebbling.js, and not one of them appears in any HTML.**
Anything that reads the front page without running scripts gets the furniture and
none of the deck. So this file says so, in prose, and points at the JSON.

v2 of the convention dropped the guess-the-path behaviour in favour of a link
relation, so shipping the file is only half of it: `_headers` sends

    Link: </llms.txt>; rel="describedby"; type="text/markdown"

on every response, which is what reaches an agent that never parses the HTML.
A file nothing advertises is found only by something that already assumed the
path, which is the failure v2 set out to fix.

Generated, because the fastest way to make this file worse than useless is to let
it drift: a stale index teaches a model the wrong things confidently. Every title
and one-line summary below is read out of the page's own <title> and
<meta name="description">, every URL out of its <link rel="canonical">, and the
card count out of the deck itself — so the only thing hand-maintained here is
which pages belong in which section, which is the one part that is a judgement.

    python3 tools/make-llms-txt.py
    python3 tools/make-llms-txt.py --check   # report drift, write nothing
"""
import argparse
import html
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "llms.txt"
PRINT_PAGE = ROOT / "print.html"

# Which pages go where. The only editorial decision in this file: the sections
# and their order. Everything else is read off the pages themselves.
SECTIONS = [
    ("The game", ["index.html", "how-to-play.html", "locutions.html", "print.html"]),
    ("Optional", ["about.html", "changelog.html", "privacy.html"]),
]

# The blockquote above is built from index.html's own <meta name="description">,
# so letting the front page repeat it in the list says the same sentence twice.
# These two override what is read off the page, and they are the only prose in
# this file that is not generated — the front page needs a line about the *page*
# rather than about the site.
OVERRIDE = {
    "index.html": {
        "title": "Penguin Pebbling",
        "desc": "The game itself. Draw a card, filter by locution, pass a pebble. "
                "This is the page the prompts are rendered into, and the reason the "
                "JSON above exists.",
    },
}

TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESC = re.compile(r'<meta name="description" content="(.*?)">', re.S)
CANON = re.compile(r'<link rel="canonical" href="(.*?)">')
PDF = re.compile(r'<a class="btn-download" href="(downloads/[^"]+\.pdf)">(.*?)</a>')


def deck_size():
    """Count the cards using make-search-index.py's parser, not a second copy of it.

    Two regexes over the same deck is exactly the drift this repository keeps
    writing tools to avoid, and the sibling tool's is already the strict one.
    """
    path = ROOT / "tools" / "make-search-index.py"
    spec = importlib.util.spec_from_file_location("make_search_index", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return len(mod.cards())


def read(page):
    text = (ROOT / page).read_text(encoding="utf-8")
    out = {}
    for key, rx in (("title", TITLE), ("desc", DESC), ("url", CANON)):
        m = rx.search(text)
        if not m:
            sys.exit(f"{page} has no {key} — llms.txt cannot describe a page that does not describe itself")
        out[key] = html.unescape(" ".join(m.group(1).split()))
    # "Print & download — Penguin Pebbling" reads as "Print & download" in a list
    # that is already under the site's own heading.
    out["title"] = out["title"].split(" — Penguin Pebbling")[0]
    # Keep what the page says about itself before any override: the blockquote is
    # the site summary and must stay the front page's own meta description, while
    # the list entry below it describes the page.
    out["site_desc"] = out["desc"]
    out.update(OVERRIDE.get(page, {}))
    return out


def downloads():
    text = PRINT_PAGE.read_text(encoding="utf-8")
    found = []
    for href, label in PDF.findall(text):
        label = html.unescape(" ".join(label.split()))
        label = re.sub(r"^Download the ", "", label)
        found.append((href, label[0].upper() + label[1:]))
    if len(found) != 3:
        sys.exit(f"Expected 3 PDFs linked from {PRINT_PAGE.name}, found {len(found)}. "
                 f"Fix this rather than publishing an index that omits one.")
    return found


def build():
    n = deck_size()
    if n != 30:
        sys.exit(f"Parsed {n} cards, expected 30. Fix the deck or the parser before "
                 f"telling a model how big this game is.")

    pages = {p: read(p) for _, group in SECTIONS for p in group}
    origin = pages["index.html"]["url"].rstrip("/")

    L = []
    L.append("# Penguin Pebbling")
    L.append("")
    L.append(f"> {pages['index.html']['site_desc']}")
    L.append("")
    L.append("A neuro-affirming card game about belonging, connection and Autistic identity, built "
             "around the Five Autistic Love Locutions: infodumping, parallel play, support swapping, "
             "deep pressure, and penguin pebbling itself. Developed by Helen Edgar (Autistic Realms) "
             "and Ryan Boren (Stimpunks), 2026. Licensed CC BY-NC-SA 4.0 "
             "(https://creativecommons.org/licenses/by-nc-sa/4.0/) — free to use, share and adapt for "
             "non-commercial purposes, with credit, a link back, and the same licence on "
             "anything built from it.")
    L.append("")
    L.append(f"**The {n} card prompts appear in no HTML.** They live in `penguin-pebbling.js` and are "
             f"drawn into the page by script, so fetching the front page gets the game's furniture and "
             f"none of the deck. The prompts are published as JSON instead — fetch that rather than "
             f"scraping the game.")
    L.append("")
    L.append("## The deck")
    L.append("")
    L.append(f"- [All {n} card prompts, as JSON]({origin}/search-index.json): every prompt with its "
             f"locution and card name. This is the game's actual content.")
    L.append("")

    for heading, group in SECTIONS:
        L.append(f"## {heading}")
        L.append("")
        for page in group:
            p = pages[page]
            L.append(f"- [{p['title']}]({p['url']}): {p['desc']}")
        L.append("")

    L.append("## Downloads")
    L.append("")
    for href, label in downloads():
        L.append(f"- [{label}]({origin}/{href})")
    L.append("")

    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()

    text = build()
    if OUT.exists() and OUT.read_text(encoding="utf-8") == text:
        print("llms.txt already matches the site")
        return 0
    if args.check:
        print("llms.txt is out of date with the pages. Run without --check.")
        return 1
    OUT.write_text(text, encoding="utf-8")
    print(f"llms.txt written — {len(text.splitlines())} lines, "
          f"{sum(len(g) for _, g in SECTIONS)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
