# Penguin Pebbling

**A Game of Creating Belonging, Building Connection and Understanding Autistic Identity**

A neuro-affirming card game built around the Five Autistic Love Locutions — infodumping,
parallel play, support swapping, deep pressure, and penguin pebbling itself. Thirty cards,
six per locution. No winners. No wrong way to play.

Developed by **Helen Edgar** at [Autistic Realms](https://autisticrealms.com) and **Ryan Boren**
at [Stimpunks](https://stimpunks.org), 2026.

Lives at **penguinpebbling.app**, hosted on Stimpunks' Netlify.

----

## What this repository is

The game was first published as a WordPress post at Autistic Realms, with the playable part
living in a single Custom HTML block. That block turned out to contain a whole `<head>` and
`<body>` — Helen had written it as a standalone HTML page and pasted it in. This repository is
that page given its own address, with the surrounding article brought along and every asset
pulled local.

**There is no build step and no dependency to install.** It is HTML, one stylesheet, two scripts,
and a folder of pictures. Open `index.html` and it works; push the folder and it deploys.

```
index.html              the game, and almost nothing else
how-to-play.html        what it is, what you need, taking turns, ending a game
locutions.html          the five locution cards and a quick guide
print.html              the printable deck, Plain Language and Easy Read guides
about.html              sources, practitioners, licence, references
changelog.html          generated from CHANGELOG.md — never edit it directly
privacy.html            what the site does with your data, which is nothing
penguin-pebbling.css    Helen's palette and type, extended to cover the page
penguin-pebbling.js     the thirty cards and the game logic
cards/art/              the re-set deck's artwork — 1 pebble stack, 5 illustrations
cards/                  35 WebP derivatives; only the 5 locution cards are still shown
cards/print/            the same 35 as Helen's original PNGs (1748x1240) — print masters
downloads/              Plain Language guide, Easy Read guide, printable deck (PDF)
og-image.png            1200x630 share card, for links unfurled on social
favicon.ico             generated — the fallback for anything that wants an .ico
icon-maskable.png       generated — the Android home-screen icon, safe-zone padded
search-index.json       generated from penguin-pebbling.js — the deck's text, for our mirror
llms.txt                generated from the pages — a short map of the site for LLMs
tools/make-images.py    regenerates cards/ from cards/print/
tools/make-og-image.py  regenerates og-image.png
tools/make-icons.py     regenerates favicon.ico and icon-maskable.png
tools/make-card-art.py  cuts cards/art/ out of the print masters
tools/set-domain.py     rewrites the site's own address everywhere at once
tools/sync-shell.py     keeps the nav and footer identical across the pages
tools/build-changelog.py renders CHANGELOG.md into changelog.html
tools/make-search-index.py publishes the deck's text for archivers and our mirror
tools/check-contrast.py checks every colour pair, both themes, against WCAG AA
tools/make-llms-txt.py  regenerates llms.txt, the curated index for language models
theme.js                light/dark, set before first paint and remembered
fonts/                  Atkinson Hyperlegible Next, self-hosted, with its OFL licence
netlify.toml _headers _redirects   Netlify configuration
```

**The site lives at <https://penguinpebbling.app/>.** Every self-reference is set by `tools/set-domain.py`, which moves all seven at once and refuses to point at a host it cannot confirm exists — see `DECISIONS.md` for why confirming that is harder than a name lookup.

## Nothing loads from autisticrealms.com

That was the point of the import. Every image, every PDF, the stylesheet, both scripts and the
typeface are served from this repository. There is no CDN, no analytics, no third-party anything
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
`tools/sync-shell.py`. Six hand-maintained copies of one menu is a drift problem with a quiet
failure mode — a link added in one place, a page that still claims to be current after a rename.
Edit the nav in `index.html`, then:

```bash
python3 tools/sync-shell.py          # stamp it into the rest
python3 tools/sync-shell.py --check  # report drift, write nothing
```

## The changelog

`CHANGELOG.md` is the source; the published page at
[penguinpebbling.app/changelog](https://penguinpebbling.app/changelog) is generated from it.
**Never edit `changelog.html` by hand** — the next build overwrites it.

```bash
python3 tools/build-changelog.py          # rebuild the page
python3 tools/build-changelog.py --check  # report drift, write nothing
```

Entries are dated by the day a change went live, newest first, split into **Game** (the cards,
the prompts, how a card is shown) and **Site**. There are no version numbers, because the site
deploys continuously.

The renderer understands a deliberately small dialect — `##`/`###`, `-` bullets, paragraphs, and
inline bold, italic, code and links — and **anything else is a hard error rather than a silent
drop.** A renderer that quietly swallows a line it does not recognise is the worst kind for a
document whose whole job is being a complete record: the page would look fine and the entry
would be gone.

## Colour

**Sage, because sage is Helen's colour** — and because our other sites are all cream:
queering.earth on warm vellum, cavendish.app on Solarized light. This one needed to look like
itself.

The ground is built on the hue of **#aac5c0**, the sage in the Deep Pressure card, and every
accent is one of the five pigments Helen already painted the deck with, sampled straight out of
`cards/print/*-locution.png` rather than picked to match:

| | | |
|---|---|---|
| Infodumping | `#bba4b8` | dusty mauve |
| Parallel Play | `#ddbbba` | dusty rose |
| Support Swapping | `#c3beaf` | taupe |
| Penguin Pebbling | `#e8e1ce` | warm sand |
| Deep Pressure | `#aac5c0` | sage — the ground is built on this |

Every one of those sits between 14% and 36% saturation. **The deck was drawn low-stimulation
already**; the site follows it rather than inventing a mood of its own.

**Low stimulation is about surfaces, not text.** Paper, panel and sunk are within a few percent
of each other, there is no pure white and no pure black anywhere, and the hues stay muted — while
text contrast stays high. The lowest text pair on the page is 4.98:1 in light and 5.27:1 in dark,
against the 4.5:1 AA asks for. Muting the text too would be the easy mistake, and it would hurt
exactly the readers this is for.

## Dark mode

Follows the system by default, in CSS alone — so it works with JavaScript off. `theme.js` only
stores a deliberate override, which means someone who never touches the toggle keeps following
their OS, including when it changes at sunset.

It is loaded from `<head>` **without `defer`**, deliberately: the attribute has to be set before
the first paint, or a reader who chose dark gets a flash of the full-brightness page first — on a
site built for sensory needs, the one bug least worth having.

**The card follows the theme too, which it could not do while it was a picture.** A
full-brightness cream rectangle against a near-black page is a glare line at every edge, and while
the card *was* Helen's artwork the only honest answer was a lifted mat under it — dimming someone's
artwork misrepresents it. Re-setting the deck as text removed the constraint: the panels are CSS, so
in dark mode they are a warm dark with light warm text.

**The cream ellipse inside each illustration stays bright on purpose.** The penguins are
black-outline drawings and need a light ground; against the darkened panel it reads as a spotlight.
Helen's drawings themselves are still never dimmed, filtered or recoloured.

```bash
python3 tools/check-contrast.py   # both themes, 48 pairs
```

That tool checks light *and* dark, and also that the `data-theme` block and the
`prefers-color-scheme` block have not drifted apart — two copies of one palette being the obvious
way this breaks later.

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

**The prompts used to be lettered into the card artwork.** That is how Helen designed the deck and
it is right for print — but on the web it meant the words could not be zoomed independently,
reflowed, restyled into a reading font, selected, copied, translated, or handed to a highlighter.
On a phone the lettering stayed small and fixed while everything around it adapted.

**The deck is re-set as text now**, approved by Helen on 2026-09-15 and set in Atkinson
Hyperlegible Next. `renderCard()` builds the card rather than fetching a picture of one: the
prompt, the locution name and the aside are text, and only the drawings are images — one pebble
stack and one illustration per locution, because Helen's artwork does not vary between the six
cards of a locution. They are decorative and carry an empty `alt`, which is correct now that the
locution is named in text beside them.

The card has **no fixed aspect ratio**, deliberately. Reflowing is the point: at 400% zoom the
prompt re-wraps and the card grows taller instead of overflowing, and on a phone the two panels
stack. See `DECISIONS.md`, including why the ink is a darker version of Helen's — her `#b28a5e`
on cream is 2.57:1, which nothing measured while it was inside a picture.

Also here, and all of it uncontroversial: a skip link, real `<button>` elements with
`aria-pressed` on the filters, `aria-live` on the card area so a drawn card is announced, full
prompt text in `alt` rather than a 150-character prefix, visible focus rings,
`prefers-reduced-motion` honoured, and `width`/`height` on every image so nothing shifts as the
page loads.

## Licence

**[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)** — free to use, share and adapt for
non-commercial purposes. Credit Helen Edgar, Autistic Realms and Ryan Boren, Stimpunks, link back,
and license anything you build on it the same way.

The game described these terms in a sentence from the start. Adopting the written licence on
2026-09-15 did not change what was allowed; it answered the question the sentence left open —
what happens to an adaptation — and gave a school or clinic's legal team something they already
recognise. Not an open-source code licence, deliberately: the code and the cards travel together
here, and the cards are not MIT. See `LICENSE.md` for the terms in full, `ATTRIBUTIONS.md` for what
belongs to whom, and `DECISIONS.md` for what is still open.
