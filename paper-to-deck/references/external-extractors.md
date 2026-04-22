# External Extractors

This skill's `scripts/extract_paper.py` can delegate PDF figure/table extraction to external libraries when they are installed. When they're not installed (or fail), it falls back to the built-in Tier 1/2/2b/2c/3 cropping logic documented in `pdf-extraction.md`.

The architecture is deliberately **hybrid** — not pick-one-winner. Different tools are strong at different things; the integrator's job is to take the best part of each.

---

## Current integration · `docling`

### Why docling

- **MIT-licensed**, no redistribution friction
- Single-call Python API: `DocumentConverter().convert(pdf).document`
- Active maintenance as of April 2026
- Clean tight-cropped images for figures — no page chrome, no bleed
- Layout-aware: handles multi-column, facing-page spreads, and cross-page tables natively
- Structured table HTML output in addition to raster images

### What docling does well in this skill

| Artifact type | Docling performance on journal PDFs |
|---|---|
| Primary figures (K-M plots, schematics) | Excellent — tight crops, correct page |
| Facing-page figures (NEJM "Figure 2 (facing page)" convention) | Excellent — detects natively without needing our Tier 2b heuristic |
| Portrait tables | Good image, good HTML |
| Landscape tables (NEJM Table 2/3) | Image extraction unreliable; HTML mangles cells |

### What docling does poorly

| Issue | Impact |
|---|---|
| Classifies small icons/logos as figures (70×29 page chrome icons, etc.) | Must filter by pixel size before accepting |
| Misclassifies certain figures as tables (e.g. forest plots classified as both) | Must match docling artifacts to paper's own `Figure N` / `Table N` captions and drop unmatched |
| Caption retrieval (`pic.captions`, `tbl.captions`) returns empty on many journal PDFs | Caption text must come from our own caption-anchored scan |
| Landscape-rotated table images: sometimes `tbl.get_image()` returns None | Fallback to our Tier 2c rotation for the image; keep docling HTML if it has it |

### The integration rule

`scripts/extract_paper.py` orchestrates as follows:

1. **Always** scan the paper for authoritative `Figure N` / `Table N` captions — this builds the index of what the paper says exists (paper is the source of truth, not the extractor).
2. **If docling is importable**, run it once, collect its artifacts in a cache, filter junk by pixel size (< 200 × 200 px rejected), mark each with host page number.
3. For each paper-declared figure/table, try to match a docling artifact by host page. Match = use docling's tight crop. Unmatched = fall through to our Tier 2/2b/2c cropping for that specific artifact.
4. For tables, save docling's HTML alongside the image regardless of whether the image came from docling or our fallback — HTML is a useful extra even when the image didn't come from docling.
5. Caption text always comes from the caption-anchored scan in step 1, never from docling.

### How to tell which extractor was used

Each entry in `paper.json`'s `figures[]` / `tables[]` has a `tier` field:

- `Tier 0 (docling, WxH)` — docling produced the image
- `Tier 2 (caption-anchored, below)` — our fallback
- `Tier 2b (facing page)` — our fallback with facing-page handling
- `Tier 2c (landscape, rotated +90 deg)` — our fallback with landscape rotation
- `Tier 3 (full-page fallback)` — our last-resort full-page render

Mixed outcomes are normal and expected (e.g. figures from Tier 0, tables from Tier 2c). Look at the tier log to confirm nothing silently downgraded.

---

## Install

```
pip install --user -U docling
```

Docling pulls layout and OCR models on first run (~50 MB). Cache lives under `~/.cache/huggingface/hub/`. Subsequent runs are fast.

### Version conflicts to watch for

- `docling` depends on recent `transformers` which in turn pins `tokenizers` and `huggingface-hub`. If a machine already has older versions, upgrade with `pip install --user -U docling transformers`.
- `docling >= 2.90` requires Python 3.10+. Tested with Python 3.12 on Windows.

---

## When docling is unavailable

The skill still works — everything falls through to Tier 1-3 as before. You get slightly less clean crops (our crops include more page chrome) and no structured table HTML, but all artifacts still extract.

Trigger the fallback path deliberately by uninstalling docling, or by temporarily forcing: edit `DOCLING_AVAILABLE = False` near the top of `extract_paper.py`.

---

## Alternatives not yet integrated

Documented here so future work knows what was considered and why:

### Marker (datalab-to/marker)
- GPL-3.0 + modified model license — complicates redistribution of derivative skills.
- `--use_llm` flag gives best-in-class accuracy on messy layouts but requires an API key.
- Python API is `PdfConverter` class, simple.
- **Consider for**: papers that broke docling (very complex scientific layouts with math + multi-panel figures).

### MinerU (opendatalab/MinerU)
- Custom license (Apache-2.0 base), Python 3.10–3.12, **20 GB disk** for full models.
- Strongest on CJK text, cross-page tables, and landscape layouts (native handling).
- CLI-first API: `mineru -p input.pdf -o output_dir`; Python SDK available.
- **Consider for**: Chinese-language papers, or when docling's HTML cell ordering breaks on exotic table layouts.

### PyMuPDF4LLM
- Thin wrapper on pymupdf (which we already use).
- No ML, CPU-only, tiny install.
- Extracts markdown + detects tables/headers with layout engine.
- **Consider for**: minimal-dependency deployment where even docling is too heavy.

### GROBID
- Java service, needs Docker or dedicated server.
- TEI/XML output, production-tested on millions of papers (ResearchGate, Semantic Scholar).
- **Consider for**: server-side batch pipelines; heavy setup for a local single-file tool.

---

## Principle: paper is the source of truth, not the extractor

No matter which extractor is used, the **paper's own caption text** is the authoritative index of what figures and tables exist. Extractors can (and do) classify things as figures that aren't, or as tables when they're plots. Always build the paper's caption index first, then match extractor output to it. Unmatched extractor output is noise, full stop.

This principle is why this skill scans `Figure N` / `Table N` captions from full text regardless of extractor — it's the cross-check that catches extractor mistakes.
