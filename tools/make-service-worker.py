#!/usr/bin/env python3
"""Generate sw.js — the service worker that makes the game work with no network.

The game is played in groups, in classrooms and clinics and community rooms, on
whatever wifi is there. The deck, the rules, the locutions and the guides should
not depend on that. This site is the easy case for it: nothing loads from a third
party, so there is nothing external to be offline *from*.

**The precache list is derived, never typed.** Pages come from sitemap.xml, the
rest from globs. A hand-kept list is the same quiet failure sync-shell.py and
set-domain.py exist to prevent — a new page would simply be missing offline, with
nothing to notice it. A new page already has to be registered in four places; it
must not become five.

**The cache name carries a hash of everything in it.** Change any precached byte
and the name changes, the new worker installs a new cache and deletes the old
one. There is no partial upgrade to reason about.

## What is NOT precached, and why

- `downloads/*.pdf` — 7.3 MB against 670 KB for everything else. Cached when
  someone actually opens one, which is the case that matters: whoever reads the
  Easy Read guide once keeps it.
- `og-image.png` — 311 KB that only ever unfurls a link. Useless offline.
- `cards/*-[1-6].webp` — the prompt-card derivatives the re-set left behind.
  Nothing references them.
- `feed.xml` — read by a feed reader, which is a different program on a
  different schedule and never passes through this worker. Nobody browsing
  offline needs the changelog in RSS when the changelog page itself is held.

## The strategy, and why it is not the usual one

Cache-first is the normal advice and it is wrong for this site. `_headers`
deliberately revalidates the HTML, the stylesheet and the scripts, because a
stale stylesheet against fresh markup renders the page wrong — that is written
up in commit 15bc1bd, which exists because it happened. A cache-first worker
turns that one-day bug into a permanent one, and stuck-on-an-old-version is the
most common way a service worker hurts a site.

So documents, CSS and JS are **network-first**: the network wins whenever there
is one, and the cache is the fallback rather than the source. Fonts, card art
and icons are **cache-first**, because their bytes only change when their
generator runs and the cache name changes with them.

    python3 tools/make-service-worker.py
    python3 tools/make-service-worker.py --check   # report drift, write nothing
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sw.js"
SITEMAP = ROOT / "sitemap.xml"

# Globs for everything that is not a page. Order is cosmetic; the list is sorted.
ASSET_GLOBS = [
    "penguin-pebbling.css", "penguin-pebbling.js", "theme.js",
    "fonts/*.woff2",
    "cards/art/*.webp",
    "cards/*-locution.webp",
    "favicon.svg", "favicon.ico", "apple-touch-icon.png", "icon-maskable.png",
    "site.webmanifest", "search-index.json", "llms.txt",
]
EXTRA_PAGES = ["404.html"]


def pages():
    """Every URL a page can be reached at — BOTH forms, deliberately.

    Netlify's Pretty URLs serve /how-to-play and rewrite the markup to match, so
    in production that is what a navigation requests. The hrefs in this
    repository are how-to-play.html, and locally nothing rewrites them, so that
    is what a navigation requests there. Production also still serves the .html
    form to anyone who has the link.

    Precaching one form only looks fine and fails completely: the worker installs,
    reports every URL held, and then the first offline navigation asks for the
    address nobody cached. Found exactly that way — the local site went blank with
    32 of 32 entries "held".

    Both forms it is. The duplicate is ~10 KB of HTML and install tolerates the
    one that 404s on whichever server is not rewriting.
    """
    xml = SITEMAP.read_text(encoding="utf-8")
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
    if not locs:
        sys.exit("sitemap.xml lists no <loc> — cannot derive the page list")
    out = set()
    for u in locs:
        path = re.sub(r"^https?://[^/]+", "", u) or "/"
        out.add(path)
        out.add("/index.html" if path == "/" else path + ".html")
    return sorted(out)


def assets():
    found = []
    for pattern in ASSET_GLOBS:
        hits = sorted(ROOT.glob(pattern))
        if not hits:
            sys.exit(f"nothing matched {pattern!r} — the precache would be short")
        found += ["/" + h.relative_to(ROOT).as_posix() for h in hits]
    for name in EXTRA_PAGES:
        if not (ROOT / name).exists():
            sys.exit(f"{name} is listed but not on disk")
        found.append("/" + name)
    return sorted(set(found))


def version(asset_paths):
    """A hash of every precached byte on disk, plus this file, plus `_headers`.

    The pages are hashed through their .html sources rather than their served
    URLs — the bytes are the same and the file is what we have.

    `_headers` is in there for a reason that cost a deploy. A browser decides
    whether to install a new worker by comparing the script BYTE FOR BYTE; the
    response headers are not part of that comparison. But the worker's own
    fetches are governed by the CSP on that response, so a CSP fix changes what
    the worker can do while changing nothing it is judged by — every browser
    keeps the old worker, still bound by the old policy, and the fix never
    arrives. Hashing `_headers` into the version makes a policy change a script
    change, which is the only thing that actually forces the update.
    """
    h = hashlib.sha256()
    h.update(Path(__file__).read_bytes())
    h.update((ROOT / "_headers").read_bytes())
    for p in asset_paths:
        h.update((ROOT / p.lstrip("/")).read_bytes())
    for html in sorted(ROOT.glob("*.html")):
        h.update(html.read_bytes())
    return h.hexdigest()[:12]


TEMPLATE = """/* Generated by tools/make-service-worker.py — do not edit by hand.
 *
 * Offline support for Penguin Pebbling. The whole site is about 670 KB, so it is
 * all held except the PDFs, which are cached when someone opens one.
 *
 * Documents, CSS and JS are network-first on purpose. `_headers` revalidates
 * them on every request because a stale stylesheet against fresh markup renders
 * the page wrong — see commit 15bc1bd, which exists because that happened. A
 * cache-first worker would make that permanent instead of lasting a day, and
 * being stuck on an old version is the usual way a service worker hurts a site.
 * The cache is the fallback here, never the source.
 */
const VERSION = "%(version)s";
const CACHE = "penguin-pebbling-" + VERSION;

const PRECACHE = %(precache)s;

/* Cache-first: these only change when their generator runs, and when they do the
 * cache name changes with them. */
const IMMUTABLE = /^\\/(fonts\\/|cards\\/|favicon|apple-touch-icon|icon-maskable)/;

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    /* Individually, not addAll: addAll is atomic, so one URL that 404s on a dev
     * server without clean URLs would abort the install and leave the site with
     * no worker at all. A missing entry just falls through to the network. */
    await Promise.allSettled(PRECACHE.map((url) => cache.add(url)));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names
      .filter((n) => n.startsWith("penguin-pebbling-") && n !== CACHE)
      .map((n) => caches.delete(n)));
    await self.clients.claim();
  })());
});

async function networkFirst(request) {
  const cache = await caches.open(CACHE);
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch (err) {
    const hit = await cache.match(request);
    if (hit) return hit;
    throw err;
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(request);
  if (hit) return hit;
  const fresh = await fetch(request);
  if (fresh && fresh.ok) cache.put(request, fresh.clone());
  return fresh;
}

const OFFLINE_BODY = `<!doctype html><html lang="en-GB"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Offline \\u2014 Penguin Pebbling</title>
<link rel="stylesheet" href="/penguin-pebbling.css">
<div class="wrap"><main class="prose" style="padding-block:3rem">
<h1>This part needs a connection</h1>
<p>The game, the rules, the five locutions and the printable page all work
offline. This particular thing was not saved to your device \\u2014 the PDF guides are
only kept once you have opened them.</p>
<p><a href="/">Back to the game</a></p>
</main></div>`;

function offline() {
  return new Response(OFFLINE_BODY, {
    status: 503,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  /* A PDF link has no download attribute, so opening one is a navigation and
   * lands here. Online it is fetched and kept; offline, and not already kept,
   * the reader gets a sentence rather than the browser's error page. */
  if (request.mode === "navigate") {
    event.respondWith(networkFirst(request).catch(async () => {
      const cache = await caches.open(CACHE);
      return (await cache.match(request))
        || (await cache.match("/404.html"))
        || offline();
    }));
    return;
  }

  if (IMMUTABLE.test(url.pathname)) {
    event.respondWith(cacheFirst(request).catch(() => offline()));
    return;
  }

  event.respondWith(networkFirst(request).catch(() => offline()));
});
"""


def build():
    precache = pages() + assets()
    body = "[\n" + "".join(f'  "{u}",\n' for u in precache) + "]"
    return TEMPLATE % {"version": version(assets()), "precache": body}, precache


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()

    text, precache = build()
    if OUT.exists() and OUT.read_text(encoding="utf-8") == text:
        print(f"sw.js already matches the site ({len(precache)} precached URLs)")
        return 0
    if args.check:
        print("sw.js is out of date with the site. Run without --check.")
        return 1
    OUT.write_text(text, encoding="utf-8")
    total = sum((ROOT / p.lstrip("/")).stat().st_size
                for p in precache if (ROOT / p.lstrip("/")).exists())
    print(f"sw.js written — {len(precache)} URLs precached, "
          f"{total:,} bytes of local files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
