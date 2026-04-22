# paper-to-deck

A pair of Claude Code skills for turning an academic paper PDF into a polished, editable PowerPoint deck — interview-first, figure-aware, language-flexible.

Built specifically for the **lab meeting / journal club / conference talk** workflow where slides need to be both typographically serious and intellectually faithful to the source paper.

## What's in this repo

| | |
|---|---|
| **`start/`** | Onboarding skill. Validates the paper PDF (magic bytes, text layer, reasonable length) and hands off. |
| **`paper-to-deck/`** | Main skill. Structured interview (10+ questions, ≥4 paper-specific) → outline (wait for user OK) → HTML deck (first 3 slides early) → `.pptx` with speaker notes. |
| **`CLAUDE.md`** | Orientation for Claude Code / future maintainers. Hard rules, file map, dev discipline. |

## Pipeline at a glance

```
PDF
 │
 ├─ start: validate (file exists · is PDF · has text layer · 2–60 pages)
 │
 └─ paper-to-deck:
    │
    ├─ Step 1 Extract   PDF → paper.json + figures/ + tables/ + pages/
    │                   (5-tier extraction: docling → embedded → caption-anchored
    │                    → facing-page → landscape-rotated → full-page fallback)
    │
    ├─ Step 2 Interview 10+ questions (audience, length, emphasis, design,
    │                   language, paper-specific, typography last)
    │
    ├─ Step 3 Outline   Slide-by-slide draft → USER APPROVES before building
    │
    ├─ Step 4 Build     deck.html (show first 3 slides, then finish)
    │
    ├─ Step 5 Export    deck.pptx via python-pptx
    │
    └─ Step 6 Summary   Caveats + next step. 2 sentences max.
```

## Design principles

### The paper is the source of truth
Every figure and table is matched to the paper's own `Figure N` / `Table N` caption. Extractor output that doesn't correspond to a paper caption is treated as noise (this eliminates misclassified logos, duplicated figure-as-table, etc.).

### Rules come from incidents, not imagination
Every rule in the skill's references corresponds to a specific failure documented in `CHANGELOG.md`. The skill does not add rules a-priori — it evolves from real runs.

### Interview is mandatory
Even if the user says "just do it", the skill pushes back once — because 5 minutes of questions saves an hour of rework. Typography comes last (by that point the user has enough context to answer well).

### Cover slide is exempt from the "title = argument" rule
The cover's job is paper identification. Other content slides use statement-style titles, but the cover displays the actual paper title. (This exception came from user feedback; originally the cover used a statement and users found it less useful.)

### Windows-first development
Scripts emit ASCII-only to stdout (`cp950` locale crashes on unicode in `print()`). Font default is Taipei Sans TC Beta with Microsoft JhengHei fallback.

## Quick start

### Install dependencies

```bash
pip install --user pymupdf python-pptx pillow
pip install --user -U docling    # optional but recommended — enables Tier 0
```

### Invoke in Claude Code

```
User: start a paper
       D:\path\to\your_paper.pdf
```

The `start` skill takes over. Answer the validation confirmation, then `paper-to-deck` runs the interview and builds the deck.

## Extraction strategy

The extractor uses a six-tier cascade. Each tier fires only if the previous one failed for that specific artifact:

| Tier | When it fires | What it does |
|---|---|---|
| 0 · docling | Always tried first if installed | Layout-aware extraction with tight crops, handles facing-page + multi-column natively |
| 1 · embedded images | arXiv preprints, clean LaTeX output | `page.get_images()` returns embedded raster objects |
| 2 · caption-anchored | Elsevier/Lancet/Nature | Find `Figure N:` caption, crop area above it |
| 2b · facing-page | NEJM "Figure N (facing page)" convention | Caption on one page, figure on opposite page — drawings density disambiguates |
| 2c · landscape rotation | NEJM Table 2/3 rotated on portrait page | Detect via caption-in-bottom-half + narrow body y-range, rotate image via PIL |
| 3 · full-page | Last resort | Render whole page, user crops manually |

See [`paper-to-deck/references/pdf-extraction.md`](paper-to-deck/references/pdf-extraction.md) and [`paper-to-deck/references/external-extractors.md`](paper-to-deck/references/external-extractors.md) for the full rationale.

## Project philosophy

Each skill is small and focused, each reference file is narrowly scoped, and the `CHANGELOG.md` doubles as an incident log. Read the changelog first if you want to understand *why* a particular rule exists — every entry references the concrete bug or user feedback that motivated it.

## License

MIT — see [LICENSE](LICENSE).

Dependencies:
- [`pymupdf`](https://github.com/pymupdf/PyMuPDF) — AGPL-3.0 (licensed separately)
- [`python-pptx`](https://github.com/scanny/python-pptx) — MIT
- [`docling`](https://github.com/DS4SD/docling) — MIT (optional Tier 0)
- [`Pillow`](https://github.com/python-pillow/Pillow) — HPND

## Status

v0.4.0 · pre-release. Tested end-to-end on two real papers (clinical review + phase-3 RCT) from different publishers and layouts. CW-rotated tables and bilingual slide decks are not yet exercised.
