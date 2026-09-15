#!/usr/bin/env python3
"""Point the site at an origin, everywhere at once.

The site's own address is written into six places across three files: the
canonical link, og:url, og:image, the JSON-LD `url` and `license`, the Sitemap
line in robots.txt, and the <loc> in sitemap.xml. There is no build step to
derive them from one constant, so without this they get changed by hand and one
gets missed — and the one that gets missed is usually the canonical, which is the
single worst one to point at a domain that does not resolve.

    python3 tools/set-domain.py --check
    python3 tools/set-domain.py https://penguinpebbling.app

`--check` reports the current origin and whether it is consistent, and writes
nothing. Run it after the domain is registered and DNS resolves — not before.
"""
import argparse
import re
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
FILES = ["index.html", "robots.txt", "sitemap.xml"]

# Every origin this site has ever been addressed by. A new one is added here the
# first time it is used, so the rewrite can always find what it is replacing.
KNOWN = [
    "https://penguinpebbling.app",
    "https://penguin-pebbling.netlify.app",
]
ORIGIN_RX = re.compile("|".join(re.escape(o) for o in KNOWN))


def current():
    found = {}
    for name in FILES:
        text = (ROOT / name).read_text(encoding="utf-8")
        for origin in set(ORIGIN_RX.findall(text)):
            found.setdefault(origin, []).append(name)
    return found


def check() -> int:
    found = current()
    if not found:
        print("No known origin found in any file — has KNOWN drifted?")
        return 2
    for origin, files in sorted(found.items()):
        print(f"{origin}  in  {', '.join(sorted(files))}")
    if len(found) > 1:
        print("\nINCONSISTENT: the files disagree about where this site lives.")
        return 2
    origin = next(iter(found))
    host = urlparse(origin).hostname
    try:
        socket.gethostbyname(host)
        print(f"\n{host} resolves. Consistent.")
        return 0
    except socket.gaierror:
        print(f"\n{host} DOES NOT RESOLVE.")
        print("A canonical link pointing at a dead domain tells search engines to")
        print("index a URL that does not exist, which can drop the page entirely.")
        return 2


def apply(new: str) -> int:
    new = new.rstrip("/")
    if new not in KNOWN:
        print(f"Add {new} to KNOWN in this script first, so a later run can find it.")
        return 2
    host = urlparse(new).hostname
    try:
        socket.gethostbyname(host)
    except socket.gaierror:
        print(f"Refusing: {host} does not resolve yet. Register the domain and let")
        print("DNS propagate first — pointing the canonical at it early is the bug")
        print("this script exists to prevent.")
        return 2

    changed = 0
    for name in FILES:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        updated, n = ORIGIN_RX.subn(new, text)
        if n:
            path.write_text(updated, encoding="utf-8")
            print(f"{name}: {n} replaced")
            changed += n
    print(f"\n{changed} references now point at {new}")
    print("Remember to update the Netlify custom domain and redeploy.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("origin", nargs="?", help="e.g. https://penguinpebbling.app")
    p.add_argument("--check", action="store_true", help="report only, write nothing")
    a = p.parse_args()
    if a.check or not a.origin:
        return check()
    return apply(a.origin)


if __name__ == "__main__":
    raise SystemExit(main())
