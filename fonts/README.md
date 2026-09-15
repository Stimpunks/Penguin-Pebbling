# Fonts

## Atkinson Hyperlegible Next

The page is set in **Atkinson Hyperlegible Next**, designed by the Braille Institute of
America specifically to be legible to readers with low vision. It differentiates the letter
shapes that are most often confused with one another — capital I, lowercase l and the digit 1;
capital O and zero; b, d, p and q — rather than treating them as a set of mirrored forms.

That is the right default for this site rather than a decorative choice. The audience is
Autistic and otherwise Disabled and Neurodivergent people, a good number of whom read with
low vision, with a screen magnifier, or with the kind of visual fatigue that makes ambiguous
letterforms expensive.

**Next**, released 2024, is the successor to the original Atkinson Hyperlegible: more weights,
a variable axis, and much wider language coverage.

### The files

Four, about 111 KB in total:

```
atkinson-hyperlegible-next-roman-latin.woff2        34 KB
atkinson-hyperlegible-next-roman-latin-ext.woff2    19 KB
atkinson-hyperlegible-next-italic-latin.woff2       37 KB
atkinson-hyperlegible-next-italic-latin-ext.woff2   20 KB
```

Each is a **variable font carrying the whole 200–800 weight axis**, so one file per style
covers regular, semibold and bold — there is no separate file per weight to forget. The italic
is a real drawn italic, not an oblique, which is why `font-synthesis: none` is safe to set.

`latin` covers the page; `latin-ext` is loaded only if a character needs it, via `unicode-range`.

### Self-hosted, and that is not incidental

`_headers` sends `default-src 'none'` with `font-src 'self'`. A `<link>` to Google Fonts would
be blocked by the site's own policy, silently, and the page would fall back to the system font
while looking fine in a local test. **Fetching a font at runtime also tells a third party who
is reading a page about Autistic identity.** Neither is a trade worth making for a 111 KB file.

### Licence

SIL Open Font License 1.1 — see `AtkinsonHyperlegibleNext-OFL.txt`, which is the licence text
as shipped upstream and must travel with the font files.

Copyright 2020-2024 The Atkinson Hyperlegible Next Project Authors.

- Upstream: <https://github.com/googlefonts/atkinson-hyperlegible-next>
- About the typeface: <https://www.brailleinstitute.org/freefont/>

The woff2 files here are the subsetted builds Google Fonts serves, retrieved 2026-09-14.
