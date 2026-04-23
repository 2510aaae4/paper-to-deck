# CHANGELOG

Version history for the `paper-to-deck` skill. Each version corresponds to a real incident or milestone in skill development — the rules exist because something specific went wrong or was observed to work. Read this to understand *why* the skill's current rules exist, not just what they are.

---

## v0.6.0 — 2026-04-24 · OE extension round (Step 3.5)

### Added
- `references/oe-extension.md` — new reference doc. Protocol for a post-outline, pre-HTML round where the agent proposes 3–4 EBM questions via OpenEvidence MCP and appends each as one slide at the end of the deck. Documents the framing (extend, not audit), the bundle format (axis + flavor table), flavor rule (mainly A "clinician's-next-question", at least one B "evidence-deepener"), axis coverage (therapy / prognosis / diagnosis), question-selection heuristics (prioritize gaps the paper names explicitly, then weak-evidence points a clinician would actually apply), per-slide rendering rules (question-form title is the narrow exception to the deck-wide statement-title rule, `data-extension="true"` marker for subtle visual differentiation), and placement (between V7 Takeaways and References).
- `SKILL.md` Step 3.5 · new prose section between Step 3 (outline) and Step 4 (HTML). Summarises the protocol and points at `references/oe-extension.md` for full detail. Includes explicit skip conditions (non-clinical paper, deck <10 slides, user opts out).
- `SKILL.md` Checkpoint · new line item "Step 3.5 OE extension round offered to the user; if accepted, 3–4 extension slides added with axis + flavor trace and `article_id` from OE."
- `SKILL.md` ASCII workflow diagram updated from 6 steps to 7, with Step 3.5 shown as opt-in for clinical papers.

### Changed
- `SKILL.md` frontmatter version → 0.6.0; `updated` → 2026-04-24; description extended to mention Step 3.5 and the extend-not-audit framing.
- `SKILL.md` Reference files table · new row for `oe-extension.md` between `anti-slop-academic.md` and `citation-on-slide.md`.

### Why this version exists
Two back-to-back events drove the rework. On 2026-04-23 the Tande 2026 SEA deck reached slide 22 (a three-big-stat outcome slide). The user asked for an OE-backed citation audit of the four claims; the agent produced `slide22_audit.md` with PASS/CAUTION/FAIL verdicts and per-claim fix suggestions. The audit was technically correct — two CAUTION calls on phrasing (the "5-10% in-hospital" number overlapping 90-day range; the "not surgical speed" clause being too strong) were defensible against downstream literature — but the output was tonally wrong for a journal-club deck. Audit reports are adversarial artifacts; decks are synthesis artifacts. The user re-framed on 2026-04-24: OE's role in this skill should be **paper extension**, not **paper challenge**. The agent should propose 3–4 EBM questions the paper *raises but doesn't fully answer*, and each becomes a slide at the end.

A subtler motivation surfaced during the reframe discussion: OE's evidence base is downstream of the paper being presented. The same literature that would "externally verify" the paper's claims very often *cites* the paper being verified. That circularity undermines audit but *enhances* extension — when the question is "what lies beyond this paper", downstream literature citing it is exactly the right source.

The flavor rule (mainly A, at least one B) emerged from a second round of discussion: pure-A bundles read as Googleable FAQ (useful but shallow); pure-B bundles read as methodology lectures (rigorous but off-brand for lab meeting / journal club). The 3+1 split preserves practicality while giving one slot for genuine evidence depth. The axis rule (therapy / prognosis / diagnosis) came from the user directly and was not agent-proposed — it maps cleanly onto how an ID clinician mentally indexes clinical papers.

The question-form slide title exception was deliberately scoped narrowly. The deck-wide rule "slide title is a statement or question, not a topic label" already allows questions as titles; the extension-slide rule tightens that to *always questions* because the narrative function is *pose-then-answer*. Without this tightening the agent would drift toward summary titles ("Whole-spine MRI coverage"), which collapses the pedagogical beat.

### Known limitations
- OE MCP auth degrades gracefully in few sessions — cookies expire and the user has to re-auth in a fresh session. The skill explicitly does NOT try to run the extension round with a subset of working OE calls; partial OE coverage is worse than none because a half-OE, half-agent-synthesized extension block is indistinguishable from the audience's POV.
- Non-clinical papers have no natural therapy/prognosis/diagnosis axis. v0.6.0 skips extension for non-clinical papers entirely; a future version might define per-domain axis mappings (e.g., for ML: "architecture variant / training regime / evaluation protocol"), but that requires real paper runs in other domains first.
- The `data-extension="true"` visual cue in the HTML deck is specified but not yet implemented in any theme file (`assets/themes/*.json`). The first deck that runs Step 3.5 through HTML will need to wire it. Recommended: dashed top-rule 1px at 15% opacity of the accent colour, or a 2% muted background tint. Pick and commit the choice to the theme files after the first run.
- The `article_id` trace in `outline.md` speaker notes is a UX bet — the assumption is that the presenter-mode walkthrough will want to chase one of the OE artifacts if an extension slide raises a question during rehearsal. If the user never actually opens the artifacts, this trace is dead weight and should be dropped in v0.6.1.
- No eval case yet — extension-round outcome quality is hard to grade automatically. Candidate metric for future: % of proposed questions the user accepts without revision. Needs at least 3 clinical papers with extension rounds run to benchmark.

---

## v0.5.0 — 2026-04-23 · Medical-teaching visual style + public-domain imagery

### Added
- `references/slide-patterns.md` · new bottom section "Medical-teaching visual archetypes" with palette, typography, and eight visual archetypes (V1 Cover × 3 variants, V2 Part divider, V3 Concept, V4 Finding, V5 Native table, V6 Collage, V7 Key Takeaways grid, V8 Branded footer strip). Reverse-engineered from two NCKU 內科 Year Review reference decks (infectious disease + endocrinology, both non-user authored; archived under `_private/style-ref/` and `_private/style-ref2/`).
- `references/interview.md` · new Category H with five questions (Q13–Q17): visual scheme, cover template, branded footer, body language, contextual public-domain imagery batch. Typography remains Category F and stays last.
- `references/public-imagery.md` · new reference doc. Allowlist of four sources (Wikimedia Commons / NIH Open-i / CDC PHIL / WHO), strict + loose licence modes, attribution format, and explicit manual-only policy for pop-culture memes (Shrek for acromegaly, Jurassic Park raptor for virulence — legitimately effective mnemonics, but copyrighted and therefore never agent-fetched).
- `scripts/search_public_imagery.py` · new script. Allowlist-guarded HTTP, token-based licence filter (rejects CC BY-NC in strict, CC BY-ND always), per-candidate attribution JSON sidecars, graceful skip when no CC-licensed match is found. Wikimedia + Open-i + CDC PHIL implemented; WHO deferred to future iteration (returns None until curated endpoint list arrives).
- `scripts/extract_paper.py` additions:
  - **Subpanel detection**: `_detect_subpanels()` parses figure captions for `(A) ... (B) ...` patterns, returns a list of labelled sub-panels attached to each figure entry in `paper.json`. Enables one figure's Fig 2A vs Fig 2B to anchor different slides without manual cropping.
  - **Structured table parse**: when docling produced `tbl-NN.html`, `_parse_table_structure()` re-parses it into `tbl-NN.json` with per-cell metadata — `text`, `is_header` (sourced from `<th>` or `<thead>`), `colspan`, `rowspan`, `numeric` (parsed value after stripping %, thousands separators, ranges, plus-minus), and `footnote` (trailing `*†‡§¶#` markers split off). Top-level `header_row_count` surfaces grouped headers. The deck-builder can emit **native editable PPT tables** (V5 archetype) with merged header cells and bolded header runs, and optionally rebuild a numeric column as a **native bar chart** (V4 archetype) without re-parsing text.
  - **Imagery opportunity scan**: `_scan_imagery_candidates()` walks the full text for anchor phrases (Fleming / Pasteur / Koch, IDSA / WHO AMR / ADA-EASD guidelines, common pathogens by Latin binomial, endocrine mnemonic terms) and emits `imagery_candidates.json` for the agent to surface in Q17. Each candidate has `{id, slide_anchor, rationale, suggested_query, source_hint, manual_only}`.
- `assets/themes/` · three theme token files (`crimson-blue.json`, `teal.json`, `minimal.json`) consumed by HTML deck and PPTX builder. Each encodes palette, typography sizes, cover default, footer default, takeaways grid default, part-divider threshold.
- `docs/plans/2026-04-23-medical-teaching-style-design.md` · design doc capturing the brainstorming session that drove this version.

### Changed
- `SKILL.md` frontmatter version → 0.5.0 and description extended to mention medical-teaching themes and the narrow public-asset fetch path.
- `SKILL.md` D5 safety section: the "no external access except PDF + docling" rule now lists four whitelisted public-asset API hosts as a third permitted category. Non-whitelisted hosts remain forbidden.
- `SKILL.md` Step 2 `Interview`: explicit instruction to read `imagery_candidates.json` before presenting Q17, and to hand the ticked IDs to `search_public_imagery.py`.
- `SKILL.md` Reference files table: rows added for `public-imagery.md` and `assets/themes/*.json`.
- `CLAUDE.md` D5 safety guardrail block: expanded to enumerate the four whitelisted API hosts, split strict / loose licence modes, and note the meme manual-only policy. Added `docs/plans/` to the directory tree. "Key files quick-reference" gained rows for medical-teaching visual tuning + public-imagery fetch.
- Extract pipeline smoke-test coverage: added inline tests for `_detect_subpanels`, `_scan_imagery_candidates`, and `_licence_passes` (not committed as a test file yet — a proper test harness is tracked under Unreleased).

### Why this version exists
The user reviewed two NCKU 內科 Year Review reference decks (antibiotics talk by Chin-Shiang Tsai 2025-08-12, 50 slides; endocrine talk by another 內分泌科 attending 2023-10-03, 56 slides) and asked whether `paper-to-deck`'s visual output could be brought into the same family. The style is distinctive: bold black centred titles with `#D62027` red accent, teal structural elements, liberal use of pastel blocks for takeaways, meme-tolerant where clinically useful, bilingual footnotes under data tables. None of this was previously capturable by the skill — v0.3 / v0.4 emphasised conservative-academic visual defaults and hard-locked imagery to paper-only.

The decision was **not** to spin off a separate `medical-lecture` skill (the narrative workflow is still single-paper journal club), but to add visual archetypes as opt-in and to carefully open one narrow external-fetch path for contextual imagery. The licence discipline (strict by default, loose as an explicit choice, manual-only for memes) came directly from the user's preference for "OK to hit public-domain sources, not OK to grab arbitrary web images".

### Known limitations
- WHO search is a no-op stub. The WHO website has no structured API and per-page licences vary; curating a safe endpoint list is deferred until the next paper that actually wants a WHO map.
- CDC PHIL search is a lightweight HTML scrape; if CDC restructures the page, the scrape will break silently and fall through to `[SKIP] no hits`. Consider wiring a user-agent rotation + version check when a paper relies on PHIL imagery.
- `_scan_imagery_candidates` anchor list is hand-curated (Fleming, Pasteur, Koch, IDSA, WHO AMR, ADA-EASD, S. aureus, K. pneumoniae, E. coli, acromegaly). Each new paper topic that would benefit from contextual imagery needs a new anchor; do not add broadly-matching patterns that would false-positive.
- Native editable PPT table emit (V5) requires the `build_pptx.py` *deck script* (deck-specific, not part of this skill repo) to read `tables/tbl-NN.json` and call `python-pptx` `add_table()`. This skill surfaces the data; the deck author wires it through. When tested on a paper, document the table-rendering result and amend `pptx-gotchas.md` if any new run-formatting quirk surfaces.
- Pop-culture meme slots remain placeholders. If Q17 yields `manual_only: true` entries, the outline must flag each one and the user must paste the image before export. No automation.
- The reference decks that inspired V1–V8 are both non-user-authored; `evals/evals.json` adds them as *inspiration references*, not eval targets (they're lectures, not journal-club runs of a single paper).
- **Windows Developer Mode required for docling** (surfaced by the first v0.5.0 SRMA test run on 2026-04-23): `huggingface_hub` 1.11.0 creates symlinks in its cache; without Developer Mode the model download aborts with `WinError 1314` mid-way, leaving a partially-built cache. Documented in `references/windows-setup.md` §6a; `start/scripts/check_deps.py` only detects *missing* packages, not *broken cache* — surfacing that is a candidate improvement for v0.5.1.
- **Docling `std::bad_alloc` on text-dense later pages**: same SRMA test run saw pages 7–14 fail docling's layout preprocessor; Tier 2 fallback took over cleanly so nothing was lost, but Fig 3 (on page 11) came from Tier 2 instead of Tier 0. Documented in `references/windows-setup.md` §6b.
- **SoF / GRADE table structured quality**: the same SRMA's Table 2 passed through docling HTML and `_parse_table_structure`, but docling collapsed multi-value cells ("K = 1 N = 2230 1.4% vs 5.1% RR 0.28 ...") into single strings and did not mark any row as `<thead>`, so `header_row_count` came back 0. Table 2 is a complex landscape SoF table; simpler tables likely parse cleanly. Improving the parser is a future call; for now the PNG crop remains the reliable path when the structured JSON is too mangled to use directly.

---

## v0.4.1 — 2026-04-23 · HTML deck gotchas + hand-off discipline

### Added
- `references/html-deck-gotchas.md` — new reference file, parallel to `pptx-gotchas.md`. Documents CSS cascade bugs and UI hand-off discipline for Step 4.
- Gotcha §1 · **CSS specificity on display-controlling rules**: an un-qualified modifier class (e.g. `.cover { display: flex }`) silently overrides `.slide { display: none }` at equal specificity when declared later. Cover slide remains visible on every subsequent slide, content collides. No console error; no automated signal. Fix: qualify state-dependent display with the state class — `.slide.cover.active { display: flex }`.
- Gotcha §2 · **UI verification is the user's job**: the skill runner must not spin up Chrome MCP + local HTTP server to preview the deck itself. The user is the authoritative judge of rendering; self-verification wastes time without catching cascade/font-fallback bugs (which look "fine" to headless Chrome too).
- General rule at end of `html-deck-gotchas.md`: **"the first keyboard arrow is the cheapest QA"** — instruct the user to open the file and press `→` once to confirm slide 1 disappears. A 5-second check that catches the most common cascade bug every time.

### Changed
- `SKILL.md` Step 4 · now opens with `Before writing any HTML, read references/html-deck-gotchas.md` (parallel to the pptx-gotchas.md directive in Step 5).
- `SKILL.md` Step 4 · added explicit hand-off paragraph: do **not** self-verify via Chrome MCP; send the file path + 5-second check and wait for the user.
- `SKILL.md` Reference files table · new row for `html-deck-gotchas.md`.

### Why this version exists
The **ORCHESTRA trial deck** (Gootjes et al., JAMA 2026;335(15)) journal-club run on 2026-04-23 hit the CSS specificity bug directly. Slides 2 and 3 rendered cover content overlapped on top of their own content — invisible when only viewing slide 1 — and the skill runner tried to self-verify with Chrome MCP instead of handing the file to the user immediately. The user had to open the HTML independently and ask "why do these three pages look the same?" to surface the bug. Time was lost on the round-trip. Both lessons are now codified.

### Added (naming convention)
- `SKILL.md` Step 1 · **slug-based naming rule**. The project directory and all deliverables use a paper-derived slug: trial acronym first (`orchestra-trial`, `recovery-trial`, `checkmate-577`), otherwise `<first-author-surname>-<year>-<topic-words>` (e.g., `gootjes-2026-debulking`). Normalized to lowercase-ASCII-hyphen, ≤ 40 chars. Replaces generic names like `jama-deck/`, `deck/`, `output/`.
- Step 4 emits `<slug>.html`, Step 5 emits `<slug>.pptx`. Step 6 final-message template updated to reference `<slug>.pptx`.

### Why this version exists (naming)
The ORCHESTRA run produced `jama-deck/deck.html` + `jama-deck/deck.pptx` — the names say nothing about which paper it is. Once the user accumulates 3+ paper decks in an archive folder, the filenames must carry identity. Trial acronyms are the cleanest identifier for RCTs (what clinicians actually remember the paper by); first-author + year is the standard fallback for papers without an acronym.

### Known limitations
- `html-deck-gotchas.md` starts with 2 entries. Likely more exist (font-fallback on mixed EN/CJK runs, `<img>` intrinsic-size vs container-constrained layout, keyboard focus after `requestFullscreen`). Add as they surface.
- Slug selection is agent discipline, not yet enforced by `extract_paper.py`. A future version could auto-propose a slug from `paper.json.title` and let the agent confirm.

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
- **OE extension visual cue in themes**: `data-extension="true"` marker is specified in v0.6.0 but no theme file implements the visual treatment (dashed top-rule, muted background, etc.). First deck that runs Step 3.5 through HTML should pick and commit the choice into `assets/themes/*.json`.
- **Extension-round acceptance-rate metric**: define a success metric for Step 3.5 (suggested: % of agent-proposed questions the user accepts without revision). Needs ≥3 clinical papers with extension rounds to establish baseline.
- **Non-clinical-paper extension axes**: v0.6.0 skips Step 3.5 for non-clinical papers because therapy/prognosis/diagnosis doesn't map. A ML-domain extension round would need its own axes (e.g., architecture / training / evaluation). Deferred until an ML paper actually asks for it.
