# Decisions

What was chosen during the import, why, and what is still open. Newest at the top of each section.

**Nothing is open.** The three items that needed Helen were all decided on 2026-09-15 and are written up below.

----

----

## Settled during the import

### The card breaks out of the prose column, because the measure was too short

Ryan, 2026-09-15: *"I kinda miss having the text beneath the cards. Can that come back, or is it too redundant now?"*

It is redundant — the card **is** the text now, so a copy beneath it would be the same words twice and a screen reader would read every prompt through and then read it again. Restoring it would undo what the re-set was for.

**But the instinct was right, and it was not nostalgia.** Measuring what was actually lost: the prompt as prose beneath the card ran about **58 characters a line**, left-aligned, at 1.65 leading in `--ink` at 12.58:1. Inside the two-panel card it ran **27**, centred, at 1.5, in `--card-ink` at 6:1. The comfortable measure is 45 to 75 characters. 27 is less than half the lower bound. The prompt had not simply moved; it had been squeezed into a column half the width with tighter leading.

The leading went straight back to 1.65 — a short measure needs *more* leading, not less, because the eye has to find the start of the next line more often.

The measure needed the card to be wider than the 680px prose column, which caps it at 624px however large the screen is. So above 1000px the card steps outside the column to 960px, re-centred with a percentage margin — `(100% - width) / 2` is exactly the negative offset that centres a child wider than its parent, with no transform and no positioning, and it survives the column ever changing width. The split moves to 1.25/1 at the same time: Helen's 50.6/49.4 is right for a printed card, where the words are set to fit the panel, and backwards on screen, where the words are given and the panel has to fit them.

**The stacking breakpoint moved from 560px to 1000px, and that is the part worth remembering.** It is not about phones. Two panels only reach a readable measure once the card is about 960px wide, which needs roughly a 1000px viewport; below that, measured, stacking beats it every time — 35 characters at an 800px viewport against 58 stacked. So the rule is to use two panels only where two panels actually read, and stack otherwise, including on a tablet that looks wide enough for a card.

Measured after: 58 characters stacked, 46 in two panels, 27 nowhere.

### The card follows the theme, and the pebbles are vector

Ryan's call, 2026-09-15, immediately after the re-set landed: *"Go theme-aware with the SVG pebbles."*

**The rule that the card stays bright no longer applied, and it is worth being clear why.** The card stayed cream in dark mode because it *was* Helen's artwork, and dimming someone's artwork misrepresents it; the lifted mat under it was a workaround for the glare, not a fix. Re-setting the deck as text removed the constraint rather than answering it — the panels are CSS now and only the drawings are hers. So the card can follow the theme like everything else on the site, which on a page built for sensory needs is what it should have been doing all along.

**The cream ellipse inside each illustration deliberately stays bright.** The penguins are black-outline drawings and need a light ground beneath them. On the darkened panel it reads as a spotlight rather than as the glare line a full cream card was.

**Helen's watercolour pebbles could not come along, and that was tested rather than assumed.** A theme-aware card needs a pebble stack with no background, and her stack is watercolour on flat cream. Keying the cream out makes the stones' pale interiors transparent. Flood-filling from the edge — which only removes background actually connected to the border — is the right technique and still fails: the middle stone's highlight is the same value as the ground *and touches the edge*, so the fill leaks in and leaves a hole straight through the stone. Tightening the tolerance moves the failure rather than removing it.

So the card draws the three flat pebbles from `favicon.svg`, which are Helen's palette already and carry no background. **Inline, not `<img src="favicon.svg">`**, and that distinction matters: an SVG loaded as an image is its own document and cannot see this page's `data-theme` attribute, so it would follow the operating system and quietly ignore the toggle. Drawn into the DOM it inherits `color` and both paths work — verified with the OS set to light and the toggle set to dark.

The watercolour stack is untouched in `cards/print/` and is still what is on the printed deck.

**One ink in dark where light needs two.** On the dark ground and on all five dark tints it lands between 10:1 and 12:1, so splitting it would buy nothing. The dark tints are Helen's own pigments at the lightness the rest of the dark palette already uses — about 15% — derived by `tools/make-card-art.py` rather than picked, so the card and the locution panels elsewhere darken as one thing. `tools/check-contrast.py` now measures sixteen card pairs, eight per theme.

### The deck is re-set as text

**Decided 2026-09-15. This was the last open item, and it was Helen's.** Done.

The prompts, the locution names and the aside are real text in the page now, set in Atkinson Hyperlegible Next. Only the drawings are still pictures.

**Ryan's call on the typeface, and it is the one that made this cheap.** The original plan assumed rebuilding Helen's serif in CSS, which meant identifying it, self-hosting it, and editing the CSP to let a second face in. Atkinson Hyperlegible Next is already here, already self-hosted, already the typeface the rest of the site is set in, and is drawn by the Braille Institute for exactly this audience. *"Since we made the game, we've standardised on Atkinson HN."*

**The saving that made the rest cheap is that Helen's artwork does not vary per card.** All six Infodumping cards carry the same penguin and the same cream ellipse; only the words differ. So thirty pictures reduce to six — one pebble stack, which is on every card in the deck, and one illustration per locution — cut out by `tools/make-card-art.py`, which detects the panel split, the ellipse and the pebbles rather than cropping at hard-coded coordinates.

The card's imagery goes from 1.5 MB across thirty files, one fetched per draw, to 152 KB across six, cached after the first. But weight was never the reason, and `DECISIONS.md` said so when this was still open: the WebP derivatives had already removed the urgency.

**The reason is that it reflows.** A prompt in a 1280px picture is a 1280px picture: at 400% zoom it does not re-wrap, on a phone the lettering stays small while everything around it adapts, and it cannot be re-set in a reading font. As text it fills a phone's width, re-wraps at any zoom, and the card grows taller instead of overflowing. That is why the layout is deliberately *not* a fixed aspect ratio, which would have fought the whole point.

**The one thing that had to change is the ink, and it is worth being plain about.** Helen letters her cards in `#b28a5e` on her cream. Baked into a picture nothing measured it; as real text it is a pair this site is answerable for, and it is **2.57:1** against the 4.5:1 AA asks for. The ink keeps her hue (31.4°) and her saturation (35.3%) exactly and only moves in lightness: `#6c5133` on the cream at 6.0:1, and `#473522` for the small text on the locution tints, which clears 5:1 on all five including the palest. `tools/check-contrast.py` measures all eight of those pairs now, so they cannot drift back.

**The alt text is gone, and that is the correct outcome.** The prompt used to be carried in `alt` because the picture was the only copy. The illustrations are decorative now — the locution is named in text beside them — so an empty `alt` is right, and a screen reader reaches the prompt as prose rather than as a description of a picture.

The print masters in `cards/print/` are untouched and the printable PDF deck still comes from them. **The thirty prompt-card WebP derivatives were retired on 2026-09-15**, once it was clear nothing linked them: 1.5 MB that `tools/make-images.py` went on regenerating and Netlify went on deploying for as long as nobody looked. That tool now owns only the five locution cards — the ones `locutions.html` still shows, where the card itself is the subject — and deletes any prompt-card WebP it finds, so the leftover cannot come back by someone re-running it. Deleting a derivative is not deleting an original: all thirty-five masters stay.

### The card text under the card art was approved

**Decided 2026-09-15. This was open item 1, and it is Helen's to decide.** Approved as built.

Every prompt is lettered into the card image. On the published page that is all there is: the widget renders the picture and nothing else, and the prompt reaches a screen reader only through a 150-character `alt` prefix that cuts mid-sentence on the longer cards.

Text baked into an image cannot be zoomed on its own, reflowed, restyled into a reading font, selected, copied, translated, or highlighted. For a game whose audience is Autistic and otherwise neurodivergent people, several of whom will be using exactly those tools, that is a real cost. It is most visible on a phone, where the lettering is small and fixed while everything around it reflows.

So `renderCard()` in `penguin-pebbling.js` draws the card image and then the same words as text underneath, and `alt` carries the whole prompt rather than a prefix. **It shipped on 2026-09-14 and ran unapproved for a day**, which is the wrong order and worth saying plainly: it was a visible change to Helen's design, made during an import, and the right version of this is that it waits. It is approved now.

The follow-on question — whether to stop using the pictures altogether and re-set the whole deck as text — is a different and much larger one, and is the single item still open.

### The licence is CC BY-NC-SA 4.0

**Decided 2026-09-15. This was open item 3, and it was Helen's and Ryan's jointly.**

The game always described its terms in a sentence: *"free to use, share, and adapt for non-commercial purposes, please credit and link back."* Clear enough to read, ambiguous enough to argue about, and with no text to point a court or a cautious institution at.

**[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) says that, and is written down.** Adopting it changes nothing about what was already permitted — use, share, adapt, non-commercially, with credit — and answers the one question the sentence left open: **ShareAlike.** An adaptation must now carry the same licence. That is a real addition to the terms, not just a formalisation, and it is the thing to be clear about with anyone who took the old wording as permission to relicense a derivative.

Two things it deliberately does not disturb. **The shop is unaffected**: NonCommercial binds the people who receive the work, not the people who made it, so Helen and Ryan go on selling the deck and taking donations exactly as before. And **the code is not separately licensed** — it travels with the game, because the code and the cards ship together here and the cards are not MIT.

`LICENSE.md` carries the terms, including the part worth saying out loud: printing the deck for a classroom or a clinic, or making a translation or an AAC version for the people in front of you, is ordinary use. ShareAlike bites on *distributing* an adaptation, not on making one.

### Sage, from Helen's own cards — and a dark mode

Ryan's call, 2026-09-14: *"I like cream backgrounds, but we use them everywhere."* He is right —
queering.earth is warm vellum `#f5efe2`, cavendish.app light is Solarized `#fdf6e3`, and this
site launched on `#faf8f5`. Three sites, one ground. Helen's favourite colour is sage.

**The palette was sampled, not chosen.** The ground is built on the hue of `#aac5c0` — the sage
in her Deep Pressure card — and the five locution tints are her five card pigments, read straight
out of `cards/print/*-locution.png`: dusty mauve, dusty rose, taupe, warm sand, sage. All five
land between 14% and 36% saturation, which is the finding that settled the brief: **the deck is
already low-stimulation, so the site should follow it rather than invent a mood.** Sage and cream
is also the pairing Helen drew into the Deep Pressure card herself, so the cream artwork sits on
the sage page as a deliberate combination rather than a clash to be managed.

**Low stimulation is about surfaces, not text**, and that distinction is the whole design. Paper,
panel and sunk sit within a few percent of each other, there is no pure white or pure black, and
no hue is loud. Text contrast is high: 4.98:1 at the lowest in light, 5.27:1 in dark. Muting the
text as well is the easy version of this brief and it would hurt the readers it is meant to serve.

**Dark mode follows the system in CSS alone**, so it works with JavaScript off. `theme.js` stores
only a deliberate override, which keeps an untouched browser tracking the OS at sunset. It loads
from `<head>` without `defer` on purpose — deferred, a reader who chose dark gets a flash of the
bright page before the attribute lands.

**The cards stay bright, and sit on a mat.** Cream artwork against a near-black page is a glare
line at every edge, and the obvious fix — a brightness filter — misrepresents Helen's work. A
lifted surface under the card closes the gap without touching a pixel of it.

`tools/check-contrast.py` grew to cover both themes, all 48 pairs, plus a check that the
`data-theme` and `prefers-color-scheme` blocks still agree: two copies of one palette is exactly
how this drifts later, and it would drift silently.

The favicon, the apple-touch icon, the manifest colours and the share card were repainted to
match, and the pages carry per-scheme `theme-color`.

### Netlify rewrites the markup on the way out, and the canonical follows it

Found 2026-09-14, right after the page split. The published HTML is not the HTML in this
repository: `href="how-to-play.html"` is served as `href='/how-to-play'`, double quotes become
single, and attribute order changes. That is Netlify's **Pretty URLs**, a site-level setting —
`skip_processing = true` in `netlify.toml` does not cover it, because that governs asset
optimisation (minifying, image compression) and this is separate HTML post-processing.

**It is on for cavendish.app and queering.earth too**, and has been all along; their published
navs serve `/guidebook` from `guidebook.html` exactly the same way. So this is how our Netlify
sites behave, not something new here.

It left a real inconsistency for a few minutes, though: the nav linked `/print` while the
canonical said `/print.html`, and both served 200. Two URLs for one page, reconciled only by a
tag. **The canonical, `og:url` and the sitemap are extensionless now**, matching what is linked
and what is served. The `.html` stays in the source hrefs so the pages work over a plain local
file server, and Netlify rewrites them on the way out.

The `_redirects` rules for `/print`, `/how-to-play`, `/locutions` and `/about` were removed as
dead weight — Netlify already serves those. `/downloads` and `/game` keep theirs, because those
never named a page.

**The general shape is familiar**: the source is clean and only the served page differs, which
is the same reason the WordPress hazards in the knowledge system are all "check it after
publishing". A diff of the live HTML against the repository will never be clean here — check
what the page *does*, not whether its bytes match.

### The game moved to the front, and the prose moved to its own pages

Ryan's call, 2026-09-14, pointing at [cavendish.app](https://cavendish.app/), which had already
solved this: *"The game itself is way down the page."*

It was. The single page opened with roughly a thousand words — what Penguin Pebbling is, then the
full How to Play — before reaching the thing all of it describes. On a phone the game was most of
a screen-and-a-half down. That ordering is inherited from the original: it was an *article* at
Autistic Realms with a game embedded in it, and the article's shape survived the import unexamined.

Now `index.html` is the game and a short list of links. `how-to-play.html`, `locutions.html`,
`print.html` and `about.html` take the rest, reachable from a `<details>` menu in a sticky bar —
the Cavendish pattern, including `aria-current="page"` and a **Play the game** button on every
other page. **No content was cut**: every word is still on the site, on the page it belongs to.

Three things followed from the move rather than being decided separately:

- **The masthead was merged into the game header.** They both said "Penguin Pebbling" and both
  carried the same tagline, one directly above the other. The game header is the `<h1>` now.
- **The collapsed "How to play" panel moved below the controls** on the game page. It is
  reference material on a page whose only job is "press Draw", and in front of the button it was
  pushing the single action off a phone screen. The full instructions have their own page; this
  is the copy you want mid-game.
- **Sentences that pointed at the old layout were rewritten.** *"use the game below"* and
  *"print and cut the card set further down this page"* were true of one long page and false of
  five. They are links now. This is the failure mode of splitting a page: the prose goes on
  describing the shape it used to have, and nothing errors.

`tools/sync-shell.py` owns the nav and footer so five copies cannot drift apart, and
`tools/set-domain.py` grew from three files to seven.

### Atkinson Hyperlegible Next, at sizes chosen for this page

Ryan's call, 2026-09-14. The widget was typed in the system UI font at 11–15px, which is what an
embed inside a blog post gets away with and not what a page about Autistic identity should ship.

**The typeface is an accessibility choice, not a styling one.** Atkinson Hyperlegible Next is
drawn by the Braille Institute to separate the characters most often confused — capital I,
lowercase l and the digit 1; capital O and zero; b, d, p and q. Self-hosted in `fonts/`, four
woff2 files totalling about 111 KB, each carrying the whole 200–800 weight axis. It has to be
self-hosted: `_headers` sends `default-src 'none'` with `font-src 'self'`, so a Google Fonts
`<link>` would be blocked by the site's own policy — silently, falling back to the system font
while looking fine in a local test — and fetching a font at runtime would also tell a third
party who is reading this page.

**Sizes are in `rem`, and that is the substantive half of "bump the font sizes up".** A larger
`px` scale is still a fixed scale: it ignores the reader's own browser default-font-size
setting, so a person who has already told their browser they want bigger text gets nothing.
`rem` honours it — measured at a 20px default, body renders 22.5px. Body is 1.125rem, card
prompts 1.1875rem (they are the thing being read), h1 2rem.

**Three colours were darkened at the same time**, because none of the above survives
grey-on-cream. `--ink-faint` at `#a89882` was about 2.6:1 on the warm paper, well under the
4.5:1 AA needs; it is `#7a6c58` now. `tools/check-contrast.py` measures all eleven pairs the
page uses and all eleven pass — it was written because "looks fine on this monitor" is not a
measurement.

What did **not** change: the palette's character, the card artwork, the layout, or any wording.

### The domain, and why a name lookup is not a good enough guard

`penguinpebbling.app` went live on 2026-09-14 and the site moved to it. All seven self-references — the canonical link, `og:url`, `og:image`, the JSON-LD `url` and `license`, the `Sitemap` line in `robots.txt`, and the `<loc>` in `sitemap.xml` — are set by `tools/set-domain.py`, which refuses to point at a host it cannot confirm exists.

**Confirming that turned out to be the interesting part.** The first version asked `socket.gethostbyname` and believed the answer. It refused the switch on a domain that was already live and serving with a valid certificate, because this machine had cached the NXDOMAIN from before the domain was registered — for the SOA minimum, which is an hour here.

Falling back to a public resolver was not enough either. `.app` is DNSSEC-signed, so the pre-registration denial is *authenticated*, and public resolvers cache it with confidence: consecutive queries to Cloudflare returned `Status: 3` and `Status: 0` seconds apart, as different edge nodes expired it at different times.

So the guard now encodes the asymmetry that actually holds: **a positive DNS answer is proof, a negative one is only weak evidence.** A resolver cannot invent an A record, so one yes settles it; a no might just be a denial that has not expired. It asks the local resolver, then Cloudflare, then Google, retries, and concludes "no" only when everything says no. Network failure is reported as unknown rather than as absence.

The `.netlify.app` address still works and Netlify 301s it to the domain, so anything indexed during the gap follows.

### Assets are local; links to Autistic Realms are not "dependencies"

All 38 assets — 35 card PNGs and 3 PDFs — were pulled over and are served from this repository. Nothing fetches from autisticrealms.com at runtime.

**The outbound links stay pointing at Helen's site**, and deliberately: the citations to her writing, the practitioner guide, and above all the shop link where the deck is sold and donations are taken. Those are credit and livelihood. "No dependencies on autisticrealms.com" means no asset will break if her site moves; it does not mean scrubbing her name off the page.

### The PNGs stay in the repository as print masters

Serving Helen's originals would spend 28.5 MB to show thirty-five pictures, on a page that shows one card at a time, to an audience that includes people on slow and metered connections. Serving only resized copies would throw away the print resolution.

Both, then: `cards/print/` holds the originals, `cards/` holds 1280px WebP at 6% of the size, and `tools/make-images.py` regenerates one from the other. 1280px is 2× the 640px a card ever occupies in the 680px column.

### The shuffle was replaced with Fisher–Yates

The original used `sort(() => Math.random() - 0.5)`. That is not a uniform shuffle — a comparison sort assumes a consistent comparator and a random one leaves items near where they started. On a six-card locution filter, the practical effect is drawing the prompt you just answered. Fisher–Yates is four lines and correct. Invisible in the interface; nothing else about drawing changed.

### Inline `onclick` became `addEventListener`

Identical behaviour, and it is what lets `_headers` ship `script-src 'self'` with no `'unsafe-inline'`. The filter buttons are now generated from the `LOCUTIONS` array rather than hand-written six times.

### Card images renamed

Helen's WordPress upload numbering (`2-1.png` … `36-1.png`) carries no meaning and its ordering is not the deck's — the Deep Pressure cards are stored `31, 35, 32, 34, 33, 36`. Renamed to `<locution>-<n>.png`. The mapping was taken from the `CARD_IMAGES` object in the original page and checked for collisions and leftovers: 35 in, 35 out, none unmapped.

`22-1.png` exists in her media library, is not referenced by the page, and was not brought over.

### The page keeps its repetitions

The intro paragraph appears twice on the published page — once as a standfirst, once in the body — and "How to Play" appears both as prose and inside the game's collapsed rules panel. Both were kept. They read as editorial choices rather than block-editor accidents, and an import is the wrong moment to start trimming someone's prose.

One sentence was adjusted, because it became false: *"The cards — use the widget above"* sat above the widget on the original page. It now reads *"use the game below, or print and cut the card set further down this page."*

### Source of truth for the import

`raw/ecosystem/wordpress/autisticrealms.com/posts/penguin-pebbling-*.json` in the Stimpunks Knowledge System, fetched 2026-08-05 — verified byte-identical to the live REST API on 2026-09-14 before anything was built from it.
