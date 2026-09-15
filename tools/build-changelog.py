#!/usr/bin/env python3
"""Render CHANGELOG.md into the body of changelog.html.

CHANGELOG.md is the source. The page is generated from it so the two cannot drift
— the same reason tools/sync-shell.py owns the nav.

**This understands a deliberately small dialect of Markdown**, because a
changelog only needs one: `##` and `###` headings, `-` bullets, paragraphs, and
inline `**bold**`, `*italic*`, `` `code` `` and `[links](url)`. Anything else is
a hard error rather than a silent drop. A renderer that quietly swallows a line
it does not understand is the worst kind for a document whose whole job is being
a complete record — you would not find out from the page, because the page would
look fine.

    python3 tools/build-changelog.py
    python3 tools/build-changelog.py --check   # report drift, write nothing
"""
import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CHANGELOG.md"
PAGE = ROOT / "changelog.html"
BEGIN = "  <!-- changelog:begin — generated from CHANGELOG.md by tools/build-changelog.py -->"
END = "  <!-- changelog:end -->"

INLINE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`")


def inline(text, lineno):
    """Escape, then re-introduce only the inline markup we allow."""
    out, pos = [], 0
    for m in INLINE.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        label, url, bold, em, code = m.groups()
        if url is not None:
            if not url.startswith(("https://", "http://", "/", "#")):
                sys.exit(f"line {lineno}: link target {url!r} is not absolute or root-relative")
            out.append(f'<a href="{html.escape(url, quote=True)}">{inline(label, lineno)}</a>')
        elif bold is not None:
            out.append(f"<strong>{inline(bold, lineno)}</strong>")
        elif em is not None:
            out.append(f"<em>{inline(em, lineno)}</em>")
        else:
            out.append(f"<code>{html.escape(code)}</code>")
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def render(md):
    lines = md.splitlines()
    body, in_list = [], False

    def close_list():
        nonlocal in_list
        if in_list:
            body.append("    </ul>")
            in_list = False

    for n, raw in enumerate(lines, 1):
        line = raw.rstrip()
        if not line:
            close_list()
            continue
        if line.startswith("# "):
            continue  # the page supplies its own <h1>
        if line.startswith("### "):
            close_list()
            body.append(f"    <h3>{inline(line[4:], n)}</h3>")
        elif line.startswith("## "):
            close_list()
            date = line[3:].strip()
            anchor = re.sub(r"[^0-9a-z-]", "-", date.lower())
            body.append(f'    <h2 id="{anchor}">'
                        f'<time datetime="{html.escape(date, quote=True)}">{inline(date, n)}</time></h2>')
        elif line.startswith("- "):
            if not in_list:
                body.append("    <ul>")
                in_list = True
            body.append(f"      <li>{inline(line[2:], n)}</li>")
        elif line.startswith(("#", ">", "    ", "\t", "|", "1. ")):
            sys.exit(f"line {n}: {line[:48]!r} uses Markdown this renderer does not "
                     f"handle. Add support for it here rather than leaving it out of the page.")
        else:
            close_list()
            body.append(f"    <p>{inline(line, n)}</p>")
    close_list()
    return "\n".join(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()

    if not PAGE.exists():
        sys.exit(f"{PAGE.name} does not exist yet — create it with the marker comments first")

    rendered = render(SOURCE.read_text(encoding="utf-8"))
    page = PAGE.read_text(encoding="utf-8")
    if BEGIN not in page or END not in page:
        sys.exit(f"{PAGE.name} is missing its changelog:begin / changelog:end markers")

    head, rest = page.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    updated = head + BEGIN + "\n" + rendered + "\n" + END + tail

    if updated == page:
        print("changelog.html already matches CHANGELOG.md")
        return 0
    if args.check:
        print("changelog.html is out of date with CHANGELOG.md. Run without --check.")
        return 1
    PAGE.write_text(updated, encoding="utf-8")
    entries = rendered.count("<h2 ")
    print(f"changelog.html rebuilt — {entries} dated entr{'y' if entries == 1 else 'ies'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
