# Changelog

Notable changes to Penguin Pebbling — both the **game** (the cards, the prompts, how a card is shown) and the **site** ([penguinpebbling.app](https://penguinpebbling.app/)). Newest first; dates are the day a change went live. The site deploys continuously, so there are no version numbers.

Each dated entry is split into **Game** and **Site**. An entry only carries the sections that changed.

## 2026-09-15

### Site

- **The site now publishes [an index for language models](https://penguinpebbling.app/llms.txt).** The thirty card prompts are drawn into the page by script and appear in nothing that reads the HTML, so anything summarising this site was getting the furniture and none of the game. The index says so in as many words and points at the prompts, which have been published as data since yesterday. It is generated from the pages themselves, so it cannot quietly fall out of date.

## 2026-09-14

### Game

- **Penguin Pebbling has a home of its own.** The game was published at [Autistic Realms](https://autisticrealms.com/penguin-pebbling-a-game-of-creating-belonging-building-connection-and-understanding-autistic-identity/) in May 2026, as a post with the playable half folded into a single block of HTML. It moved here whole: all thirty prompts, all thirty-five card faces, and the three printable guides, unchanged. The original post stays where it is.
- **Every card's prompt is now shown as text as well as lettered into the artwork.** The words are drawn into the card, which is right for print and costly on a screen — lettering cannot be zoomed on its own, reflowed, set in a reading font, selected, copied, or read aloud by a screen reader picking its way through a page. The card is still the card; the same words sit underneath it, and the alt text carries the whole prompt rather than the first hundred and fifty characters.
- **Cards are properly shuffled.** The deck was being sorted by a coin flip, which is not the same as shuffling: cards stayed near where they started. On a single-locution filter of six cards, that meant being handed back the prompt you had just answered.

### Site

- **Everything the game needs is served from here.** Thirty-five card images and three PDFs came across, so nothing on this site depends on autisticrealms.com staying where it is. Links to Helen's writing and her shop point at her site, because that is where they belong.
- **The game is the front page.** For a day it sat below about a thousand words of introduction — you had to scroll past the explanation to reach the thing being explained. [How to play](https://penguinpebbling.app/how-to-play), [the five locutions](https://penguinpebbling.app/locutions), [print and download](https://penguinpebbling.app/print) and [about](https://penguinpebbling.app/about) have their own pages now, in the menu at the top.
- **Set in Atkinson Hyperlegible Next**, the Braille Institute's typeface for readers with low vision, self-hosted so no third party learns who is reading. Every size went up, and the scale follows the reader's own browser text-size setting rather than overriding it.
- **A sage palette, and a dark mode.** Sage is Helen's colour, and it keeps this site from looking like our others. The ground and all five locution tints are sampled from her own card artwork rather than picked to match. Dark mode follows your device and can be overridden with the toggle in the bar; the choice is remembered on your own device and never leaves it.
- **The printable deck, the Plain Language guide and the Easy Read guide** are all hosted here and free.
- **A privacy page, and there is very little on it.** A game used by families, schools and clinics should be able to say plainly what it does with your data, so now it does: nothing. No accounts, no cookies, no analytics, no third parties, and the only thing kept on your device is your light or dark choice — which is never sent anywhere, and is not stored at all unless you touch the toggle. [Privacy](https://penguinpebbling.app/privacy) is linked from the foot of every page.
- **Fixes:** shared links were showing no preview image, the page was telling search engines to index an address that did not exist yet, a stale stylesheet could survive a day after a change, and a corrected card image would have sat in readers' caches for a year with no way to replace it. All four are corrected.
