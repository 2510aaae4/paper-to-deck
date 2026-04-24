# PPTX Generation Gotchas

Technical pitfalls encountered when generating .pptx with `python-pptx`. Read this before writing any script that emits a `.pptx` — each entry is a bug caught in production that is easy to miss in code review and catastrophic in the rendered slide.

---

## 1 · Letter-spacing unit mismatch (spc in OOXML)

**Symptom**: All-caps labels render with letters stretched far apart, sometimes wrapping vertically (`C L I N I C A L` on separate lines). Occurs on eyebrows, kickers, abbreviation lines, small uppercase tags — any run with a tracking style.

**Cause**: OOXML's `spc` attribute (on `<a:rPr>`) is measured in **hundredths of a point**, not hundredths of an em. If you treat an input like `letter_spacing=22` (meant as "0.22em, typical for uppercase eyebrow") and naively multiply by 100 to get `spc="2200"`, you have just set 22 points of extra tracking between every character — roughly 2× the font size itself.

**Visible in**: HTML decks inherit `letter-spacing: 0.22em` which is CSS em units. Copying this value pattern into a PPTX builder without re-scaling is the most common route to this bug.

**Correct**: Use a multiplier of **~10**, not 100, when the input is in "em × 100" form. A 9 pt eyebrow with `letter_spacing=18` becomes `spc=180` = 1.8 pt between characters — subtle, readable, matches the HTML intent.

```python
# Bad — spc is in 1/100 pt, not 1/100 em
rPr.set("spc", str(int(letter_spacing * 100)))

# Good — converts em-ish input to 1/100 pt
rPr.set("spc", str(int(letter_spacing * 10)))
```

**Why this bug slips through unit tests**: python-pptx accepts any integer for `spc` without validation. The file saves. PowerPoint opens it. The bug is only visible when a human looks at the slide.

**How to detect before the human sees it**: Render the first slide to PNG with `libreoffice --headless --convert-to png` (or similar), scan for labels whose bounding box height exceeds their font's expected ascender height by >2×. Automate this as a smoke test.

---

## 2 · Font-fallback for CJK text

**Symptom**: English text renders in requested font (e.g., Taipei Sans TC Beta); Chinese text silently falls back to Calibri or system default, creating visually inconsistent runs within the same paragraph.

**Cause**: `run.font.name` only sets the Latin typeface. East Asian characters use a separate typeface slot declared in `<a:ea>` inside `<a:rPr>`. If you don't set it, PowerPoint uses the theme's East Asian font.

**Correct**: For every text run that may contain CJK, also set the `<a:ea>` (east-asian) and `<a:cs>` (complex script) typeface elements explicitly:

```python
rPr = run._r.get_or_add_rPr()
ea = etree.SubElement(rPr, qn("a:ea"))
ea.set("typeface", font_name)
cs = etree.SubElement(rPr, qn("a:cs"))
cs.set("typeface", font_name)
```

Do this for speaker notes too — notes inherit a different theme and will silently fall back to Calibri even when the main deck looks right.

---

## 3 · Text auto-fit vs. fixed box size

**Symptom**: Titles or body text overflow the textbox, getting visually truncated at the edge or behind other shapes. Worst on slides with long translated titles or auto-generated content.

**Cause**: python-pptx `add_textbox` creates a fixed-size shape with no auto-fit policy. Content that exceeds the box is clipped — there is no warning.

**Correct strategies**:
- For titles with known max length: size boxes generously (1.5× expected height) and enable `tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT`.
- For body text: use `tf.word_wrap = True` and leave vertical room.
- For slides with wildly variable content length: compute expected height from character count × line-height × line-width and resize the box programmatically before saving.

**Never** rely on "it looked fine in the first test case" — test with both a very short and a very long title.

---

## 4 · OKLCH color conversion

**Symptom**: HTML deck uses `oklch(0.45 0.15 250)` for accent; PPTX accent looks visibly different (usually more washed out or shifted hue).

**Cause**: python-pptx takes sRGB only (`RGBColor(0x2C, 0x41, 0x7A)`). Converting OKLCH → sRGB requires going through OKLab → linear RGB → sRGB with gamma correction. Doing this by eye produces mismatches of 5–10 ΔE.

**Correct**: Either (a) write the OKLCH value into a tiny HTML file and `getComputedStyle` it via headless browser to get the exact sRGB the user saw, or (b) use a Python colorspace library (`colour-science`, `coloraide`) for a principled conversion. Don't eyeball hex values.

**Quick formula** if you can't use a library: for any `oklch(L C H)`, a good approximation is to convert via the OKLab → XYZ D65 → sRGB chain documented in the OKLab paper. Values near the deck's accent range (muted navy / slate) are usually within 10 sRGB units of what a proper library returns.

---

## 5 · Table cells don't inherit run formatting consistently

**Symptom**: Table cells show inconsistent font sizes, colors, or missing bold even when every run was explicitly styled.

**Cause**: When `python-pptx` creates a cell text frame, it auto-generates a default paragraph/run. Adding a new run via `p.add_run()` leaves the default run empty but present — sometimes PowerPoint picks up the empty run's default font instead of your styled one.

**Correct**:
```python
tf = cell.text_frame
tf.clear()                      # remove the default empty run
p = tf.paragraphs[0]
r = p.add_run()
r.text = "..."
# set fonts on r, not on the default
```

Also set cell-level `vertical_anchor` and margins (`cell.margin_left = Emu(...)`) — these don't inherit from the text frame.

---

## 6 · Images bloat the .pptx silently

**Symptom**: A 20-slide deck balloons to 30+ MB because every figure is embedded at full capture resolution (often 4000×3000 px for a 300 DPI journal figure).

**Cause**: `slide.shapes.add_picture(path, ...)` embeds the original file bytes — not a resampled copy. A single 8 MB PNG appears on every slide that references it (python-pptx does deduplicate identical bytes, but not near-identical versions).

**Correct**: Resample images before adding:
```python
from PIL import Image
img = Image.open(src)
img.thumbnail((2400, 2400), Image.LANCZOS)  # plenty for 1920 px canvas
img.save(tmp_path, optimize=True, quality=90)
slide.shapes.add_picture(str(tmp_path), ...)
```

For scientific figures that need to stay crisp when zoomed: cap at 2400 px on the longest edge, which is 125% of a 1920 px canvas. Beyond that adds file size without perceptible gain on screen.

---

## 7 · Coordinate math off-slide (centring helpers produce negative x)

**Symptom**: User opens deck, reports "slide 4 content is cut off on the left" or "something's missing on the edge." The textbox is there in the file, but PowerPoint renders only what falls inside the slide's [0, slide_width] × [0, slide_height] rectangle; the rest is silently clipped.

**Cause**: Builder code computes a box position as `x = node_center - box_width / 2` to "centre the text under a node." When the node is near the left edge and the text box is wider than the node, the result is negative. The file saves, python-pptx accepts negative `Inches(...)`, but the viewer crops.

**The ENDO-ORAL 2026-04-24 incident**: slide 4 timeline had three nodes at x = 1.2 / 5.5 / 9.8 (inches) with a 3.9-inch wide detail text underneath centred via `x - 1.5`. For node 1 that gave `1.2 - 1.5 = -0.3` — the leftmost 0.3 inch of the first detail box was off-slide. A connector line was also overshot: drawn 9.8 inches wide from `x=1.8`, ending at 11.6, past the rightmost node centre at 10.25. Neither produced a build-time error.

**Correct**: Every shape/textbox placement must satisfy `0 ≤ x` and `x + width ≤ slide_width` (same for y and height). For centring helpers, clamp at the extremes:
```python
lab_w = 2.8
lab_x = max(0.1, min(slide_width - lab_w - 0.1, cx - lab_w / 2))
```
The two `0.1` margins give a visible breathing room and ensure the box never skims the hard edge.

**How to catch before the user sees it**: run `scripts/verify_pptx_bounds.py <deck.pptx>` after saving. It walks `slide.shapes` and flags any shape whose bounding box leaves the slide rectangle. Zero-cost; no rendering required; catches this bug every time. Wire it into Step 5 as a pre-declaration gate.

---

## 8 · Hero font size exceeds box height

**Symptom**: A hero-stat slide (e.g. `"44.7 %"` at 150 pt) renders with the top of the digits cut off or the entire number pushed out of the box. Title slides with very large display type are the usual victims.

**Cause**: `Pt(N)` = N/72 inches of *cap height* (plus ascender/descender). A 150-pt digit occupies ≈ 2.08 in of vertical space, but the author sized the box at `h = 1.8 in` — 14 % too short. python-pptx does not warn; the text frame's default is "no auto-fit", so overflow happens silently.

**Correct — either**:
- (a) Size the box so `h ≥ (size_pt / 72) × line_count × 1.15` (the 1.15 accounts for line-height padding). For a 150-pt single-line hero: `h ≥ 2.4 in`.
- (b) Enable `tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` so PowerPoint shrinks the text to fit. Fine for defensive backstop on titles, but **not** for hero stats — you do not want "44.7 %" silently shrunk to 110 pt because the box was too short.

**Decision rule**: if the number is the slide's entire point (V4 Finding / hero stat), size the box to the font. If the text is a title or subtitle where slight auto-shrink is acceptable, let TEXT_TO_FIT_SHAPE handle it.

**How to catch before the user sees it**: `scripts/verify_pptx_bounds.py` reads each textbox's first run size and compares against box height. Flags any box where `size_pt / 72 > h - margins`.

---

## 9 · "Native or raster?" — default to native, raster is a failure mode

**Symptom**: The interview answer or outline says "native editable PPT table preferred; raster fallback if rendering breaks." The builder uses raster images anyway because raster is easier to code. User asks later "where are the native tables?" — rework.

**Cause**: "Fallback" reads as "also fine" when you're coding under time pressure. It isn't. Raster tables are not editable in PowerPoint — the user cannot fix a typo, adjust column widths, or copy a cell value. For a deck the user will present from, raster is a downgrade.

**Correct**: When outline or interview specifies "native preferred, raster fallback":
1. Implement native first. Read the table data from `paper.json` or the paper's extracted text and build a `shapes.add_table()` in the deck. Bold + fill the header row, zebra-stripe the body, left-align the label column, centre the numeric columns.
2. Only fall back to raster if native actually fails for this table (e.g. > 10 columns that won't project, merged-header semantics lost in extraction). If falling back, tell the user explicitly in the hand-off message *why*.
3. Do NOT silently choose raster because it's less code.

**Curation rule** (this intersects with `anti-slop-academic.md §8`): a native table built from a 20-row paper table should be curated to **5–10 rows of the rows that matter for the argument**, not a faithful reproduction. The paper table is for the paper; the slide table is for the presentation beat.

---

## General rule · Visual QA before declaring done

Every `.pptx` generated by script must be opened in the target viewer (PowerPoint / Keynote / LibreOffice) by the operator before the work is declared complete. Smoke-tests in code catch API errors, not layout disasters. If the operator is a script (e.g. CI), render slide 1 to PNG and compare against a reference image — do not trust file-size or shape-count checks alone.

**Pre-declaration gate** (added v0.6.1 after ENDO-ORAL 2026-04-24 incident):
Before any "deck is done" message, run `scripts/verify_pptx_bounds.py <deck.pptx>`. It walks every shape on every slide and flags: (a) shapes extending outside the slide rectangle (gotcha §7), (b) textboxes where the first-run font size exceeds the box height (gotcha §8), (c) raster-image shapes on slides the outline tagged as native-table (gotcha §9). Non-zero exit means fix the builder before handing off — not after the user sees it.
