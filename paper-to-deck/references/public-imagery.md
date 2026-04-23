# Public-Domain Contextual Imagery

When the user opts into Q17 "contextual public-domain imagery", the skill pulls images from a small whitelist of open sources, filters by licence, and drops them into the deck with attribution. This reference documents the allowlist, the licence logic, the workflow, and the places where the skill **declines to act** (memes, copyrighted images).

---

## Why this exists

A single research paper has ~4–10 extractable figures. Medical-teaching decks observed in the wild (NCKU 內科 Year Review reference decks) run at 60–80% image density — far higher than a single paper can provide. D3 "figures only from the paper" remained the default for v0.1–v0.4 because naive external fetching risks (a) version drift, (b) wrong-image matches that look plausible, (c) copyright-ambiguous stock photos.

v0.5.0 opens a narrow, audited path: a small allowlist of authoritative open-licence sources, a strict licence filter, and a user batch-approval step before any fetch.

---

## Allowlist (v0.5.0)

The skill may call these endpoints and **only** these endpoints for imagery:

| Source | Endpoint | Content | Licence flags accessible |
|---|---|---|---|
| **Wikimedia Commons** | `https://commons.wikimedia.org/w/api.php` | Historical photos, anatomical illustrations, drug structures, portraits, maps | Yes (`extmetadata.LicenseShortName`) |
| **NIH Open-i** | `https://openi.nlm.nih.gov/api/search` | Biomedical imagery (radiology, pathology, histology) from PMC open-access papers | Yes (licence info per record) |
| **CDC PHIL** | `https://phil.cdc.gov` (web scrape via approved query path) | Pathogen microscopy, historical public-health photos, vaccine history | US federal government → public domain by default |
| **WHO open imagery** | `https://www.who.int/` report pages | AMR maps, global-burden charts | Per-page; often CC BY-NC-SA (check) |

Adding a new source requires editing this file + `scripts/search_public_imagery.py` allowlist **and** documenting the incident that justified it in `CHANGELOG.md`. Do not add URLs in-passing.

### Why not these

- **Unsplash / Pexels / Pixabay**: stock photo feel is wrong for academic slides; licence metadata is loose.
- **Google Images**: no licence metadata; risk of wrong attribution.
- **Generic web scraping**: licence ambiguity; deck could be delivered with uncleared imagery.
- **arXiv / bioRxiv full figures**: per-figure licence varies within a paper; inspection cost too high for batch fetch.

---

## Licence policy

### Strict mode (default)

Accept only:
- **CC0 / Public Domain** (`P`)
- **CC BY** (`BY`) — any version, attribution required
- **CC BY-SA** (`BY-SA`) — any version, attribution + share-alike
- **US-Gov / US Federal PD** (PHIL, NASA, etc.)

Reject:
- CC BY-NC, CC BY-ND, CC BY-NC-ND, CC BY-NC-SA
- "All rights reserved"
- Missing or ambiguous licence metadata (do **not** guess; skip the candidate)

### Loose mode (user opt-in via Q17 answer `b`)

Adds: CC BY-NC (any version). Warn the user once — recorded commercial use of the final deck violates the licence.

**Never** relax beyond loose. `CC BY-ND` blocks the mixed / cropped use the skill typically needs; the various Creative Commons `NC-ND` variants are always excluded.

---

## Attribution format

Every fetched image gets attribution rendered on the slide. Two placement options:

### On-slide caption (default)

Directly below the image, single line, 10pt, `text.muted` (`#6C757D`):

```
Wikimedia Commons · CC BY-SA 4.0 · photo by J. Doe
```

### Speaker-note attribution (alternative)

If the slide aesthetic demands no visible caption (e.g. V1 cover with a full-bleed mascot), move the attribution to speaker notes:

```
[Image: Wikimedia Commons · CC BY-SA 4.0 · photo by J. Doe · retrieved 2026-04-23]
```

Side-car metadata always persists regardless of placement — `public_imagery/<slug>.attribution.json` stores:

```json
{
  "source": "wikimedia-commons",
  "source_url": "https://commons.wikimedia.org/wiki/File:...",
  "licence": "CC BY-SA 4.0",
  "author": "J. Doe",
  "title": "Neisseria gonorrhoeae culture (stained)",
  "retrieved_at": "2026-04-23T14:30:00Z",
  "used_in_slide": 5
}
```

This file is committed to the project directory even when the attribution renders on the slide — it's the paper-trail for future licence audits.

---

## Workflow

```
extract_paper.py
    ↓
imagery_candidates.json (produced during extract)
    ↓
interview Q17 shows candidates → user ticks
    ↓
search_public_imagery.py --candidates imagery_candidates.json \
                         --approved <comma-separated ids> \
                         --mode strict|loose
    ↓
public_imagery/<slug>.png          ← only if licence passes
public_imagery/<slug>.attribution.json
    ↓
HTML deck + PPTX render image with on-slide caption (or notes-only if V1 cover)
```

### Imagery candidates format (`imagery_candidates.json`)

Produced by `extract_paper.py` after reading `full_text.txt`. Each entry:

```json
{
  "id": "c01",
  "slide_anchor": "slide-3-context",
  "rationale": "Paper cites Sir Alexander Fleming's 1928 penicillin discovery; a historical portrait would anchor the introduction.",
  "suggested_query": "Alexander Fleming portrait",
  "source_hint": "wikimedia-commons",
  "manual_only": false
}
```

For meme slots (Shrek, movie stills) the candidate flags `manual_only: true`; the search script skips these and the agent leaves a placeholder in the HTML/PPTX.

### Failure modes

| Situation | Action |
|---|---|
| Query returns no results | Log `{id}: skip — no hits`. No placeholder; agent notes this in outline preamble. |
| All hits fail licence filter | Log `{id}: skip — no CC-licensed match`. Same handling. |
| Hit has licence metadata but ambiguous version | Reject. Do not assume "probably CC BY". |
| Rate-limited by source | Back off; try next source in `source_hint`; if all fail, skip. |
| Network unreachable | Skip entire Q17 step; fall back to paper-only figures. Warn in outline preamble. |

**Never** generate an approximate image with an LLM / DALL-E / Nano Banana to work around a missing fetch. The skill's imagery discipline (D3) preserves audit trail; generated approximations look plausible but cannot be sourced.

---

## Pop-culture memes (manual-only slot)

Medical-teaching reference decks use memes as mnemonics — Shrek's face for acromegaly features; Jurassic Park raptor for virulence analogies. These images are copyrighted by Disney, Universal, etc. The skill's position:

- **Agent does not fetch.** Even if Shrek images exist on Wikimedia, they're uploaded in violation of copyright and the skill will not whitelist that path.
- **Candidate list marks `manual_only: true`** for meme slots. The rationale field describes the mnemonic intent ("Shrek's facial features mirror acromegaly soft-tissue enlargement — strong visual mnemonic for the 國考 audience").
- **Agent leaves placeholder.** In HTML and PPTX a dashed-outline rectangle with the rationale text appears; the user pastes their own meme before final export.

Do not try to sidestep this by generating a "non-copyrighted Shrek-style ogre face" with an image model. The copyright concern is about intent and recognisability, not pixel identity; an LLM-generated lookalike carries the same legal risk for anyone who screencaps the recorded talk.

---

## Testing the workflow

Before wide use, verify on one candidate paper:

1. Run `extract_paper.py` on a paper that cites a named historical figure (e.g. Fleming for penicillin).
2. Check `imagery_candidates.json` contains a candidate with source_hint `wikimedia-commons`.
3. Run `search_public_imagery.py --approved c01 --mode strict`.
4. Confirm `public_imagery/c01.png` exists, attribution JSON has `licence` populated, and the licence is in the strict allowlist.
5. Render the deck; confirm on-slide caption shows the attribution.
6. Delete `public_imagery/` and retry — the script must be idempotent and re-fetch.

Each subsequent paper that exercises a new source (Open-i for a pathology candidate; WHO for a map) should be added to `evals/evals.json` with its source mix noted.

---

## Amendment log

| Date | Change | Driver |
|---|---|---|
| 2026-04-23 | Initial allowlist (Wikimedia / Open-i / CDC PHIL / WHO), strict + loose licence modes, manual-only meme policy | v0.5.0 design doc (`docs/plans/2026-04-23-medical-teaching-style-design.md`) |
