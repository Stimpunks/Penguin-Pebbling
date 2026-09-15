# CLAUDE.md — Penguin Pebbling

Guidance for Claude Code working in this repository.

## What this is

**Penguin Pebbling** ([penguinpebbling.app](https://penguinpebbling.app/)) is a neuro-affirming card game by **Helen Edgar** (Autistic Realms) and **Ryan Boren** (Stimpunks), published first at Autistic Realms and given its own site here. Thirty cards across the Five Autistic Love Locutions, playable in the browser or printable as a deck.

Read `README.md` for the layout, `ATTRIBUTIONS.md` for who owns what, `LICENSE.md` for the terms, and `DECISIONS.md` for what was chosen during the import and what is still open. **`DECISIONS.md` has no open items.** All three that needed Helen — the card text under the art, the deck being re-set as text, and the licence — were decided on 2026-09-15 and are written up under Settled. Read them before reopening any of it.

## Two people work here

Helen Edgar and Ryan Boren both have rights to this work. **So *you* is whoever is at the keyboard, and it is never safe to guess.** Ask which one only when the answer changes the work — a byline, an attribution, whose call a design decision is. It usually does not.

**Helen's design decisions are Helen's.** The palette, the card artwork, the type, the wording of the prompts. Propose, do not apply.

The one time that was stretched is worth knowing about. Rendering the card prompt as text under the art shipped on 2026-09-14 and was approved on the 15th — so it ran live and unapproved for a day. It is settled now and the outcome was the right one, which is exactly why it is not a precedent: a visible change to someone else's game waits for them, and the fact that it turned out fine is not the test.

## House rules

- **Capitalize Autistic and Disabled. Identity-first language** — "Autistic person", never "person with autism". This is not a style preference; it is the community's own usage and the whole site is written in it.
- **Horizontal rules in Markdown are `----`, four dashes.** YAML fences stay at three.
- **One line per paragraph in Markdown.** No hard-wrapping prose; let the editor soft-wrap. `DECISIONS.md`, `ATTRIBUTIONS.md` and `CHANGELOG.md` are written this way; parts of `README.md` predate the rule.
- **The licence is CC BY-NC-SA 4.0**, adopted 2026-09-15. The ShareAlike is the part that is new and easy to get wrong when describing it: an adaptation must carry the same licence. `LICENSE.md` is the source; the site states it on `about.html`, in the footer and in the JSON-LD.
- **British spelling** in page copy — Helen's, and the published text uses it (*centre*, *recognise*, *journalling*).
- **Never hand-edit a generated file.** See below — there are three of them now, and each has a tool that will overwrite it.

## Generated files — never edit these by hand

| File | Generated from | By |
|---|---|---|
| `cards/` (35 WebP) | `cards/print/` (the PNG masters) | `tools/make-images.py` |
| `changelog.html` | `CHANGELOG.md` | `tools/build-changelog.py` |
| `search-index.json` | `penguin-pebbling.js` | `tools/make-search-index.py` |
| `llms.txt` | the pages' own title/description/canonical, and the deck | `tools/make-llms-txt.py` |
| `og-image.png` | the deck, the card palette, `favicon.svg`, `cards/art/`, the woff2 | `tools/make-og-image.py` |
| `favicon.ico`, `icon-maskable.png` | `apple-touch-icon.png` | `tools/make-icons.py` |
| `cards/art/` and the `card-art:palette` block in the CSS | `cards/print/` | `tools/make-card-art.py` |
| `sw.js` | `sitemap.xml` plus globs | `tools/make-service-worker.py` |
| the nav and footer in every page but `index.html` | the marked blocks in `index.html` | `tools/sync-shell.py` |

Edit the source on the left-hand side, then run the tool. An edit on the right is lost on the next run, silently.

## The shape of the site

**Seven pages, not one.** `index.html` is the game and a short list of links; `how-to-play.html`, `locutions.html`, `print.html`, `about.html` and `changelog.html` hold everything else, reached from a `<details>` **Menu** in a sticky bar. It was one long page for a day, with the game buried under a thousand words — `DECISIONS.md` has the reasoning.

`privacy.html` is the seventh and is deliberately **not** in the Menu — it is linked from the footer, which is where a privacy notice belongs and leaves the six-item game nav as designed. `sync-shell.py` knows this: it still stamps the shell into the page, and `FOOTER_ONLY` is what stops it erroring over a page with no nav link. Anything else missing from the nav is still a hard error, because that is what catches a rename.

The nav and footer are authored once in `index.html`, between `<!-- shell:nav -->` and `<!-- shell:footer -->` markers, and stamped into the other six by `tools/sync-shell.py`. **Edit the nav in `index.html` and then run the tool** — editing it in `about.html` is editing a copy.

**A new page has to be registered in four places**: the nav (or `FOOTER_ONLY`), `sitemap.xml`, `sync-shell.py`'s `PAGES`, and `set-domain.py`'s `FILES`. Miss one and nothing errors — the page simply drifts, or never gets its domain rewritten.

Alongside them: `penguin-pebbling.css` (one stylesheet), and **two scripts** — `penguin-pebbling.js` (the thirty cards and the game logic) and `theme.js` (light/dark, deliberately loaded from `<head>` without `defer` so the theme lands before first paint).

## The tools

Eleven, all Python, all run by hand, none wired into a build. Eight take `--check`, which reports drift and writes nothing.

| Tool | What it does | `--check`? |
|---|---|---|
| `tools/sync-shell.py` | stamps the nav and footer into every page | yes |
| `tools/check-contrast.py` | every colour pair, both themes, against WCAG AA | it only ever checks |
| `tools/build-changelog.py` | renders `CHANGELOG.md` into `changelog.html` | yes |
| `tools/make-search-index.py` | publishes the deck's text at `/search-index.json` | yes |
| `tools/set-domain.py` | rewrites the site's own address everywhere at once | yes |
| `tools/make-llms-txt.py` | regenerates `llms.txt`, the curated index for language models | yes |
| `tools/make-images.py` | regenerates `cards/` from `cards/print/` | no |
| `tools/make-og-image.py` | redraws `og-image.png` as the card the site draws | yes |
| `tools/make-icons.py` | regenerates `favicon.ico` and `icon-maskable.png` | no |
| `tools/make-card-art.py` | cuts the illustrations out of the print masters for the re-set deck | yes |
| `tools/make-service-worker.py` | regenerates `sw.js`, the offline precache | yes |

`make-images.py`, `make-og-image.py`, `make-icons.py` and `make-card-art.py` need Pillow, and `make-og-image.py` also needs fontTools and brotli — it renders the page's own woff2, which Pillow cannot read; if it is missing they say so and name the `pip` line. **A tool that could not run has not run** — do not report a check as passing because it printed an error.

`build-changelog.py` understands a deliberately small Markdown dialect and treats anything else as a **hard error rather than a silent drop**. That is on purpose: a changelog that quietly loses an entry still looks fine.

## Verifying a change

There is no test suite. There are nine checks, and they are fast — run them all before calling anything done:

```bash
python3 tools/sync-shell.py --check
python3 tools/check-contrast.py
python3 tools/build-changelog.py --check
python3 tools/make-search-index.py --check
python3 tools/make-llms-txt.py --check
python3 tools/make-card-art.py --check
python3 tools/make-og-image.py --check
python3 tools/make-service-worker.py --check
python3 tools/set-domain.py --check
```

Then serve the folder and actually look at it. `.claude/launch.json` configures the preview server, so in Claude Code just start the `penguin-pebbling` preview; it runs:

```bash
npx -y serve . -l 8913 --no-clipboard
```

`python3 -m http.server 8913` also works here and serves every asset type the page uses with the right content type — verified 2026-09-14. Neither server is a dependency of the site; nothing is installed into the repository and `npx serve` is a dev-time convenience only.

Check the console is clean, draw a few cards, exercise the locution filters, toggle dark mode, and look at it at 375px wide. The card art is fixed-width lettering; the text beneath it is what has to reflow.

## The service worker

**It is network-first for documents, CSS and JS, and that is not the usual advice.** `_headers` revalidates those on every request because a stale stylesheet against fresh markup renders the page wrong — commit `15bc1bd` exists because that happened. A cache-first worker makes that permanent rather than day-long. Fonts, card art and icons are cache-first; their bytes only change when a generator runs, and the cache name is a hash of them.

**The precache holds both URL forms of every page** — `/how-to-play` *and* `/how-to-play.html`. Netlify's Pretty URLs rewrites the markup so production navigates to the first; nothing rewrites locally, so a dev server navigates to the second. Caching one form looks completely fine — the worker installs and reports every URL held — and then the first offline navigation asks for the address nobody cached.

**Once a worker is shipped it lives on people's devices until something unregisters it.** Removing offline support later is not deleting `sw.js`; it is publishing a worker whose only job is to unregister itself. Worth knowing before changing its shape.

## Deploying, and why the live page never matches the repo

**Netlify deploys from `main`, so pushing publishes.** There is no staging step. Treat a push as the publish it is.

Netlify's **Pretty URLs** rewrites the served HTML: `href="how-to-play.html"` goes out as `href='/how-to-play'`, double quotes become single, attribute order shifts. `skip_processing = true` in `netlify.toml` does not cover it. So **a diff of the live HTML against this repository will never be clean — verify what a page *does*, not that its bytes match.** `DECISIONS.md` has the detail, including why the canonical and sitemap are extensionless while the source hrefs keep their `.html`.

## No build step, and keep it that way

No npm, no bundler, no framework, no CDN, no analytics, nothing fetched from a third party at runtime. `_headers` ships `default-src 'none'`, and **adding any third-party resource means editing the CSP, which is the signal to stop and ask whether it is worth it.**

**There is a webfont, and it is self-hosted.** Atkinson Hyperlegible Next lives in `fonts/` — four woff2 files, about 111 KB, with its OFL licence text, which must travel with them. Self-hosting is not incidental: `font-src 'self'` means a Google Fonts `<link>` would be blocked by the site's own policy, silently falling back to the system font while looking fine in a local test — and fetching a font at runtime would tell a third party who is reading a page about Autistic identity. See `fonts/README.md`.

## Accessibility is the product, not a pass at the end

The audience is Autistic and otherwise neurodivergent people, many using screen readers, zoom, reading fonts, AAC, or translation. Anything that makes the page harder to operate is a defect in the game, not a cosmetic issue.

Already in place and worth not regressing: a skip link, real `<button>`s with `aria-pressed`, `aria-live` on the card area, visible focus rings, `prefers-reduced-motion`, a `forced-colors` block that repairs the one state Windows High Contrast flattens (the active locution filter), `scroll-padding-top` so a sticky bar never covers what an anchor jumped to, `width`/`height` on every image, a type scale in `rem` so the reader's own browser text size is honoured, and a dark mode that follows the system in CSS alone so it works with JavaScript off.

**The deck is text now, not pictures.** The prompt, the locution name and the aside are real text set in Atkinson Hyperlegible Next; only the drawings are images, and they are decorative with an empty `alt` because the locution is named in text beside them. `renderCard()` builds the card — it does not fetch one.

**That means the card's colours are this site's responsibility.** Helen letters her cards in `#b28a5e` on cream, which is 2.57:1 and was never measured while it was inside a picture. The ink keeps her hue and saturation and moves only in lightness; `tools/check-contrast.py` measures all eight card pairs. **Do not "restore fidelity" by putting her original ink back** — read the entry in `DECISIONS.md` first.

**The card follows the theme, and the pebble stack is inline SVG for that reason.** An SVG loaded with `<img src>` is its own document and cannot see this page's `data-theme`, so it would track the OS and ignore the toggle. `pebbleStack()` builds it in the DOM so it inherits `color`. Do not "tidy" it into an `<img>`.

**The card's breakpoints are about line length, not devices.** It stacks below 1000px and breaks out of the prose column to 960px above it, because two panels only reach a readable measure (45–75 characters) once the card is about 960px wide. Measured: 58 characters stacked, 46 in two panels, and 27 in the bare prose column, which is what it was. Do not move these to match a device width.

**The card deliberately has no fixed aspect ratio.** Reflowing is the whole reason the deck was re-set: the prompt has to be allowed to make the card taller at 400% zoom rather than overflow it. A rule that pins the card to 1.41:1 undoes the change.

**Contrast is measured, not eyeballed.** `tools/check-contrast.py` covers both themes and also checks that the `data-theme` and `prefers-color-scheme` blocks have not drifted apart — two copies of one palette being the obvious way this breaks later. Low stimulation here is about surfaces, not text: muting the text too would hurt exactly the readers this is for.

## Things you cannot see from inside this repository

- **The Stimpunks Knowledge System mirrors this site** into `site/penguinpebbling.app/` and logs work here through its update-logs skill. Both live in that repository, not this one.
- **That mirror reads `/search-index.json` to get the card prompts**, because the prompts appear in no HTML — they are drawn by `penguin-pebbling.js` at runtime. If the deck or the page structure changes, the mirror and its `expect_min` of 5 may need attention. This is the reason `search-index.json` exists.

## Links out

**Links to autisticrealms.com stay.** The citations, the practitioner guide, and the shop link are credit and livelihood. "No dependencies on autisticrealms.com" was about assets — nothing should *break* if her site moves — and never about removing her from the page.
