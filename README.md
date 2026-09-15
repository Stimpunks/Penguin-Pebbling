# Penguin Pebbling

**A Game of Creating Belonging, Building Connection and Understanding Autistic Identity**

A neuro-affirming card game built around the Five Autistic Love Locutions — infodumping,
parallel play, support swapping, deep pressure, and penguin pebbling itself. Thirty cards,
six per locution. No winners. No wrong way to play.

Developed by **Helen Edgar** at [Autistic Realms](https://autisticrealms.com) and **Ryan Boren**
at [Stimpunks](https://stimpunks.org), 2026.

Destined for **penguinpebbling.app**, hosted on Stimpunks' Netlify.

----

## What this repository is

The game was first published as a WordPress post at Autistic Realms, with the playable part
living in a single Custom HTML block. That block turned out to contain a whole `<head>` and
`<body>` — Helen had written it as a standalone HTML page and pasted it in. This repository is
that page given its own address, with the surrounding article brought along and every asset
pulled local.

**There is no build step and no dependency to install.** It is HTML, one stylesheet, one script,
and a folder of pictures. Open `index.html` and it works; push the folder and it deploys.

```
index.html              the game, and almost nothing else
how-to-play.html        what it is, what you need, taking turns, ending a game
locutions.html          the five locution cards and a quick guide
print.html              the printable deck, Plain Language and Easy Read guides
about.html              sources, practitioners, licence, references
penguin-pebbling.css    Helen's palette and type, extended to cover the page
penguin-pebbling.js     the thirty cards and the game logic
cards/                  35 WebP images the page shows (1280px, ~50 KB each)
cards/print/            the same 35 as Helen's original PNGs (1748x1240) — print masters
downloads/              Plain Language guide, Easy Read guide, printable deck (PDF)
og-image.png            1200x630 share card, for links unfurled on social
tools/make-images.py    regenerates cards/ from cards/print/
tools/make-og-image.py  regenerates og-image.png
tools/set-domain.py     rewrites the site's own address everywhere at once
tools/sync-shell.py     keeps the nav and footer identical across the pages
tools/check-contrast.py checks every colour pair against WCAG AA
fonts/                  Atkinson Hyperlegible Next, self-hosted, with its OFL licence
netlify.toml _headers _redirects   Netlify configuration
```

**The site lives at <https://penguinpebbling.app/>.** Every self-reference is set by `tools/set-domain.py`, which moves all seven at once and refuses to point at a host it cannot confirm exists — see `DECISIONS.md` for why confirming that is harder than a name lookup.

## Nothing loads from autisticrealms.com

That was the point of the import. Every image, every PDF, the stylesheet and the script are
served from this repository. There is no webfont, no CDN, no analytics, no third-party anything
— the page renders identically with the network unplugged after first load, and the
Content-Security-Policy in `_headers` is `default-src 'none'` because nothing needs more.

**Links to Autistic Realms are a different matter and they stay.** The citations to Helen's
writing, the practitioner guide, and the shop link where the deck can be bought or donated for
are credit and livelihood, not dependencies. Removing them would be the bug.

## Working on it

Any static server will do:

```bash
python3 -m http.server 8913
```

After replacing a card image, drop the new original in `cards/print/` at the same filename and
run:

```bash
python3 tools/make-images.py
```

It rewrites only what changed and prints the size saved. Needs Pillow (`python3 -m pip install
--upgrade Pillow`) and nothing else.

## The game is the front page

Everything that explains the game lives on its own page, reachable from the **Menu** in the bar
at the top. `index.html` is the game and a short list of links, and nothing else.

It was one long page for a day, and the game sat below roughly a thousand words of introduction
and instructions — you had to scroll past the explanation to reach the thing being explained.
This follows what [cavendish.app](https://cavendish.app/) already does: a `<details>` menu in a
sticky bar, `aria-current="page"` on the link you are on, and a **Play the game** button on every
page that is not the game.

A `<details>` rather than a scripted menu, deliberately: it opens with the keyboard, is announced
as expandable, and works with JavaScript off — which matters, because the menu is how you reach
the printable deck and the Easy Read guide, and those are exactly what someone without a working
game needs.

**The nav and footer live in `index.html` and are stamped into the other pages** by
`tools/sync-shell.py`. Five hand-maintained copies of one menu is a drift problem with a quiet
failure mode — a link added in one place, a page that still claims to be current after a rename.
Edit the nav in `index.html`, then:

```bash
python3 tools/sync-shell.py          # stamp it into the rest
python3 tools/sync-shell.py --check  # report drift, write nothing
```

## Typography

The page is set in **Atkinson Hyperlegible Next**, self-hosted from `fonts/` — the Braille
Institute's typeface, drawn so the letterforms most often confused with one another stay
distinct. Body text is **1.125rem** (18px at the browser default), up from the 15px the widget
used as an embed inside a blog post, and every size on the page moved with it.

**The scale is in `rem`, which is the part that matters most.** A `px` size ignores the reader's
own default-font-size setting — zoom still works, but somebody who has set larger text
everywhere would not get it here. `rem` follows that setting: at a 20px browser default the body
renders at 22.5px without anyone touching a zoom control.

Colours were darkened at the same time, because a legible typeface at a comfortable size is
still undone by grey-on-cream nobody can resolve. `tools/check-contrast.py` measures every
text/background pair the page uses against WCAG 2.1 AA; all eleven pass.

```bash
python3 tools/check-contrast.py
```

## Accessibility

This is a game about belonging, made for Autistic and otherwise neurodivergent people. The
accessibility of the page is part of the work, not a finishing pass.

**The card prompts are lettered into the card artwork.** That is how Helen designed the deck and
it is right for print — but on the web it means the words cannot be zoomed independently,
reflowed, restyled into a reading font, selected, copied, translated, or handed to a
highlighter. On a phone the lettering is small and fixed.

So the page shows **the card, and the same words as text beneath it**. The text is the
authoritative copy: it is what a screen reader gets in the `alt`, what reflows at 400% zoom, and
what a reader can select. *This is the one deliberate departure from the published page* — see
`DECISIONS.md`. It is a handful of lines in `penguin-pebbling.js` (`renderCard`) if it is ever
decided against.

Also here, and all of it uncontroversial: a skip link, real `<button>` elements with
`aria-pressed` on the filters, `aria-live` on the card area so a drawn card is announced, full
prompt text in `alt` rather than a 150-character prefix, visible focus rings,
`prefers-reduced-motion` honoured, and `width`/`height` on every image so nothing shifts as the
page loads.

## Licence

**Free to use, share, and adapt for non-commercial purposes.** Please credit Helen Edgar,
Autistic Realms and Ryan Boren, Stimpunks, and link back.

That is the licence as the game itself states it, and it is deliberately not one of the standard
open-source licences — the code and the cards travel together here, and the cards are not MIT.
See `ATTRIBUTIONS.md` for what belongs to whom, and `DECISIONS.md` for what is still open.
