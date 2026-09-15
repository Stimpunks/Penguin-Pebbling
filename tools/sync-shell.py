#!/usr/bin/env python3
"""Keep the nav and footer identical across every page.

The site is six hand-authored HTML files with no build step, and the nav and
footer appear in all six. Left alone that is six copies of one thing, which
drifts — a link added to the menu on one page and not the others, or a page that
still claims to be the current one after being renamed. The failure is quiet:
every page still renders.

So index.html holds the canonical copy of each shared block, marked off by
`<!-- shell:nav -->` / `<!-- /shell:nav -->` and the same for `footer`, and this
stamps them into the other pages — setting `aria-current="page"` on whichever
link points at the page being written, and dropping the "Play the game" button
from index.html itself, since it is already there.

    python3 tools/sync-shell.py --check   # report drift, write nothing
    python3 tools/sync-shell.py           # stamp index.html's copy into the rest

Edit the nav in index.html, then run it.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = "index.html"
PAGES = ["index.html", "how-to-play.html", "locutions.html", "print.html",
         "about.html", "changelog.html", "privacy.html"]

# Pages deliberately reached from the footer rather than the Menu. They still get
# the shell stamped — that is the whole point — they just have no nav link to mark
# as current. A privacy notice belongs in the footer, and keeping it out of the
# Menu leaves the six-item game nav as it was designed.
FOOTER_ONLY = {"privacy.html"}
BLOCKS = ["nav", "footer"]

CTA = '\n      <a class="topbar-cta" href="index.html">Play the game</a>'


def block_re(name):
    return re.compile(
        r"(?P<open><!-- shell:%s\b.*?-->)(?P<body>.*?)(?P<close><!-- /shell:%s -->)" % (name, name),
        re.S,
    )


def extract(text, name):
    m = block_re(name).search(text)
    if not m:
        sys.exit(f"{SOURCE} is missing its <!-- shell:{name} --> block")
    return m.group("body")


def localise(body, page, name):
    """Adjust the canonical block for one page."""
    if name != "nav":
        return body
    # exactly one link may claim to be the current page
    body = re.sub(r'\s+aria-current="page"', "", body)
    pattern = r'(<a href="%s")' % re.escape(page)
    if not re.search(pattern, body):
        # Still an error for a normal page: this is what catches a nav link left
        # behind by a rename, which would otherwise lose aria-current silently.
        if page not in FOOTER_ONLY:
            sys.exit(f"nav has no link to {page} — add one in {SOURCE} before syncing")
    else:
        body = re.sub(pattern, r'\1 aria-current="page"', body, count=1)
    # the "Play the game" button is pointless on the game page
    body = body.replace(CTA, "")
    if page != SOURCE:
        body = body.replace("</details>", "</details>" + CTA, 1)
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()

    src = (ROOT / SOURCE).read_text(encoding="utf-8")
    canonical = {name: extract(src, name) for name in BLOCKS}

    # every nav link must point at a file that exists
    for href in re.findall(r'<a href="([^"#:]+\.html)"', canonical["nav"]):
        if not (ROOT / href).exists():
            sys.exit(f"nav links to {href}, which does not exist")

    drifted, written = [], []
    for page in PAGES:
        path = ROOT / page
        if not path.exists():
            sys.exit(f"{page} is listed in PAGES but not on disk")
        text = original = path.read_text(encoding="utf-8")
        for name in BLOCKS:
            want = localise(canonical[name], page, name)
            m = block_re(name).search(text)
            if not m:
                sys.exit(f"{page} is missing its <!-- shell:{name} --> block")
            if m.group("body") != want:
                drifted.append(f"{page}:{name}")
            text = block_re(name).sub(
                lambda mm: mm.group("open") + want + mm.group("close"), text, count=1
            )
        if text != original and not args.check:
            path.write_text(text, encoding="utf-8")
            written.append(page)

    if args.check:
        if drifted:
            print("drifted: " + ", ".join(drifted))
            print(f"\n{len(drifted)} block(s) differ from {SOURCE}. Run without --check.")
            return 1
        print(f"nav and footer match {SOURCE} in all {len(PAGES)} pages.")
        return 0

    print(f"updated: {', '.join(written)}" if written else "already in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
