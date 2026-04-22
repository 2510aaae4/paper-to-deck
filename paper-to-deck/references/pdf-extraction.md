# PDF Figure & Content Extraction

Academic PDFs are adversarial. The same tool call that works perfectly on an arXiv preprint returns empty on a Lancet review, garbles a two-column IEEE paper, and hallucinates section boundaries in a Nature article. This reference documents the three-tier fallback strategy this skill uses and the publisher-specific traps each tier is designed to catch.

---

## The three-tier fallback

Always attempt tiers in order. Stop at the first one that returns usable output. A paper that needs tier 3 for figures might still yield a clean text extract via tier 1 — the strategies are per-artifact, not per-paper.

### Tier 0 · External extractor (docling)

Delegated to a maintained open-source library when available. `scripts/extract_paper.py` tries docling first (see `references/external-extractors.md` for rationale and install). Docling produces tight-cropped images, handles multi-column and facing-page layouts natively, and provides structured HTML for tables as a bonus.

**When Tier 0 wins:** primary research figures (K-M plots, schematics), facing-page figures (needs no special handling), most portrait tables.

**When Tier 0 silently misclassifies:** small logos and page-chrome icons get detected as figures; occasional figure-as-table or table-as-figure double classification; caption text is usually empty. These are filtered by the integration layer.

**Caption text never comes from the extractor.** The paper's own caption scan (Tier 2, below) is the source of truth. An extractor that classifies a page 8 region as both figure and table is disambiguated by which `Figure N` / `Table N` caption the paper actually has on its pages.

### Tier 1 · Embedded image objects
```python
for page in doc:
    for img in page.get_images(full=True):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        pix.save(f"fig-{i}.png")
```

**When it works:** arXiv preprints, conference papers compiled from LaTeX with `\includegraphics`, papers where figures are actual PNG/JPG objects embedded during typesetting.

**When it fails silently:** Elsevier (Lancet, Cell, NEJM), Wiley, Springer Nature. These publishers composite figures from vector paths, text, and shapes directly on the page. `get_images()` returns either an empty list or only the journal logo / footer ornaments.

**Signal that you're in failure mode:** `get_images()` returns 0 images on a paper that visibly has 4 figures, OR returns only images of size < 100 px on a side (those are logos/icons, not figures).

### Tier 2 · Caption-anchored page crop

Find where the figure *caption* sits on the page. The figure itself is the region directly above the caption.

```python
import fitz, re
fig_caption_pattern = re.compile(r"^\s*Figure\s+(\d+)[:\.]?", re.M)

for page_num, page in enumerate(doc, start=1):
    text = page.get_text()
    # Find all "Figure N:" captions on this page
    for m in fig_caption_pattern.finditer(text):
        fig_num = int(m.group(1))
        # Locate the caption's y-coordinate via the dict API
        caption_y = _find_line_y(page, m.group(0))
        # Crop from a reasonable top margin to just above the caption
        rect = fitz.Rect(20, 90, page.rect.width - 20, caption_y - 4)
        pix = page.get_pixmap(clip=rect, dpi=200)
        pix.save(f"fig-{fig_num:02d}.png")
```

The helper `_find_line_y`:
```python
def _find_line_y(page, needle_prefix):
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0: continue
        for line in b.get("lines", []):
            text = "".join(s["text"] for s in line.get("spans", []))
            if text.strip().startswith(needle_prefix):
                return line["bbox"][1]
    return None
```

**When it works:** Any paper where captions follow the figure (the usual layout). Tested on clinical-review and conference-proceedings papers across major publishers.

**Trap 1:** Multi-column layouts. If the figure spans both columns but the caption is one-column-wide, cropping from the caption's left edge cuts off half the figure. Solution: force the crop to span the full text-width of the page (`page.rect.width - 2 * margin`), not just the caption's bbox width.

**Trap 2:** Captions on the next page. Long papers with tight figure-caption pairing sometimes push a caption to the next page. Detect this by checking if the figure-shaped whitespace sits at the bottom of a page with no caption — use the previous page's figure region instead.

**Trap 3:** Captions using "Fig. N" / "Fig N" / "FIGURE N". Loosen the regex: `r"^\s*(?:Figure|Fig\.?|FIGURE)\s+(\d+)"`.

### Tier 2b · Facing-page figures

Some journals (NEJM most notably; also certain Lancet layouts, Nature Letter format) print figures as a **two-page spread**: the caption sits on one page, the figure itself sits on the **opposite page**. The caption typically contains the string `(facing page)` as a reader hint.

When the caption text matches `(facing page)`, do **not** trust the caption's y-coordinate as the anchor for cropping. Instead:

1. Detect the convention: `re.search(r"\(facing\s+page\)", caption, re.I)`.
2. Pick the candidate host page — usually the page **before** the caption page (`cap_page - 1`), because print pagination puts an even-numbered figure page opposite an odd-numbered caption page.
3. **Disambiguate with drawings density**: call `page.get_drawings()` on both neighbours (`cap_page - 1` and `cap_page + 1`) and pick the page with the higher count. This handles the edge case where the "facing page" is actually the next page (two-column spreads in some layouts).
4. Render the whole host page (there's no caption on that page to anchor against).

**Test case**: an NEJM phase-3 RCT paper (v0.3.2). Its Figure 2 caption was on page 9 with `(facing page)`; the actual forest plot was on page 8 (267 drawings vs page 9's 4 drawings). Tier 2 without facing-page detection silently produced a text-region crop of page 9 — the mistake was invisible until the operator actually looked at the image.

**How to detect the bug before a human sees it**: after extraction, run the rendered artifact through a cheap OCR pass (`pytesseract`). If the OCR returns mostly body text (words, sentences) rather than the structural elements a figure should have (axis labels, short subgroup labels, numeric confidence intervals), flag the extraction as suspect and fall back to rendering the whole host page.

### Tier 3 · Full-page render

```python
for fig_num, page_num in figure_locations:
    pix = doc[page_num - 1].get_pixmap(dpi=220)
    pix.save(f"page-{page_num:02d}.png")
```

The user crops manually from the rendered page. This is the unconditional fallback — it always produces *something*, at the cost of the user doing the cropping.

**When to go here directly:** The paper is a scanned historical article (no text layer), or the figure is tightly surrounded by paragraphs (mathematical proofs with inline diagrams, chemistry papers with reaction schemes embedded in prose).

Always include rendered pages as sidecars when tier 2 is used — if a crop is wrong, the user can re-crop from the full page PNG without re-running the script.

---

## Publisher-specific fingerprints

Use text hints from the first page to auto-select the tier:

| Publisher | First-page signal | Default tier | Gotchas |
|---|---|---|---|
| **arXiv** | `arXiv:` identifier in header/margin | Tier 1 | None major; preprint figures embed cleanly |
| **Elsevier** (Lancet, Cell, JAMA) | `1-s2.0-` in filename or `ScienceDirect` footer | **Tier 2 directly** | `get_images()` almost always returns empty |
| **Nature/Springer** | `nature.com` or `doi.org/10.1038/` in text | Tier 1 or 2 | Mixed; worth trying tier 1 first |
| **IEEE** | `©20XX IEEE` footer | Tier 2 | Two-column layout — see Trap 1 |
| **ACM** | `© 20XX ACM` or `ACM Reference Format:` | Tier 1 | Usually clean PDF from LaTeX |
| **PLOS / BMC / open-access** | `Creative Commons` in footer | Tier 1 | Usually clean |
| **Scanned / legacy** | No text layer (`page.get_text()` returns empty) | **Run OCR first** — `ocrmypdf input.pdf output.pdf` — then retry |

---

## Text extraction notes

Beyond figures, the same tier-logic applies to the paper's sections and tables.

### Sections

The naive pattern `^\s*(\d+(?:\.\d+)?)\s+([A-Z][A-Za-z \-&]{2,60})\s*$` catches most papers but fails on:
- **Lancet/Cell**: sections are typeset as smallcaps headers without numbers. Use font-size heuristic: any text run where `span["size"] > median_size * 1.25` and `span["flags"] & 2**4` (bold) is likely a section header.
- **Nature**: section labels are tiny eyebrow-style uppercase. Look for short all-caps runs under 60 characters.
- **Reviews**: may have no numbered sections at all — just thematic headers ("Mechanisms", "Diagnosis"). Fall back to the font-size heuristic.

### Tables

`Table N` captions are much more standardized than figures, and the caption sits **above** the table rather than below. Same tier logic, inverted crop direction:

```python
table_pattern = re.compile(r"(?m)^\s*Table\s+(\d+)[:\.\s]")
# For each match:
#   1. Find the caption line's y-coordinate via the dict API
#   2. Crop from slightly ABOVE the caption (to include it) to bottom of page
#   3. Render at 220 DPI
```

```python
rect = fitz.Rect(20, max(60, cap_y - 10), page.rect.width - 20, page.rect.height * 0.96)
pix = page.get_pixmap(clip=rect, dpi=220)
```

**Output**: save as `tables/tbl-NN.png` with a sidecar `tbl-NN.txt` containing the caption. This parallels the `figures/` directory.

**Do not** attempt to extract table content as structured rows from PDF text. Table text is rarely aligned reliably in a PDF text layer — columns get merged, headers drop, numeric cells interleave with labels. Snapshot the region as an image and let the deck-building stage decide how to use it:
- For slides, follow `anti-slop-academic.md` entry #8 (fifteen-row-table is slop — reformat to key-point chart or typography).
- For speaker notes, keep the caption as reference.
- For user review, the table image is the canonical artifact — they can decide if they want it on a slide or not.

**Edge case**: appendix / supplementary tables that appear after the reference list. The same caption-anchored extraction works, but flag these in the output so the deck-building stage knows they're supplementary. (Heuristic: caption is on a page after the "References" section starts.)

---

### Tier 2c · Landscape tables rotated on a portrait page

Medical journals (NEJM especially) frequently print dense tables in landscape orientation on physically portrait pages — the table is visually rotated 90° CCW so the long axis runs top-to-bottom of the printed page. The caption sits along what was the "top" of the landscape layout, which becomes the **left vertical edge** of the portrait page.

If you crop with the standard Tier 2 logic (caption at top, crop downward), you capture a narrow slice of row labels and miss the entire data region. Signature of the failure: the output PNG is unusually slim (low file size, few hundred px tall even at high DPI), and when opened shows only the leftmost 1–2 columns of the table.

**Two detection signals, combined:**

1. **Text direction vectors** (preferred when they're honest). Every span in `page.get_text("dict")` has a `dir` unit vector. For landscape CCW rotation, spans below the caption should return `(0, -1)`. Collect spans, vote: if ≥55% are non-horizontal, the table is rotated.

2. **Geometric signature** (fallback, critical for NEJM-style PDFs). In many medical journal PDFs, pymupdf reports `dir = (1, 0)` even for visually-rotated content — the rotation is baked into the rendering transform, not stored in the text orientation metadata. When direction voting fails, fall back to geometry:

   - `cap_y / page_height > 0.55` — caption sits in the bottom 45% of the page (portrait tables always have the caption near the top)
   - AND the y-range of body spans below the caption is narrow (< 200 px) — because what was the "body of the table" now lives on a narrow horizontal strip from pymupdf's perspective

   Both conditions together are a strong signature. Caption-at-bottom alone is too loose (short portrait tables can have captions halfway down the page).

**Handling (route C · PIL rotate):**

Once detected, render the full host page and rotate the resulting image 90° CW (for CCW-rotated content) so it reads normally:

```python
pix = page.get_pixmap(dpi=220)
pix.save(tmp_path)
from PIL import Image
img = Image.open(tmp_path)
# rotation=+90 means the source content was rotated 90° CCW on the page;
# PIL.rotate takes CCW angles, so we pass -rotation to undo.
img_readable = img.rotate(-rotation, expand=True, resample=Image.BICUBIC)
img_readable.save(out_path, optimize=True)
```

Alternative (route A, render-time rotation with `fitz.Matrix(1,1).prerotate()`) is slightly cheaper in bytes, but requires re-mapping caption coordinates into the rotated coordinate system to crop precisely. Route C is simpler, one PNG per table at trivial overhead, and a human can still re-crop from the `pages/page-NN.png` sidecar if needed.

**CW-rotated tables** (rarer — some older European layouts). Geometric signature inverts: caption at top but body y-range narrow. Detection requires an additional check I have not implemented — when encountered, fall through to Tier 3 and surface the caveat so the operator manually rotates.

**Test case**: a recent NEJM phase-3 trial's Tables 2 and 3 (efficacy on p.6, safety on p.10) were both landscape; direction vectors reported `(1, 0)` (signal 1 fails); geometric signal 2 fires cleanly (`cap_y / page_h ≈ 0.77` in both cases, body y-range ≈ 100 px). Rotated PIL output reads normally and fits a slide with standard figure-slide layout.

**Attribution note for slide content**: when using a rotated table on a slide, flag in the caption that the original orientation was landscape ("Landscape orientation in original — rotated here for reading"). This is not legally required but removes any "did they cheat on the figure?" confusion for the audience.

---

## Captions: the one thing to save as sidecar text

For every figure saved as `fig-NN.png`, also save its caption as `fig-NN.txt` in UTF-8. Captions are **critical context** for slide design:

- They tell you what the figure is actually showing (often the figure label alone is not enough).
- They contain citations, statistical details, and abbreviation expansions.
- They carry the paper's original attribution (author's voice) — useful when composing the slide's own caption.

Use the same caption-anchored extraction to get the caption text: find the line starting with `Figure N:`, then concatenate subsequent lines until a blank line or page break.

---

## Output contract

After successful extraction, `paper-to-deck` expects this layout under the project directory:

```
<project>/
├── paper.json          # {title, authors, year, venue, abstract, sections[], figures[], tables[], citations[]}
├── full_text.txt       # UTF-8 dump of the entire PDF text
├── figures/
│   ├── fig-01.png      # cropped figure image
│   ├── fig-01.txt      # caption, UTF-8
│   └── fig-02.png / .txt
├── tables/
│   ├── tbl-01.png
│   ├── tbl-01.txt
│   ├── tbl-02.png / .txt
│   └── tbl-03.png / .txt
└── pages/
    ├── page-05.png     # rendered host page for every artifact
    ├── page-07.png     # so user can re-crop manually if needed
    └── page-08.png
```

Each entry in `paper.json`'s `figures[]` / `tables[]` records:
- `num` — the artifact's number in the paper (Figure 1, Table 2, etc.)
- `caption` — full caption text (truncated to 500 chars in JSON; full text lives in sidecar .txt)
- `host_page` — the page the artifact was rendered from (1-indexed)
- `caption_page` — the page the caption appears on (differs from host_page for facing-page figures)
- `tier` — extraction method used: `"Tier 2 (caption-anchored)"` / `"Tier 2b (facing page, previous)"` / `"Tier 3 (full-page fallback)"`
- `image` — relative path to the PNG
- `image_width`, `image_height` — pixel dimensions

The `tier` field lets the deck-building stage know what to flag in the outline's "caveats" section. Tier 2b and Tier 3 crops may include unrelated text from the host page — the user should visually check these before the deck commits to them.
