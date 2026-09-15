# CLAUDE.md — Penguin Pebbling

Guidance for Claude Code working in this repository.

## What this is

**Penguin Pebbling** ([penguinpebbling.app](https://penguinpebbling.app/)) is a neuro-affirming card game by **Helen Edgar** (Autistic Realms) and **Ryan Boren** (Stimpunks), published first at Autistic Realms and given its own site here. Thirty cards across the Five Autistic Love Locutions, playable in the browser or printable as a deck.

Read `README.md` for the layout, `ATTRIBUTIONS.md` for who owns what, and `DECISIONS.md` for what was chosen during the import and what is still open. **`DECISIONS.md` has three open items and all three are Helen's to answer** — the card text under the art, re-setting the deck as text, and the licence (that last one jointly with Ryan). Check it before proposing anything that touches the card presentation or the licence.

## Two people work here

Helen Edgar and Ryan Boren both have rights to this work. **So *you* is whoever is at the keyboard, and it is never safe to guess.** Ask which one only when the answer changes the work — a byline, an attribution, whose call a design decision is. It usually does not.

**Helen's design decisions are Helen's.** The palette, the card artwork, the type, the wording of the prompts. Propose, do not apply. The one place this was already stretched — rendering the card prompt as text under the art — is written up in `DECISIONS.md` as an open item precisely because it is a visible change to her game.

## House rules

- **Capitalize Autistic and Disabled. Identity-first language** — "Autistic person", never "person with autism". This is not a style preference; it is the community's own usage and the whole site is written in it.
- **Horizontal rules in Markdown are `----`, four dashes.** YAML fences stay at three.
- **One line per paragraph in Markdown.** No hard-wrapping prose; let the editor soft-wrap. `DECISIONS.md`, `ATTRIBUTIONS.md` and `CHANGELOG.md` are written this way; parts of `README.md` predate the rule.
- **British spelling** in page copy — Helen's, and the published text uses it (*centre*, *recognise*, *journalling*).
- **Never hand-edit a generated file.** See below — there are three of them now, and each has a tool that will overwrite it.

## Generated files — never edit these by hand

| File | Generated from | By |
|---|---|---|
| `cards/` (35 WebP) | `cards/print/` (the PNG masters) | `tools/make-images.py` |
| `changelog.html` | `CHANGELOG.md` | `tools/build-changelog.py` |
| `search-index.json` | `penguin-pebbling.js` | `tools/make-search-index.py` |
| `og-image.png` | drawn from scratch | `tools/make-og-image.py` |
| the nav and footer in every page but `index.html` | the marked blocks in `index.html` | `tools/sync-shell.py` |

Edit the source on the left-hand side, then run the tool. An edit on the right is lost on the next run, silently.

## The shape of the site

**Six pages, not one.** `index.html` is the game and a short list of links; `how-to-play.html`, `locutions.html`, `print.html`, `about.html` and `changelog.html` hold everything else, reached from a `<details>` **Menu** in a sticky bar. It was one long page for a day, with the game buried under a thousand words — `DECISIONS.md` has the reasoning.

The nav and footer are authored once in `index.html`, between `<!-- shell:nav -->` and `<!-- shell:footer -->` markers, and stamped into the other five by `tools/sync-shell.py`. **Edit the nav in `index.html` and then run the tool** — editing it in `about.html` is editing a copy.

Alongside them: `penguin-pebbling.css` (one stylesheet), and **two scripts** — `penguin-pebbling.js` (the thirty cards and the game logic) and `theme.js` (light/dark, deliberately loaded from `<head>` without `defer` so the theme lands before first paint).

## The tools

Seven, all Python, all run by hand, none wired into a build. Four take `--check`, which reports drift and writes nothing.

| Tool | What it does | `--check`? |
|---|---|---|
| `tools/sync-shell.py` | stamps the nav and footer into every page | yes |
| `tools/check-contrast.py` | every colour pair, both themes, against WCAG AA | it only ever checks |
| `tools/build-changelog.py` | renders `CHANGELOG.md` into `changelog.html` | yes |
| `tools/make-search-index.py` | publishes the deck's text at `/search-index.json` | yes |
| `tools/set-domain.py` | rewrites the site's own address everywhere at once | yes |
| `tools/make-images.py` | regenerates `cards/` from `cards/print/` | no |
| `tools/make-og-image.py` | regenerates `og-image.png` | no |

`make-images.py` and `make-og-image.py` need Pillow; if it is missing they say so and name the `pip` line. **A tool that could not run has not run** — do not report a check as passing because it printed an error.

`build-changelog.py` understands a deliberately small Markdown dialect and treats anything else as a **hard error rather than a silent drop**. That is on purpose: a changelog that quietly loses an entry still looks fine.

## Verifying a change

There is no test suite. There are five checks, and they are fast — run them all before calling anything done:

```bash
python3 tools/sync-shell.py --check
python3 tools/check-contrast.py
python3 tools/build-changelog.py --check
python3 tools/make-search-index.py --check
python3 tools/set-domain.py --check
```

Then serve the folder and actually look at it. `.claude/launch.json` configures the preview server, so in Claude Code just start the `penguin-pebbling` preview; it runs:

```bash
npx -y serve . -l 8913 --no-clipboard
```

`python3 -m http.server 8913` also works here and serves every asset type the page uses with the right content type — verified 2026-09-14. Neither server is a dependency of the site; nothing is installed into the repository and `npx serve` is a dev-time convenience only.

Check the console is clean, draw a few cards, exercise the locution filters, toggle dark mode, and look at it at 375px wide. The card art is fixed-width lettering; the text beneath it is what has to reflow.

## Deploying, and why the live page never matches the repo

**Netlify deploys from `main`, so pushing publishes.** There is no staging step. Treat a push as the publish it is.

Netlify's **Pretty URLs** rewrites the served HTML: `href="how-to-play.html"` goes out as `href='/how-to-play'`, double quotes become single, attribute order shifts. `skip_processing = true` in `netlify.toml` does not cover it. So **a diff of the live HTML against this repository will never be clean — verify what a page *does*, not that its bytes match.** `DECISIONS.md` has the detail, including why the canonical and sitemap are extensionless while the source hrefs keep their `.html`.

## No build step, and keep it that way

No npm, no bundler, no framework, no CDN, no analytics, nothing fetched from a third party at runtime. `_headers` ships `default-src 'none'`, and **adding any third-party resource means editing the CSP, which is the signal to stop and ask whether it is worth it.**

**There is a webfont, and it is self-hosted.** Atkinson Hyperlegible Next lives in `fonts/` — four woff2 files, about 111 KB, with its OFL licence text, which must travel with them. Self-hosting is not incidental: `font-src 'self'` means a Google Fonts `<link>` would be blocked by the site's own policy, silently falling back to the system font while looking fine in a local test — and fetching a font at runtime would tell a third party who is reading a page about Autistic identity. See `fonts/README.md`.

## Accessibility is the product, not a pass at the end

The audience is Autistic and otherwise neurodivergent people, many using screen readers, zoom, reading fonts, AAC, or translation. Anything that makes the page harder to operate is a defect in the game, not a cosmetic issue.

Already in place and worth not regressing: full prompt text in every `alt` (not a prefix), a skip link, real `<button>`s with `aria-pressed`, `aria-live` on the card area, visible focus rings, `prefers-reduced-motion`, `width`/`height` on every image, a type scale in `rem` so the reader's own browser text size is honoured, and a dark mode that follows the system in CSS alone so it works with JavaScript off.

**The prompts are lettered into the card artwork.** That is the standing accessibility problem here and the reason the text is also rendered beneath. Do not "simplify" by removing it without reading `DECISIONS.md` first.

**Contrast is measured, not eyeballed.** `tools/check-contrast.py` covers both themes and also checks that the `data-theme` and `prefers-color-scheme` blocks have not drifted apart — two copies of one palette being the obvious way this breaks later. Low stimulation here is about surfaces, not text: muting the text too would hurt exactly the readers this is for.

## Things you cannot see from inside this repository

- **The Stimpunks Knowledge System mirrors this site** into `site/penguinpebbling.app/` and logs work here through its update-logs skill. Both live in that repository, not this one.
- **That mirror reads `/search-index.json` to get the card prompts**, because the prompts appear in no HTML — they are drawn by `penguin-pebbling.js` at runtime. If the deck or the page structure changes, the mirror and its `expect_min` of 5 may need attention. This is the reason `search-index.json` exists.

## Links out

**Links to autisticrealms.com stay.** The citations, the practitioner guide, and the shop link are credit and livelihood. "No dependencies on autisticrealms.com" was about assets — nothing should *break* if her site moves — and never about removing her from the page.
