# CHANGELOG

Version history for the `paper-to-deck` skill. Each version corresponds to a real incident or milestone in skill development — the rules exist because something specific went wrong or was observed to work. Read this to understand *why* the skill's current rules exist, not just what they are.

---

## v0.4.0 — 2026-04-23 · Docling Tier 0 integration

### Added
- `scripts/extract_paper.py` now has a **Tier 0** that delegates to [docling](https://github.com/DS4SD/docling) when it's installed. Docling gives tight-cropped figure/table images without the page chrome our caption-anchored crops include, and handles facing-page figures + multi-column layouts natively.
- `references/external-extractors.md` — full rationale for the integration: why docling, what it does well vs. poorly, how Tier 0 interacts with Tier 1/2/2b/2c fallbacks, install & version-conflict notes, and notes on alternatives (Marker, MinerU, PyMuPDF4LLM, GROBID) that were evaluated but not integrated.
- Per-artifact `tier` field now includes `Tier 0 (docling, WxH)` when docling produced the image.
- Tables now produce `tables/tbl-NN.html` alongside `tables/tbl-NN.png` when docling provides structured HTML — useful even when the image itself came from our Tier 2c fallback.

### Changed
- The orchestration flow in `extract_paper.py`: a new `_extract_artifacts()` function runs Tier 0 once, then materialises each paper-declared figure/table by matching docling output to the paper's own caption index. Unmatched or missing artifacts fall through to Tier 1/2/2b/2c/3 per-artifact rather than wholesale. Old top-level `_extract_figures()` / `_extract_tables()` functions removed; helpers kept.
- Guiding principle codified into `external-extractors.md`: **the paper's own caption text is the authoritative index**. Extractors can misclassify; the paper's captions are the cross-check.
- `references/pdf-extraction.md` · new Tier 0 section added before Tier 1.

### Fixed
- phase-3-RCT test case facing-page handling for Figure 2: Tier 0 detects it natively now, so our Tier 2b heuristic no longer has to carry this case. Tier 2b remains as fallback for environments without docling.
- Caption-text retrieval for Tier 0 artifacts: docling's `pic.captions` / `tbl.captions` were empty on this paper's layout, so captions always come from our own caption-anchored scan, regardless of which tier produced the image.

### Install requirement (soft — not blocking)
- `pip install --user -U docling` (MIT licensed, ~50 MB model download on first run). If not installed, the skill works exactly as before via Tier 1/2/2b/2c/3 fallback.

### Known limitations
- Docling sometimes produces malformed HTML for landscape tables (cell order jumbles). For such tables, the image still comes from our Tier 2c rotation, but the HTML may be useful only as rough text content — not structured data. Flagged in `external-extractors.md`.
- Docling's junk figures (< 200 × 200 px, typically logos/page chrome) are filtered at the integration layer. Threshold may need tuning for some paper layouts.

---

## v0.3.3 — 2026-04-23 · Landscape table detection + rotation handling

### Added
- `scripts/extract_paper.py` · `_detect_landscape_on_page()` combines two signals to catch visually-rotated tables: text-direction vector voting (works when the PDF stores rotated orientation honestly) AND geometric signature (caption in bottom 45% of page + narrow body y-range — critical for NEJM-style PDFs where direction vectors lie and always report `(1, 0)`).
- `scripts/extract_paper.py` handles rotation via PIL: renders full page, rotates image 90° CW for CCW-rotated content, saves as `tbl-NN.png` with `tier` = `"Tier 2c (landscape, rotated +90 deg)"`.
- `paper.json` table entries now include a `rotation` field (degrees; 0 for portrait, ±90 for landscape) so the deck-building stage can surface the "this was originally landscape" caveat on the slide caption.

### Fixed
- phase-3-RCT test case regression: Tables 2 (efficacy) and 3 (safety) were landscape in the original PDF (top-tier clinical journal layout). Tier 2 portrait extraction cropped only a narrow vertical sliver showing row labels without data columns. The image was unusably thin (135 KB for the sliver vs 357 KB for the correctly-extracted portrait Table 1 — file-size disparity is a cheap detection signal but not part of the current pipeline; adding it to `verification.md` as a Tier A automated check remains `Unreleased`).
- Signal 1 (direction vectors) alone is insufficient for NEJM — their PDF rendering produces `dir = (1, 0)` even for visually-rotated text. Signal 2 (caption-position + y-range geometry) was essential.

### Changed
- `references/pdf-extraction.md`: new Tier 2c section documenting detection signals and the PIL rotate handling path. Notes that CW-rotated tables (rarer) currently fall through to Tier 3.

### Open
- CW-rotation detection not yet implemented; operator sees the full host page as a `pages/page-NN.png` sidecar and can manually rotate.
- Mixed orientations (tables + figures, both kinds on same page) would need per-artifact rotation evaluation rather than per-page. Not observed in practice yet.

---

## v0.3.2 — 2026-04-23 · Facing-page figures + universal table extraction

### Added
- `scripts/extract_paper.py` now extracts **all tables** by the same caption-anchored method used for figures, with the crop inverted (caption sits above the table, not below). Output lives in `tables/tbl-NN.png` + `tables/tbl-NN.txt` (caption sidecar).
- `scripts/extract_paper.py` now detects the **"facing page" figure convention** (NEJM Fig 2 etc.) — when the caption contains `(facing page)`, the actual figure is on the opposite physical page, not above the caption. Uses `page.get_drawings()` density as a tiebreaker when the neighbour page could be either +1 or -1.
- Host-page sidecars now live in a dedicated `pages/` directory; each figure/table also records the host page number so the user can re-crop manually when the automated crop is wrong.
- `paper.json` artifact entries now include `tier` field (`Tier 2 (caption-anchored)` / `Tier 2b (facing page, previous)` / etc.) so the deck-building stage can surface extraction uncertainty in the outline's caveats section.

### Fixed
- phase-3-RCT test case test case regression: Figure 2 (forest plot) was silently cropped from the wrong page — the caption text page instead of the actual forest plot. Tier 2b now resolves this correctly. Was invisible to shape-count / file-size checks but obvious once a human opened the image. This incident is documented in `pdf-extraction.md` §"Tier 2b" as the canonical case.
- `extract_paper.py` force-reconfigures stdout to UTF-8 at script start (was implicit before; some Windows locales still required `PYTHONIOENCODING=utf-8`).

### Changed
- `references/pdf-extraction.md`: added Tier 2b section on facing-page handling; expanded Tables section with the inverted caption-anchored crop pattern; updated Output contract to show new `tables/` + `pages/` directory layout and the `tier` field.

### Why this matters
When the extractor silently crops the wrong region, the bug survives all the way to a rendered deck — none of the automated `verification.md` Tier A checks catch it. The fix is a specific heuristic (facing-page detection via drawings density) rather than more automation. The lesson being codified into pdf-extraction.md: extraction bugs that produce plausible-looking-but-wrong images are the dangerous class; OCR-sanity-checking the extracted artifact is a cheap additional gate.

---

## v0.3.1 — 2026-04-22 · Typography as an explicit interview question

### Added
- `references/interview.md` Category F · Typography: a mandatory single question asked **after** all other interview categories. Default is Taipei Sans TC Beta with five alternatives (Microsoft JhengHei, Noto Sans TC, serif options, custom, decide-for-me). Motivated by the phase-3-RCT test case test run — the user had been silently defaulted to the earlier deck's font without being asked, and wanted the option explicitly surfaced.

### Changed
- Paper-specific questions moved from Category F to Category G (renaming only; templates unchanged).
- Interview presentation template updated to show Typography as the final category, after Language, with a short prompt telling the user the default is Taipei Sans TC Beta.
- Minimum interview question count stays 10; in practice the typography question pushes the natural number to 11–13 including ≥4 paper-specific.

### Why this matters
The font choice is a design decision the user owns, not a skill default. Silently defaulting works for internal consistency (house style) but fails when the user's audience has different font expectations (e.g. all-English conference crowd, a lab with a custom template, a serif-oriented review journal). Making it a question turns a hidden assumption into a choice.

---

## v0.3.0 — 2026-04-22 · Tier 2 academic references

### Added
- `references/figure-attribution.md` — fair-use decision tree, four-context defaults (internal / departmental / public / published), redraw-vs-embed logic. Motivated by the clinical-review test case where 4 figures were embedded without systematic attribution guidance.
- `references/equation-handling.md` — three rendering paths (raster from PDF / `matplotlib.text` retype / LaTeX Beamer switch), decision table for when equations belong on slides at all. Motivated by a clinical-review test case that had no equations, prompting the need to document when to skip rather than render.
- `references/citation-on-slide.md` — author-year over numeric, five-context format table, the "no `[12]` on slides" hard rule. Motivated by anti-slop pattern #3 (citation vomit) needing a positive format specification.

### Changed
- `references/slide-patterns.md`: added **P9 Thematic Review** pattern (non-IMRAD layout for review / survey / meta-analysis papers). The Lancet review test case revealed the original 8 patterns (P1–P8 IMRAD-flavored) don't fit thematic reviews — the deck had to improvise. P9 codifies the improvisation.
- `SKILL.md`: reference file table reorganized into "design & content discipline" vs "technical pipeline" groups. Both groups now reference all Tier 1 + Tier 2 additions.

---

## v0.2.0 — 2026-04-22 · Post-Lancet-test bug fixes + Tier 1 operational references

### Added
- `references/pptx-gotchas.md` — six technical pitfalls for `python-pptx` generation. Entry #1 is the critical `spc` unit mismatch (OOXML `spc` is 1/100 pt, not 1/100 em) that caused blown letter-spacing on every uppercase label in the first Lancet deck build.
- `references/windows-setup.md` — Windows-specific setup and gotchas. Entry #1 is the cp950 console encoding crash that killed `extract_paper.py` on its first run.
- `references/pdf-extraction.md` — three-tier fallback (embedded images → caption-anchored page crop → full-page render) and publisher-specific fingerprints. Motivated by Elsevier/Lancet's `get_images()` returning empty on figures that clearly exist.
- `references/verification.md` — three-tier deck verification (automated render + OCR + human inspection + presenter walkthrough). The PPTX bugs observed (letter-spacing, font fallback, text overflow) were all invisible to `python-pptx` — only a human opening the file caught them. Verification codifies "never ship without looking".

### Changed
- `references/anti-slop-academic.md`: added patterns #10 "Figure N as title" and #11 "bullets as information transfer" (≤ 40 words/slide rule) based on opinion feedback on the first Lancet deck draft.
- `references/slide-patterns.md`: added universal rules section covering "title is an argument not a label", "body ≤ 40 words", "figure attribution in caption not title", "dense-layout discipline" — all emerging from the opinion-review pass.
- `SKILL.md` Step 5: mandates reading `pptx-gotchas.md` before writing PPTX code; adds visual-inspection checkpoints.
- `scripts/extract_paper.py`: ASCII-only stdout (fixes cp950 crash).

### Fixed
- Reverted rule "title slide = paper title is slop" — user correctly pointed out that the cover's job is paper identification, not argument framing. The "title is an argument" rule now applies to content slides only; the cover is explicitly exempt.

---

## v0.1.0 — 2026-04-22 · Initial skeleton

### Added
- `SKILL.md` — main spec with D1–D5 discipline (interview-first, outline-first, figures-from-paper-only, anti-slop, safety overrides for huashu-design inheritance).
- `references/interview.md` — six-category question bank, ≥10 questions with ≥4 paper-specific template.
- `references/slide-patterns.md` — eight canonical research-slide patterns (P1 Hook through P8 Takeaway).
- `references/anti-slop-academic.md` — nine common academic slide slop patterns with fixes, plus detection checklist.
- `assets/outline-template.md` — outline document structure for Step 3.
- `scripts/extract_paper.py` — PDF → structured JSON + figure PNG extractor (best-effort, publisher-agnostic).

### Designed against
- `huashu-design` and `claude-canva-design` prior art — borrowing the L1–L5 Claude Design architecture and Junior Designer workflow pattern, but with explicit overrides (D5) to disable brand-asset-protocol auto-triggering, `~/Downloads` globbing, and external curl — all unnecessary and surprising for academic-paper contexts.

### Known at release
- Extract script works on arXiv preprints; fails gracefully on Elsevier/Lancet (will be addressed in v0.2).
- PPTX generation path not yet implemented — deferred to `claude-scientific-writer:pptx` or `huashu-design:html2pptx.js`.

---

## Unreleased · Candidate items for next iteration

Items identified but not yet written. These become releases when driven by a real incident:

- **Publisher-specific extractors**: dedicated parsers for Elsevier/Lancet/Cell (Tier 2 fallback is generic; a Lancet-specific caption pattern would get cleaner crops).
- **Speaker-note language switcher**: currently the interview asks once for notes language; no support for mid-deck language switch (e.g. English notes for intro, Chinese for methods).
- **LaTeX Beamer handoff**: when the user chooses Beamer output via `equation-handling.md` path (c), the skill should route to `claude-scientific-writer:venue-templates` rather than drop the work. The handoff is not yet wired.
- **Evaluation harness expansion**: `evals/evals.json` currently has one case (the Lancet review). Add at least one primary-research case (arXiv ML paper), one short-format case (5-min lightning talk), and one bilingual-notes case.
- **Per-paper design brief template**: currently the interview produces an ad-hoc `design_brief.json`. Formalize as a schema and version it.
