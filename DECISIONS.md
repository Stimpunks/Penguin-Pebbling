# Decisions

What was chosen during the import, why, and what is still open. Newest at the top of each section.

----

## Open — these need Helen

### 1. The card text under the card art

**Status: implemented, and the easiest thing here to reverse.**

Every prompt is lettered into the card image. On the published page that is all there is: the widget renders the picture and nothing else, and the prompt reaches a screen reader only through a 150-character `alt` prefix that cuts mid-sentence on the longer cards.

Text baked into an image cannot be zoomed on its own, reflowed, restyled into a reading font, selected, copied, translated, or highlighted. For a game whose audience is Autistic and otherwise neurodivergent people, several of whom will be using exactly those tools, that is a real cost. It is most visible on a phone, where the lettering is small and fixed while everything around it reflows.

So `renderCard()` in `penguin-pebbling.js` draws the card image and then the same words as text underneath, and `alt` now carries the whole prompt rather than a prefix.

**This is a visible change to Helen's design and it is hers to approve.** It is one function. If she would rather the page show the art alone, delete the `card-text` block from `renderCard` and the `.card-text` rules from the stylesheet; the fuller `alt` text should stay either way.

### 2. Whether the deck should be re-set as text rather than pictures

Follows from the above but is much larger. The cards are 1748×1240 PNGs — beautiful, and 28.5 MB for the set. Rendering each card from text and CSS with the penguin illustration as a separate transparent image would give a deck that is a few hundred kilobytes, scales to any screen, and needs no `alt` at all because it would be text.

It would also mean rebuilding Helen's typography in CSS, and the printable PDF deck would still need the PNGs. **Not proposed, only noted.** The WebP derivatives already take the page from 28.5 MB to 1.8 MB, which removes the urgency.

### 3. The licence is a sentence, not a licence

The game says *"free to use, share, and adapt for non-commercial purposes, please credit and link back."* That is clear enough to read and ambiguous enough to argue about — it does not say whether adaptations must carry the same terms, and it has no text to point a court or a cautious institution at.

**CC BY-NC-SA 4.0 says exactly this and is written down.** Adopting it would cost nothing and would answer the question a school or clinic's legal team asks. But it is a licensing decision about Helen's artwork as much as the code, so it is hers and Ryan's jointly, not something to slip in during an import. Left exactly as the game states it.

----

## Settled during the import

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
