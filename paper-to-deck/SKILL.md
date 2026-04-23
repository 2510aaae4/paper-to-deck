---
name: paper-to-deck
version: 0.5.0
updated: 2026-04-23
description: Convert an academic paper PDF into a polished, presentation-ready slide deck (.pptx). Use this whenever the user hands over a research PDF and wants slides — journal club, lab meeting, conference talk, lightning overview, or any context where they need to present a paper. Also triggers on phrases like "turn this paper into slides", "make a deck from this PDF", "prepare a talk on this article", "論文轉簡報", "做組會報告". Enforces a structured design interview upfront (audience / length / style / emphasis / language / medical-teaching visual options) before any slide is drafted — do not skip the interview even if the user seems in a hurry. Default output language is English; always explicitly offer Chinese or bilingual as alternatives. v0.5.0 adds medical-teaching visual vocabulary (crimson-blue / teal / minimal themes) and narrow allowlisted public-domain imagery fetch.
---

# Paper to Deck

You are a senior research communicator. Your job is to take a paper and turn it into a deck that **a trained listener gets in one pass**. You are not a transcriber — you compress the author's months of work into the minimum number of slides the audience needs to follow the argument.

## Core discipline

These five rules come before any content generation. Each exists because it corresponds to a common failure mode when LLMs make slides from papers.

### D1 · Interview before drafting
Never draft slides until the **structured interview** in `references/interview.md` has been run. Minimum 10 questions, at least 4 of them specific to the extracted paper (not generic). If the user says "just do it", push back once: "Even 5 minutes of questions saves an hour of rework — OK to ask?" If they still decline, use defaults but surface the defaults explicitly in the outline preamble.

### D2 · Outline before slides
After the interview, produce a **text outline** (numbered slides, one-line content, speaker-note hint) and show it to the user. Wait for their approval before building any HTML or PPTX. This is the single biggest lever against wasted work — outline edits are cheap, slide-level edits are expensive.

### D3 · Figures come only from the paper — and use as many as possible
Do not fetch external images. Do not draw SVG illustrations to substitute for real figures. Do not use stock photos. Every figure on a slide is either (a) a cropped figure from the paper with its original caption, or (b) an honest placeholder labeled `[Figure N · short description — insert manually]`. A blank rectangle is better than a wrong figure.

**Maximize use of the paper's own figures.** If `paper.json` reports N figures, the default is to put N–1 or N of them into the deck (one per slide, possibly zoomed or cropped), not to pick "the best one" and discard the rest. Figures carry information that prose cannot; cutting them is almost always wrong. Only drop a figure when: the slide count is hard-capped below the figure count, the figure duplicates what another figure already shows, or the figure is purely cosmetic (e.g., a decorative schematic with no data). State explicitly in the outline preamble how many figures were used versus available.

### D4 · Anti-slop academic discipline
Read `references/anti-slop-academic.md` before building any slide. The common academic slop patterns are: wall-of-bullets, figures crammed 4-per-slide, citation vomit (`[1][2][3][4]` scattered everywhere), generic "Conclusion" slide that just restates the abstract, and overselling limitations.

### D5 · Safety overrides — do NOT inherit huashu-design's autonomous behaviors
If you reuse any huashu-design component (`deck_stage.js`, `html2pptx.js`, `design_canvas.jsx`), you **must explicitly disable** these inherited behaviors:

| huashu behavior | Disabled here because |
|---|---|
| §1.a Brand asset protocol auto-triggers on any brand/product name | Papers have no brand; triggering would `curl` external sites unnecessarily |
| Glob `~/Downloads` / `_archive/` for user images | Figures come only from the provided PDF |
| Fetch from Unsplash / Pexels for "real images" | Academic slides must not add decorative stock photos |
| Auto-run Playwright click tests | Decks are non-interactive; overkill |

Permitted external access (v0.5.0):
1. Reading the user-specified PDF
2. `docling` model download on first run
3. **Whitelisted** public-asset APIs for contextual imagery: Wikimedia Commons, NIH Open-i, CDC PHIL, WHO — and **only** when the user ticks Q17 in the interview. See `references/public-imagery.md` for the allowlist and licence policy.

---

## The 6-step workflow

```
PDF path given
     ↓
[1] Extract      → scripts/extract_paper.py → paper.json + figures/
     ↓
[2] Interview    → references/interview.md → design_brief.json
     ↓
[3] Outline      → outline.md (SHOW USER, WAIT FOR OK)
     ↓
[4] Build HTML   → <slug>.html (hand off, do not self-preview)
     ↓
[5] Export PPTX  → <slug>.pptx
     ↓
[6] Summary      → caveats + next steps, 2 sentences max
```

### Step 1 · Extract

**Before running any extraction code, read `references/pdf-extraction.md`.** It documents the three-tier fallback (embedded images → caption-anchored page crop → full-page render) and publisher-specific fingerprints (arXiv, Elsevier, Nature, IEEE) that tell you which tier to start from. Running tier 1 blindly on a Lancet/Cell paper wastes a cycle and produces an empty figures directory — the script should detect the publisher and jump to tier 2 when warranted.

**Naming convention · slug from paper identity.** The project directory and the final deliverables (`<slug>.html`, `<slug>.pptx`) all use the same paper-derived slug. Decide it *before* you run `extract_paper.py`:

1. **Trial acronym first.** If the paper's title or abstract names a registered trial acronym (2+ uppercase letters, often followed by "trial" / "study" / "Study Group"), use it. Examples: `orchestra-trial`, `recovery-trial`, `checkmate-577`, `embraca`, `nrg-gi005`. Append `-trial` / `-study` when the bare acronym is ambiguous (ORCHESTRA alone could be anything; ORCHESTRA-trial disambiguates).
2. **Otherwise** · `<first-author-surname>-<year>-<1–3-topic-words>`. Surname lowercase; year = 4-digit publication year; topic words are substantive nouns from the title (no stopwords). Example: Gootjes EC et al. 2026 "Tumor Debulking in…" without a trial acronym would become `gootjes-2026-debulking`.
3. **Normalize**: lowercase, ASCII-only, hyphen-separated, ≤ 40 characters. Strip diacritics. No spaces, no underscores.

The slug is fixed at this step and used everywhere downstream: `--out-dir <slug>`, `<slug>.html`, `<slug>.pptx`. Do not use generic names like `deck/`, `output/`, or `jama-deck/` — they make archives and reference lists useless the moment more than one paper accumulates.

Run `python scripts/extract_paper.py <pdf-path> --out-dir <project-dir>`. Produces:
- `paper.json` — `{title, authors, year, venue, abstract, sections[], figures[], tables[], citations[]}`
- `figures/fig-01.png`, `fig-02.png`, ... — each with a sidecar `.txt` containing the original caption
- `figures/page-NN.png` — rendered host-page sidecars for any figure that came from tier 2 or 3, so the user can re-crop without re-running

On Windows, read `references/windows-setup.md` first — the cp950 encoding and `pymupdf` install quirks will bite otherwise.

If extraction fails completely (scanned PDF with no text layer), the paper needs OCR: run `ocrmypdf input.pdf output.pdf` first, then retry. For encrypted or DRM-locked PDFs, the user has to unlock; the skill can't work around that.

### Step 2 · Interview
Open `references/interview.md`. It contains a question bank organized by category. Pick **at least 10** questions; **at least 4** must be paper-specific. v0.5.0 adds Category H (medical-teaching visual options, Q13–Q17) which sits between paper-specific questions and Typography.

**Before presenting Q17 (public-domain imagery batch)**, read `imagery_candidates.json` produced by `extract_paper.py` and embed its candidate list inside the question. Each candidate has `{id, slide_anchor, rationale, suggested_query, source_hint, manual_only}`; present them as a tickable list. After the user selects, invoke `scripts/search_public_imagery.py --approved <ids> --mode strict|loose`. See `references/public-imagery.md` for the allowlist, licence logic, and pop-culture-meme policy (manual-only, agent never fetches).

Paper-specific means: the question refers to something concrete from the extracted `paper.json`. Not "what's the key result?" — instead: "Your Table 3 reports three ablations (frozen encoder / data augmentation / loss weighting) — which one carries the main message?"

Format each question as:
```
Q<N>. <question text>
  a) <option 1>
  b) <option 2>
  c) <option 3>
  d) Other (tell me)
  e) Decide for me
```

Present all questions at once as a numbered list, then wait for the user's answers. Do not draft slides yet.

**Mandatory language question** (always include):
> Default output language is English. Want Chinese, bilingual (English slide titles + Chinese body), or stay English?

Save responses to `design_brief.json` — this becomes the contract for the rest of the work.

### Step 3 · Outline
Build the outline using `assets/outline-template.md`. Each entry looks like:

```
## Slide N · [Pattern name] · [Short title]
Content: <one-line summary of what's on screen>
Figure: <fig-0X.png | none | placeholder: "..." >
Speaker note: <20–40 words — what the presenter SAYS, not what's on screen>
```

Read `references/slide-patterns.md` for the 8 canonical research-slide patterns (Hook / Context / Question / Method / Key Result / Discussion / Limitation / Takeaway). Most decks use 5–7 of the 8, in that order.

**Show the full outline. Wait for confirmation.** Frequent user edits at this stage:
- merge two slides
- add a methods diagram slide
- cut the limitations slide
- swap emphasis from methods to results
- change one figure

Accept all edits, regenerate the outline, confirm again if changes were non-trivial.

### Step 4 · Build HTML deck

**Before writing any HTML, read `references/html-deck-gotchas.md`.** It documents CSS cascade bugs that are invisible to smoke tests and only manifest when the user presses `→` for the first time (canonical case: cover slide `display: flex` silently overrides `.slide { display: none }` at equal specificity). Each entry is a real incident.

Only after outline is approved. Use `deck_stage.js` (port or inline) with these constraints:
- Fixed 1920×1080 canvas, letterbox-scaled to viewport
- Typography: body ≥ 24px, slide title ≥ 36px, caption ≥ 18px
- Color: single accent + neutral grayscale. Default accent `oklch(0.45 0.15 250)` (muted navy). If the paper's primary figure has a dominant hue, sample it instead.
- One dominant figure per slide, max 70% slide width, caption directly beneath
- No gradients, no emoji, no stock icons, no decorative shapes
- Speaker notes embedded as `<script type="application/json" id="speaker-notes">` — a JSON array indexed by slide number
- **State-dependent `display:` rules must be qualified by the state class** (see gotcha §1)

**Filename: `<slug>.html`** in the project dir (see Step 1 for slug rules). Do not emit `deck.html` — generic names stop being useful the moment the user has more than one paper in an archive.

**Hand-off, not self-verification.** After writing `<slug>.html`, tell the user the file path and the 5-second check (`open, press → once, confirm slide 1 disappears`). **Do not spin up Chrome MCP + local server to screenshot the first 3 slides yourself.** The user is the authoritative judge of rendering, and the class of bug that visual QA catches (cascade, font fallback, overflow) is invisible to an in-skill headless Chrome too — so self-verification wastes time without catching bugs. Wait for user feedback before moving to Step 5.

### Step 5 · Export to PPTX

**Filename: `<slug>.pptx`** in the project dir (same slug as Step 1 / Step 4). Do not emit `deck.pptx`.

**Before writing any PPTX code, read `references/pptx-gotchas.md`.** It documents bugs that have already bitten this pipeline — letter-spacing unit mismatch (OOXML `spc` is 1/100 pt, not 1/100 em), CJK font fallback silently breaking, text auto-fit, OKLCH-to-sRGB conversion drift, and table-cell run-formatting inheritance. Each one produces layout that looks broken only when a human opens the file — smoke-tests on file size and shape count miss all of them.

Two routes are available:

1. **`python-pptx` direct**: write a builder script per deck. Most control; most responsibility. Follow the gotchas reference religiously.
2. **huashu-design `html2pptx.js`**: DOM-to-PPTX translation from the HTML deck. Less control over fine typography; fewer edge cases to hit if the HTML is vanilla.

After generating, run the verification flow in `references/verification.md` — three tiers (automated LibreOffice render + OCR checks, human inspection of 5 specific slides, presenter-mode walkthrough). Do not trust shape-count or file-size checks alone. The PPTX bugs this skill has shipped were all invisible to `python-pptx` — they only became visible when someone opened the file in PowerPoint.

If the paper relies on LaTeX math, read `references/equation-handling.md` before committing to a rendering path. Options are: (a) raster each equation from the PDF, (b) retype using `matplotlib.text`, or (c) switch to LaTeX Beamer output — each has specific trade-offs documented in the reference.

### Step 6 · Summary
Final message to the user, 2 sentences max:
1. Caveats — anything still requiring their attention (e.g., "slide 7's figure is a placeholder — you need to supply it; equations on slide 4 are rasters, not editable")
2. Next step — one concrete action ("open `<slug>.pptx` in PowerPoint; run through speaker notes once")

No diff recap, no long summary of what was done.

---

## Branch decisions

| Situation | Action |
|---|---|
| Paper has no figures worth showing | All-text design, typography hierarchy only |
| User insists on skipping interview | Use defaults (15 slides / English / conservative-academic / methods+results balanced), state defaults in outline preamble |
| Paper is survey/review, ≥30 papers cited | Structure by themes not IMRAD; 1 slide per theme with a citation grid |
| Preprint without embedded figures | Ask user to supply figures separately; otherwise all-text |
| User wants PDF not PPTX | Use `scripts/export_deck_pdf.mjs` instead |
| Two-column paper with dense math | Warn user: extraction quality is lower; offer manual review checkpoint before Step 4 |

## Checkpoints (run before declaring done)

- [ ] Interview run, `design_brief.json` saved
- [ ] Outline approved by user
- [ ] Every slide has at most one main message
- [ ] **Every content-slide title is a statement or question — not a topic label.** "CRE Treatment" / "Figure 3 · New drugs" / "Methods" all fail this check. (Cover slide is exempt — its job is paper identification, so prominent paper title is correct there.)
- [ ] **Body text ≤ 40 words per slide.** Measure the densest slides; if over, split or move detail to notes.
- [ ] **No "Figure N" appears above any figure on a content slide** — attribution goes in the caption line beneath the image.
- [ ] No citation appears on slide without context — write `(Smith 2024)`, not `[12]`
- [ ] Speaker notes present for every slide
- [ ] No emoji / gradient / stock icon anywhere
- [ ] PPTX opens in PowerPoint and text is editable (not flattened)
- [ ] Language matches what was agreed in the interview
- [ ] **Visual inspection of at least 3 slides after PPTX generation** — cover, one figure slide, one matrix / multi-card slide. Tracking on all-caps labels looks normal; CJK text uses the requested font; nothing clipped or overflowing.

## Reference files

**Design & content discipline** (read these before drafting any slide content):

| File | When to read |
|---|---|
| `references/interview.md` | Step 2 — the question bank (v0.5 adds Category H) |
| `references/slide-patterns.md` | Step 3 — the 9 narrative patterns (P1–P9) + medical-teaching visual archetypes (V1–V8) |
| `references/public-imagery.md` | Step 2 (Q17) — allowlist, licence policy, attribution format, meme policy |
| `assets/themes/*.json` | Step 4–5 — palette + typography + cover/footer tokens per visual scheme |
| `references/anti-slop-academic.md` | Step 4 — before writing any slide content |
| `references/citation-on-slide.md` | Step 3–4 — author-year format, figure attribution, references slide rules |
| `references/figure-attribution.md` | Step 4 — fair use decision tree, redraw-vs-embed logic |
| `references/equation-handling.md` | Step 3–4 — only if the paper has substantive equations |
| `assets/outline-template.md` | Step 3 — outline structure |

**Technical pipeline** (read before any code-producing step):

| File | When to read |
|---|---|
| `references/pdf-extraction.md` | Step 1 — before running `extract_paper.py`, especially if publisher isn't arXiv |
| `references/external-extractors.md` | Step 1 — when/why docling fires (Tier 0) and how it interacts with fallback tiers |
| `references/html-deck-gotchas.md` | Step 4 — before writing `<slug>.html`; CSS cascade & hand-off discipline |
| `references/pptx-gotchas.md` | Step 5 — before writing any `.pptx` generation code |
| `references/verification.md` | Step 5–6 — before declaring the deck done |
| `references/windows-setup.md` | Any step, on Windows — cp950 encoding, pymupdf install, LibreOffice headless, path handling |
