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
import json
import re
import socket
import sys
import urllib.request
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


def resolves(host, attempts=4):
    """Does this host exist? Returns (ok, how).

    **A positive answer is proof; a negative one is only weak evidence.** That
    asymmetry is the whole design. A resolver cannot invent an A record, so one
    yes settles it. A no can simply be a cached denial that has not expired —
    and on a freshly registered domain that is the normal case, not an edge one.

    Two things make the stale denial long-lived here. This machine caches the
    NXDOMAIN it got while the domain did not exist, for as long as the SOA
    minimum says (an hour for penguinpebbling.app). And `.app` is DNSSEC-signed,
    so the denial is *authenticated* and public resolvers cache it confidently —
    observed live on this domain, with consecutive queries to Cloudflare
    returning Status 3 and Status 0 seconds apart as different edge nodes
    expired it at different times.

    So: ask the local resolver, then Cloudflare, then Google, and keep asking
    until something says yes. Conclude "no" only when every attempt said no.
    Network failure is reported as unknown rather than absence.
    """
    try:
        socket.gethostbyname(host)
        return True, "local resolver"
    except socket.gaierror:
        pass

    providers = [
        ("1.1.1.1", "https://cloudflare-dns.com/dns-query"),
        ("8.8.8.8", "https://dns.google/resolve"),
    ]
    reached = False
    for attempt in range(attempts):
        for name, endpoint in providers:
            req = urllib.request.Request(
                f"{endpoint}?name={host}&type=A",
                headers={"Accept": "application/dns-json"},
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.load(r)
            except Exception:
                continue
            reached = True
            if any(a.get("type") == 1 for a in data.get("Answer", [])):
                note = f"{name}, attempt {attempt + 1}"
                if attempt:
                    note += " (earlier attempts hit a cached denial)"
                return True, f"{note}; this machine's resolver still has a stale negative cache"

    if not reached:
        return None, "local resolver says no; could not reach any public resolver to confirm"
    return False, f"local resolver and {len(providers)} public resolvers all say no, over {attempts} attempts"


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
    ok, how = resolves(host)
    if ok:
        print(f"\n{host} resolves — via {how}. Consistent.")
        return 0
    if ok is None:
        print(f"\n{host}: UNKNOWN — {how}")
        return 2
    print(f"\n{host} DOES NOT RESOLVE ({how}).")
    print("A canonical link pointing at a dead domain tells search engines to")
    print("index a URL that does not exist, which can drop the page entirely.")
    return 2


def apply(new: str) -> int:
    new = new.rstrip("/")
    if new not in KNOWN:
        print(f"Add {new} to KNOWN in this script first, so a later run can find it.")
        return 2
    host = urlparse(new).hostname
    ok, how = resolves(host)
    if ok is None:
        print(f"Refusing: cannot confirm {host} exists — {how}")
        print("Re-run when the network is available.")
        return 2
    if not ok:
        print(f"Refusing: {host} does not resolve ({how}). Register the domain and")
        print("let DNS propagate first — pointing the canonical at it early is the")
        print("bug this script exists to prevent.")
        return 2
    print(f"{host} resolves — via {how}.")

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
