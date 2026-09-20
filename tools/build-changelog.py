#!/usr/bin/env python3
"""Render CHANGELOG.md into the body of changelog.html, and into feed.xml.

CHANGELOG.md is the source. Both outputs are generated from it so the three
cannot drift — the same reason tools/sync-shell.py owns the nav.

**One tool, two outputs, on purpose.** The obvious alternative was a second
script for the feed, and it would have needed its own copy of the Markdown
reader below. Two parsers over one document is precisely the failure the rest of
these tools exist to prevent: they agree on the day they are written and quietly
disagree later, and the disagreement shows up as a feed item that is missing a
sentence the page has. The page body and the feed items are rendered by the same
function here, with the same hard errors.

**This understands a deliberately small dialect of Markdown**, because a
changelog only needs one: `##` and `###` headings, `-` bullets, paragraphs, and
inline `**bold**`, `*italic*`, `` `code` `` and `[links](url)`. Anything else is
a hard error rather than a silent drop. A renderer that quietly swallows a line
it does not understand is the worst kind for a document whose whole job is being
a complete record — you would not find out from the page, because the page would
look fine.

## The feed

`/feed.xml` is RSS 2.0. One item per dated entry, newest first, each one linking
to its own anchor on the changelog page — the same anchor the `<h2>` already
carries, so the feed and the page cannot point at different things.

**Nothing in the feed is allowed to change between two runs over an unchanged
CHANGELOG.md**, which is why there is no `lastBuildDate` of "now" and no
"generated on" line. A generated file whose bytes differ every run cannot be
checked, and `--check` is how this one stays honest: it would report drift
forever and mean nothing. `lastBuildDate` is the newest entry's own date.

**A feed carries its links out of their page**, so root-relative and `#anchor`
targets are resolved against the site's own origin on the way in. The origin is
read out of changelog.html's `<link rel="canonical">` rather than typed here, so
tools/set-domain.py moves the feed with everything else. CHANGELOG.md is in that
tool's file list for the same reason: the absolute links in the prose end up in
both outputs, and rewriting only the outputs would be undone by the next run of
this script.

    python3 tools/build-changelog.py
    python3 tools/build-changelog.py --check   # report drift, write nothing
"""
import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CHANGELOG.md"
PAGE = ROOT / "changelog.html"
FEED = ROOT / "feed.xml"
BEGIN = "  <!-- changelog:begin — generated from CHANGELOG.md by tools/build-changelog.py -->"
END = "  <!-- changelog:end -->"

# Enough entries to fill a reader's list on first subscribe, without the file
# growing without limit. The page keeps everything; the feed is a notification.
MAX_ITEMS = 20

# RFC 822 names the days and months in English. strftime's %a and %b follow
# whatever locale the machine running this happens to have, which would make the
# output of a generated file depend on whose laptop generated it.
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
ABBR_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

TITLE_RX = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RX = re.compile(r'<meta name="description" content="(.*?)">', re.S)
CANON_RX = re.compile(r'<link rel="canonical" href="(.*?)">')
LANG_RX = re.compile(r'<html lang="([^"]+)"')

INLINE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`")


def inline(text, lineno, base=None):
    """Escape, then re-introduce only the inline markup we allow.

    `base`, when given, is a function that makes a link target absolute. The page
    is served at the same origin as the links, so it does not need one; the feed
    is read somewhere else entirely, where a bare /privacy resolves against the
    reader's own site.
    """
    out, pos = [], 0
    for m in INLINE.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        label, url, bold, em, code = m.groups()
        if url is not None:
            if not url.startswith(("https://", "http://", "/", "#")):
                sys.exit(f"line {lineno}: link target {url!r} is not absolute or root-relative")
            if base is not None:
                url = base(url)
            out.append(f'<a href="{html.escape(url, quote=True)}">{inline(label, lineno, base)}</a>')
        elif bold is not None:
            out.append(f"<strong>{inline(bold, lineno, base)}</strong>")
        elif em is not None:
            out.append(f"<em>{inline(em, lineno, base)}</em>")
        else:
            out.append(f"<code>{html.escape(code)}</code>")
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def render(pairs, indent="    ", base=None):
    """Render (line number, text) pairs to HTML.

    The line numbers are carried rather than recomputed so that an entry rendered
    on its own for the feed still reports errors against the real line in
    CHANGELOG.md.
    """
    body, in_list = [], False

    def close_list():
        nonlocal in_list
        if in_list:
            body.append(f"{indent}</ul>")
            in_list = False

    for n, raw in pairs:
        line = raw.rstrip()
        if not line:
            close_list()
            continue
        if line.startswith("# "):
            continue  # the page supplies its own <h1>
        if line.startswith("### "):
            close_list()
            body.append(f"{indent}<h3>{inline(line[4:], n, base)}</h3>")
        elif line.startswith("## "):
            close_list()
            d = line[3:].strip()
            anchor = re.sub(r"[^0-9a-z-]", "-", d.lower())
            body.append(f'{indent}<h2 id="{anchor}">'
                        f'<time datetime="{html.escape(d, quote=True)}">{inline(d, n, base)}</time></h2>')
        elif line.startswith("- "):
            if not in_list:
                body.append(f"{indent}<ul>")
                in_list = True
            body.append(f"{indent}  <li>{inline(line[2:], n, base)}</li>")
        elif line.startswith(("#", ">", "    ", "\t", "|", "1. ")):
            sys.exit(f"line {n}: {line[:48]!r} uses Markdown this renderer does not "
                     f"handle. Add support for it here rather than leaving it out of the page.")
        else:
            close_list()
            body.append(f"{indent}<p>{inline(line, n, base)}</p>")
    close_list()
    return "\n".join(body)


def source_lines():
    return list(enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), 1))


def entries(pairs):
    """Split the source into its dated entries, in the order they are written.

    Whatever sits above the first `## ` is the page's standing introduction. It
    belongs at the top of the page and in no feed item, so it is not collected
    here.
    """
    found = []
    for n, raw in pairs:
        line = raw.rstrip()
        if line.startswith("## "):
            found.append({"date": line[3:].strip(), "line": n, "body": []})
        elif found:
            found[-1]["body"].append((n, raw))

    if not found:
        sys.exit("CHANGELOG.md has no dated `## ` entries — the feed would have no items")

    seen = {}
    previous = None
    for e in found:
        try:
            e["day"] = date.fromisoformat(e["date"])
        except ValueError:
            sys.exit(f"line {e['line']}: heading {e['date']!r} is not a YYYY-MM-DD date. "
                     f"Every entry is one, because the page anchors it and the feed dates it.")
        if e["date"] in seen:
            # Two entries on one day would share an anchor and a feed guid, and a
            # reader dedupes on the guid — the second one would never be shown.
            sys.exit(f"line {e['line']}: {e['date']} already has an entry at line "
                     f"{seen[e['date']]}. Merge them rather than dating two entries the same day.")
        seen[e["date"]] = e["line"]
        if previous is not None and e["day"] > previous:
            sys.exit(f"line {e['line']}: {e['date']} is newer than the entry above it. "
                     f"This file is newest first, and the feed publishes it in the order it is written.")
        previous = e["day"]
    return found


def page_meta():
    """Describe the feed with what the page already says about itself.

    A hand-written channel title and description is one more pair of sentences to
    keep in step with the page, and the page's own <title>, description and
    canonical are already correct and already maintained.
    """
    text = PAGE.read_text(encoding="utf-8")
    out = {}
    for key, rx, what in (("title", TITLE_RX, "<title>"),
                          ("desc", DESC_RX, '<meta name="description">'),
                          ("url", CANON_RX, '<link rel="canonical">'),
                          ("lang", LANG_RX, "<html lang>")):
        m = rx.search(text)
        if not m:
            sys.exit(f"{PAGE.name} has no {what} — the feed is described by the page it mirrors")
        out[key] = html.unescape(" ".join(m.group(1).split()))
    parsed = urlparse(out["url"])
    if not parsed.scheme or not parsed.netloc:
        sys.exit(f"{PAGE.name}'s canonical {out['url']!r} is not absolute — a feed needs a real origin")
    out["origin"] = f"{parsed.scheme}://{parsed.netloc}"
    return out


def absolutiser(meta):
    def fix(url):
        if url.startswith("#"):
            return meta["url"] + url
        if url.startswith("/"):
            return meta["origin"] + url
        return url
    return fix


def rfc822(d):
    """A date as an RFC 822 timestamp, at midday UTC.

    A changelog entry is a day, not a moment, so the time of day is invented
    either way — but it is not arbitrary. Midnight UTC is displayed by a reader
    in Chicago as the evening before, filing a 15 September entry under the 14th.
    Midday is the choice that lands on the written date across the Americas,
    Europe and most of Asia; only the far side of the date line still sees the
    following morning, and nothing can be right everywhere at once.
    """
    return (f"{DAYS[d.weekday()]}, {d.day:02d} {ABBR_MONTHS[d.month - 1]} {d.year} "
            f"12:00:00 +0000")


def xml_text(s):
    return html.escape(s, quote=False)


def build_feed(meta, found):
    items = found[:MAX_ITEMS]
    base = absolutiser(meta)
    L = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<!-- Generated from CHANGELOG.md by tools/build-changelog.py — do not edit by hand. -->",
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{xml_text(meta['title'])}</title>",
        f"    <link>{xml_text(meta['url'])}</link>",
        f"    <description>{xml_text(meta['desc'])}</description>",
        f"    <language>{xml_text(meta['lang'])}</language>",
        "    <copyright>Helen Edgar and Ryan Boren, 2026. Licensed CC BY-NC-SA 4.0 "
        "(https://creativecommons.org/licenses/by-nc-sa/4.0/).</copyright>",
        f"    <lastBuildDate>{rfc822(items[0]['day'])}</lastBuildDate>",
        "    <generator>tools/build-changelog.py</generator>",
        f'    <atom:link href="{html.escape(meta["origin"] + "/feed.xml", quote=True)}" '
        f'rel="self" type="application/rss+xml"/>',
    ]
    for e in items:
        link = f"{meta['url']}#{e['date']}"
        body = render(e["body"], indent="", base=base)
        if "]]>" in body:
            # Cannot happen while every `>` goes through html.escape, which is why
            # this is an assertion and not an escaping routine. If it ever does,
            # the feed would end mid-item and most readers would show nothing.
            sys.exit(f"entry {e['date']} renders a ']]>' that would close the CDATA early")
        title = f"{e['day'].day} {MONTHS[e['day'].month - 1]} {e['day'].year}"
        L += [
            "    <item>",
            f"      <title>{xml_text(title)}</title>",
            f"      <link>{xml_text(link)}</link>",
            f'      <guid isPermaLink="true">{xml_text(link)}</guid>',
            f"      <pubDate>{rfc822(e['day'])}</pubDate>",
            "      <description><![CDATA[",
            body,
            "      ]]></description>",
            "    </item>",
        ]
    L += ["  </channel>", "</rss>", ""]
    return "\n".join(L)


def build_page(pairs):
    page = PAGE.read_text(encoding="utf-8")
    if BEGIN not in page or END not in page:
        sys.exit(f"{PAGE.name} is missing its changelog:begin / changelog:end markers")
    head, rest = page.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return page, head + BEGIN + "\n" + render(pairs) + "\n" + END + tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()

    if not PAGE.exists():
        sys.exit(f"{PAGE.name} does not exist yet — create it with the marker comments first")

    pairs = source_lines()
    found = entries(pairs)
    current_page, updated_page = build_page(pairs)
    feed = build_feed(page_meta(), found)

    stale = []
    if updated_page != current_page:
        stale.append(PAGE.name)
    if not FEED.exists() or FEED.read_text(encoding="utf-8") != feed:
        stale.append(FEED.name)

    if not stale:
        print(f"changelog.html and feed.xml already match CHANGELOG.md "
              f"({len(found)} dated entries)")
        return 0
    if args.check:
        print(f"{' and '.join(stale)} out of date with CHANGELOG.md. Run without --check.")
        return 1

    if PAGE.name in stale:
        PAGE.write_text(updated_page, encoding="utf-8")
    if FEED.name in stale:
        FEED.write_text(feed, encoding="utf-8")
    shown = min(len(found), MAX_ITEMS)
    print(f"{' and '.join(stale)} rebuilt — {len(found)} dated "
          f"entr{'y' if len(found) == 1 else 'ies'}, {shown} in the feed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
