# Deck Verification

A `.pptx` file that opens without errors is not the same as a deck that looks correct. Every PPTX bug this skill has shipped was invisible to `python-pptx` (no exception, no warning, file saved fine) and only became obvious when a human opened PowerPoint. This reference defines the verification gate that must run **before** declaring any deck done.

The bug history that motivates this reference:
- `spc` unit mismatch produced letter-spacing of 22pt per character. API succeeded. PowerPoint rendered labels with individual letters stretched across the slide like Scrabble tiles.
- Font-fallback caused CJK speaker notes to render in Calibri instead of Taipei Sans TC Beta. No error; wrong font silently.
- Text overflow clipped a 72pt title down to one line visible instead of three.

None of these are caught by shape-count, file-size, or "the file opens" checks.

---

## The three verification tiers

### Tier A · Automated visual rendering (fast, catches 80%)

Convert the PPTX to PNG with LibreOffice headless, then run a small set of checks on the rasters:

```bash
# Convert PPTX → one PNG per slide
soffice --headless --convert-to png --outdir verify_png/ deck.pptx

# Or: convert to PDF first, then rasterize each page
soffice --headless --convert-to pdf --outdir verify_pdf/ deck.pptx
pdftoppm -r 120 verify_pdf/deck.pdf verify_png/slide -png
```

**Automated checks on the rendered PNGs:**

1. **OCR-readable text count**: run `pytesseract.image_to_string()` on each slide. If a slide has <20 characters detected where the deck's outline says it has ≥80 characters of body text, something is wrong — likely overflow clipping or font not installed.

2. **Tracking sanity** (detects the `spc` bug): for any slide that has an uppercase label per the outline, check the OCR output contains the expected words as contiguous tokens. Blown tracking produces output like `C L I N I C A L   S Y N D R O M E S` — count spaces-between-letters ratio; if > 0.4, tracking is broken.

3. **Figure presence**: for every slide that `outline.md` says has a figure, the rendered PNG should have a region of non-background pixels larger than 400×300. Missing figure = white slide = broken image reference.

4. **Slide count**: match `outline.md`'s planned slide count to rendered PNG count.

A minimal script: `scripts/verify_deck.py`. Passing this tier covers the mechanical bug class.

### Tier B · Human visual inspection (mandatory, 5 slides minimum)

Automated checks can't tell if a slide *looks right*. The operator must open the deck in PowerPoint and actually look at:

1. **Slide 1 (cover)** — bibliographic info readable at projection size; paper title clearly identifying the work.
2. **One figure slide** (5, 8, 10, or 11) — figure not cut off, caption legible, no ghost text from the page-crop showing.
3. **One matrix/table slide** (6 or 12) — columns aligned, color-coded cells readable, no text wrapping weirdly within cells.
4. **One dense-content slide** (13, 14, or 15) — drug names on separate lines, bullets readable at ≥24px equivalent.
5. **Takeaway / closing slide** — typography mirrors opening, no accidental "Thank You" page slop.

For each, use this checklist:
- [ ] Typography: no letter exploded, no word-cut-in-half wrapping, no font fallback to Calibri for CJK
- [ ] Layout: nothing overlapping, no text touching slide edges, figures centered in their regions
- [ ] Color: accent color consistent across slides, not shifted into a different hue
- [ ] Speaker notes: visible in the notes pane, language matches what was agreed

### Tier C · Presenter mode walkthrough (5 minutes, once per deck)

Open the deck in PowerPoint's **Presenter Mode** (F5 / Slideshow → From Beginning) and click through all slides at talk pace. This catches:

- Animation or transition artifacts the static view hides.
- Slide-to-slide rhythm problems (three consecutive text-heavy slides = the audience will check out).
- Wrong aspect ratio issues (the deck renders in 4:3 when the room projector is 16:9, or vice versa).
- Navigation between slides that logically pair (e.g. matrix slide 12 should flow naturally into prose slide 13).

---

## What to do when verification fails

Triage by tier:

| Failure tier | Typical cause | Action |
|---|---|---|
| **A · Automated** | Mechanical bug (tracking, overflow, missing figure ref) | Fix the generator script, re-run, re-verify. Do not hand-fix in PowerPoint — it will be lost on next generation. |
| **B · Human inspection** | Content density, figure crop quality, typography feeling off | If it's a design decision (density) — adjust the outline, regenerate. If it's a figure crop (common with tier-2 PDF extraction) — re-crop with manually specified rect, or ask the user to supply the figure. |
| **C · Presenter walkthrough** | Narrative flow or pacing | This is usually fixable only with the user in the loop — flag specific slides and ask if they want to restructure. |

---

## What NOT to verify

Don't automate these checks — they produce false positives and waste cycles:

- **Exact pixel position** of text boxes. Minor shifts due to font metrics differences between systems are normal and invisible to viewers.
- **Color histograms** of the whole deck. Small variations from rendering engine differences (LibreOffice vs PowerPoint) will trip any strict check.
- **Font embedding**: whether the font is embedded is a different question from whether it renders correctly at build time. Address via `windows-setup.md`'s font-install guidance, not by aborting verification.

---

## The ritual before shipping

Every time you tell the user "deck is done", the chain must be:
1. Tier A script ran, all checks passed (save its output log in `verify/` as evidence).
2. You personally opened at least 5 slides per Tier B (cover, figure, matrix, dense, takeaway).
3. You ran at least one Tier C walkthrough.

The checkbox `[ ] Visual inspection of at least 3 slides` in `SKILL.md`'s closing checklist corresponds to the Tier B step. Tier A and Tier C are stronger — use them when the deck matters (conference talk, formal review, going external).

**Principle**: no automated test suite can fully replace an operator who has actually looked at the slides. Build the automation to save time on the obvious bugs, not to grant permission to skip looking.
