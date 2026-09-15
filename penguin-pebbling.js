/* Penguin Pebbling — the card game.
 *
 * Helen Edgar, Autistic Realms & Ryan Boren, Stimpunks (2026).
 *
 * The deck below is the thirty cards as published at autisticrealms.com, parsed
 * out of the original page rather than retyped, so the wording is hers to the
 * character. `image` names a file in cards/ (WebP, shown) and cards/print/ (PNG,
 * the master). `prompt` and `aside` carry the same words that are drawn on the
 * card face — see ACCESSIBILITY in README.md for why holding both matters.
 */

const DECK = [
  { locution: "id", name: "Infodumping", image: "infodumping-1", prompt: "What brings you joy right now? Share as much or as little as you like.", aside: null },
  { locution: "id", name: "Infodumping", image: "infodumping-2", prompt: "What's something you know a lot about that you rarely get to talk about? This is your space.", aside: null },
  { locution: "id", name: "Infodumping", image: "infodumping-3", prompt: "What's a topic, video, book, or idea you're passionate about recently? This is your space to share.", aside: null },
  { locution: "id", name: "Infodumping", image: "infodumping-4", prompt: "Do you have a glimmer to share — maybe a sensory moment that brought you joy recently that surprised or delighted you?", aside: null },
  { locution: "id", name: "Infodumping", image: "infodumping-5", prompt: "Say or write a word, draw something, or show us an image or an object that represents something you love right now. Pass it round if you'd like.", aside: null },
  { locution: "id", name: "Infodumping", image: "infodumping-6", prompt: "Is there a passion or interest that people in your life don't always understand?\nYou don't need to justify it here.\nShare if you are comfortable.", aside: null },
  { locution: "pp", name: "Parallel Play", image: "parallel-play-1", prompt: "For the next 5–10 minutes, everyone is invited to do something that brings them joy — read, stim, doodle, hold your pebble, sit or move. No communication needed. Just be here together. When you are ready you can return to the group.", aside: null },
  { locution: "pp", name: "Parallel Play", image: "parallel-play-2", prompt: "What does parallel play or body doubling feel like for you?\nWhat moments do you think this is most helpful for you?", aside: null },
  { locution: "pp", name: "Parallel Play", image: "parallel-play-3", prompt: "Is there something you have been meaning to do for ages but just haven't been able to start?\nCan you invite someone to join you online or in person for accountability and low-demand presence?", aside: null },
  { locution: "pp", name: "Parallel Play", image: "parallel-play-4", prompt: "Do you find it easier to start or finish things — work, daily tasks, creative projects — when someone else is simply present, even if you're not communicating? Online or in person. What does that feel like for you?", aside: null },
  { locution: "pp", name: "Parallel Play", image: "parallel-play-5", prompt: "Is there someone in your life whose quiet presence helps you feel more settled or able to function?\nYou don't need to explain why — just notice if that's true for you. Think about how you might get more time and space for this in your life — it may be online or in person.", aside: null },
  { locution: "pp", name: "Parallel Play", image: "parallel-play-6", prompt: "Is there a place — physical or online — where you feel comfortable simply existing alongside others?\nWhat makes that space feel safe?\nIs there anything you want to change — you could share with the others if you want, or just reflect.", aside: null },
  { locution: "ss", name: "Support Swapping", image: "support-swapping-1", prompt: "Is there something you find genuinely easy that others often find hard?\nIs there anything you could offer freely to someone who needed it?", aside: "If this resonates, you might like to ask the group — does anyone have something to offer here?" },
  { locution: "ss", name: "Support Swapping", image: "support-swapping-2", prompt: "Is there something you wish someone would notice and offer to help with — without you having to ask?", aside: "If someone shares something they need and you have something to offer — pass them a pebble." },
  { locution: "ss", name: "Support Swapping", image: "support-swapping-3", prompt: "Can you think of a time someone helped you in a way that really worked for your needs?\nWhat made that support feel right?", aside: "You might like to sit with this for yourself — or share amongst those you are with." },
  { locution: "ss", name: "Support Swapping", image: "support-swapping-4", prompt: "Write, draw, or show one small thing you need today.\nYou don't have to show anyone.\nNaming needs is its own form of care.", aside: "First — notice this for yourself.\nThen — if you'd like, open it to the group." },
  { locution: "ss", name: "Support Swapping", image: "support-swapping-5", prompt: "Is there something you find hard to ask for, even when you need it?\nYou don't have to share why — just notice if something comes up for you.", aside: "If someone shares something they find hard to ask for and it resonates — pass them a pebble." },
  { locution: "ss", name: "Support Swapping", image: "support-swapping-6", prompt: "Has anyone ever supported you in an unexpected way that made a real difference?\nWhat did that feel like?", aside: "You might like to sit with this for yourself — or share amongst those you are with." },
  { locution: "pb", name: "Penguin Pebbling", image: "penguin-pebbling-1", prompt: "Have you ever come across something — a stone, a meme, a flower, a song, a photo — and immediately thought of someone?\nWhat was it, and who did you think of?", aside: "You might like to sit with this for yourself — or share amongst those you are with." },
  { locution: "pb", name: "Penguin Pebbling", image: "penguin-pebbling-2", prompt: "If you could offer the group a pebble right now — something small that says something about who you are or what you love — what would it be?\nA photo on your phone, a word, a sound, a real object — anything counts.", aside: "Pass it round if you'd like — or just hold it for yourself." },
  { locution: "pb", name: "Penguin Pebbling", image: "penguin-pebbling-3", prompt: "What kinds of things do you notice — physically or emotionally — that others might walk past?\nIs there something you have collected, saved, or held onto because it felt meaningful?", aside: "You might like to sit with this for yourself — or share amongst those you are with." },
  { locution: "pb", name: "Penguin Pebbling", image: "penguin-pebbling-4", prompt: "Is there a way you show care for people that they don't always recognise as care?\nWhat does it look like for you?\n\nDo you ever wish people understood that this was your way of saying —\nI care for you, I thought of you.", aside: "If this resonates, you might like to ask the group — does anyone else show care in ways that go unnoticed?" },
  { locution: "pb", name: "Penguin Pebbling", image: "penguin-pebbling-5", prompt: "Pass a real pebble to someone in the group whose presence you appreciate, or it might be someone you thought of this week and you can share later.\n\nNo words needed.\nThe pebble holds the meaning.", aside: null },
  { locution: "pb", name: "Penguin Pebbling", image: "penguin-pebbling-6", prompt: "Is there something that brings you joy that you would love to share with others?\n\nMaybe you have never quite found the right moment — or the right person.\nThis might be that moment.", aside: "First — notice this for yourself.\nThen — if you'd like, open it to the group." },
  { locution: "dp", name: "Deep Pressure", image: "deep-pressure-1", prompt: "What helps your nervous system settle?\nIt might be weight, pressure, texture, warmth, movement, sound, your environment — or something else entirely.", aside: "You might like to sit with this for yourself — or share amongst those you are with." },
  { locution: "dp", name: "Deep Pressure", image: "deep-pressure-2", prompt: "What are the specific tools or objects you reach for when your nervous system feels dysregulated?\nIt might be a weighted blanket, a fidget, a scent, a texture, a sound, a movement, or a comfort object.", aside: "First — notice this for yourself.\nThen — if you'd like, share with the group and consider creating your own sensory toolkit." },
  { locution: "dp", name: "Deep Pressure", image: "deep-pressure-3", prompt: "Take a few minutes to do something that helps your nervous system regulate — stim, rock, stretch, move, or snuggle under a blanket.\n\nNo commentary needed.\nJust be here, grounded together.\n\nWhen you are ready, return to the group.", aside: null },
  { locution: "dp", name: "Deep Pressure", image: "deep-pressure-4", prompt: "How well do you pick up on the internal signals your body sends — hunger, thirst, pain, fatigue?\nIs there anything that helps you tune in earlier?\nIs there anything you need right now?", aside: "You might like to sit with this for yourself — or share amongst those you are with." },
  { locution: "dp", name: "Deep Pressure", image: "deep-pressure-5", prompt: "Have you ever had to mask or hide what your nervous system needed — pretending you were fine when you weren't?\nWhat would it mean to have more space to honour your sensory needs openly?", aside: "You might like to sit with this for yourself — or share amongst those you are with." },
  { locution: "dp", name: "Deep Pressure", image: "deep-pressure-6", prompt: "Is there one thing your nervous system needs more of in your life?\nMore/less movement, more quiet/more sound, more time with interests or stimming — or something else entirely.", aside: "You don't have to share it.\nYou could write it down and keep it — as a small act of care for yourself." },
];

/* The five locutions, in the order they are introduced on the page. */
const LOCUTIONS = [
  { id: "all", label: "All cards" },
  { id: "id",  label: "Infodumping" },
  { id: "pp",  label: "Parallel Play" },
  { id: "ss",  label: "Support Swapping" },
  { id: "pb",  label: "Penguin Pebbling" },
  { id: "dp",  label: "Deep Pressure" },
];

const FOOTER =
  "Share in whatever way feels right for you \u2014 speaking, writing, drawing, " +
  "AAC, gesture, or any other form of communication";

let filter = "all";
let deck = [];
let pebbles = 3;

/* Fisher-Yates. The original shuffled with `sort(() => Math.random() - 0.5)`,
 * which is not a uniform shuffle — comparison sorts assume a consistent
 * comparator, and a random one leaves cards near where they started. On a deck
 * of six that is the difference between a prompt you have not seen and the one
 * you just answered. */
function shuffled(list) {
  const out = [...list];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

function refillDeck() {
  deck = shuffled(filter === "all" ? DECK : DECK.filter((c) => c.locution === filter));
}

/* The slug the artwork is filed under: "parallel-play-3" -> "parallel-play".
 * One illustration serves all six cards of a locution, because Helen drew it
 * that way — see tools/make-card-art.py. */
function locutionSlug(card) {
  return card.image.replace(/-\d+$/, "");
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

function renderCard(card) {
  const area = document.getElementById("card-area");
  area.replaceChildren();

  /* The card is built, not fetched. Helen letters her prompts into the artwork,
   * which is right for print and costs a screen reader, a translator, a
   * highlighter, a reading font and anyone at 400% zoom everything. Here the
   * words are words and only the drawings are pictures.
   *
   * Both images are decorative: the locution is named in text beside them and
   * the prompt is the prompt, so an empty alt is correct rather than lazy —
   * describing the penguin would make a screen reader read furniture before
   * content. */
  const slug = locutionSlug(card);
  const pcard = el("div", "pcard");
  pcard.dataset.locution = slug;

  const left = el("div", "pcard-text");
  const pebbles = document.createElement("img");
  pebbles.src = "cards/art/pebbles.webp";
  pebbles.alt = "";
  pebbles.width = 200;
  pebbles.height = 220;
  pebbles.decoding = "async";
  pebbles.className = "pcard-pebbles";

  const locution = el("div", "pcard-locution", card.name);
  const prompt = el("div", "pcard-prompt");
  /* A blank line in a prompt is a paragraph break, a single one is a line break.
   * Helen set them that way on the cards and the rhythm is part of the prompt. */
  card.prompt.split("\n\n").forEach((para) => {
    const p = document.createElement("p");
    para.split("\n").forEach((line, i) => {
      if (i) p.append(document.createElement("br"));
      p.append(document.createTextNode(line));
    });
    prompt.append(p);
  });
  left.append(pebbles, locution, prompt);

  if (card.aside) {
    const extra = el("div", "pcard-prompt");
    const p = document.createElement("p");
    p.textContent = card.aside.replace(/\n/g, " ");
    extra.append(p);
    left.append(extra);
  }
  left.append(el("div", "pcard-aside", FOOTER));

  const right = el("div", "pcard-art");
  right.append(el("div", "pcard-title", "Penguin Pebbling Game"));
  const art = document.createElement("img");
  art.src = "cards/art/" + slug + ".webp";
  art.alt = "";
  art.width = 560;
  art.height = 770;
  art.decoding = "async";
  right.append(art);
  right.append(el("div", "pcard-credit", "Autistic Realms & Stimpunks \u00a9 2026"));

  pcard.append(left, right);
  area.append(pcard);
}

function clearCard() {
  const area = document.getElementById("card-area");
  area.replaceChildren(
    el("div", "card-empty", "Press \u201cDraw a card\u201d to begin \u{1FAA8}")
  );
}

function drawCard() {
  if (!deck.length) refillDeck();
  renderCard(deck.pop());
}

function setFilter(id) {
  filter = id;
  document.querySelectorAll(".fbtn").forEach((b) => {
    const on = b.dataset.id === id;
    b.classList.toggle("on", on);
    b.setAttribute("aria-pressed", String(on));
  });
  refillDeck();
  clearCard();
}

function updatePebbles() {
  const held = document.getElementById("pebbles-display");
  held.textContent = pebbles > 0 ? "\u{1FAA8}".repeat(pebbles) : "\u2014";
  held.setAttribute(
    "aria-label",
    pebbles === 1 ? "You are holding 1 pebble" : `You are holding ${pebbles} pebbles`
  );
  /* The bank never runs out. That is the rule, not a display cheat. */
  document.getElementById("bank-display").textContent =
    "\u{1FAA8}".repeat(10) + " always replenishing";
}

function passPebble() {
  if (pebbles <= 0) return;
  pebbles--;
  updatePebbles();
}

function takePebble() {
  pebbles++;
  updatePebbles();
}

function init() {
  const row = document.querySelector(".filter-row");
  LOCUTIONS.forEach(({ id, label }) => {
    const b = el("button", "fbtn" + (id === "all" ? " on" : ""), label);
    b.type = "button";
    b.dataset.id = id;
    b.setAttribute("aria-pressed", String(id === "all"));
    b.addEventListener("click", () => setFilter(id));
    row.append(b);
  });

  document.getElementById("btn-draw").addEventListener("click", drawCard);
  document.getElementById("btn-skip").addEventListener("click", drawCard);
  document.getElementById("btn-pass").addEventListener("click", passPebble);
  document.getElementById("btn-take").addEventListener("click", takePebble);

  refillDeck();
  clearCard();
  updatePebbles();
}

document.addEventListener("DOMContentLoaded", init);
