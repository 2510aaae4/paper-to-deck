# OE Extension Round · Step 3.5

A short agent-facilitated round between **outline approval** and **HTML building**. The agent proposes 3–4 evidence-based-medicine questions that **extend** the paper — not challenge it — and each approved question becomes one slide appended near the end of the deck.

## Why this step exists

The obvious use of OpenEvidence (OE) on a clinical paper is citation audit: verify numbers, flag overclaims. That framing was tried once (Tande 2026 SEA deck, slide 22) and produced a technically correct but tonally wrong result — the audit report read as adversarial, and the outputs weren't things you could drop into a journal-club deck. The rework reframed OE as an **extender**: after the paper is presented faithfully, what does the literature say about the three or four clinical questions this paper most obviously raises in a listener's head? Those questions become slides at the end, so the deck opens with "what the paper says" and closes with "what this paper does not answer."

This also sidesteps a subtle problem with using OE on the paper's own numbers: OE pulls from downstream literature that **itself cites** the paper you're auditing, so "external verification" can be more circular than it looks. When the question is *what lies beyond the paper* rather than *is the paper right*, that circularity stops mattering.

## When to run this step

After the outline is approved (end of Step 3) and before any HTML is written (start of Step 4). Specifically:

- Skip if the paper is non-clinical (ML / physics / engineering papers don't have therapy/prognosis/diagnosis axes — use domain-appropriate extension axes or skip).
- Skip if the user's audience (`design_brief.json` A1) is non-medical or the talk is <10 slides (no room to append 3–4 extension slides).
- Skip if the user explicitly opts out in Q-extension (see below).

## Prerequisites

- `OE_AVAILABLE=true` was carried forward from `start` Step 0b. If `start` recorded `OE_AVAILABLE=false` (user declined, or auth couldn't be completed), Step 3.5 is **skipped silently** — do not prompt again, the user already answered upstream. Skipping means: outline goes straight to Step 4 (HTML build) without extension entries.
- If `start` was bypassed (user handed over a PDF path in their first message), `OE_AVAILABLE` is unknown. Probe once with `mcp__openevidence__oe_auth_status`: on success set `OE_AVAILABLE=true` and proceed; on failure set `OE_AVAILABLE=false` and skip. Do not attempt cookie refresh from within `paper-to-deck` — that's `start`'s job.
- Belt-and-suspenders: even if `OE_AVAILABLE=true` was carried forward, call `oe_auth_status` once at the top of Step 3.5 before running any `oe_ask`. Cookies can expire mid-session on long runs. If the live check fails, tell the user and skip the step — do not fall back to agent-synthesized "extension" slides.
- Reference to the `audit-oe-skill` project (htlin222) is intentionally **not** inherited — its PASS/CAUTION/FAIL structure applies to audit, not extension. Don't import that vocabulary.

## The user interaction

### Q-extension (ask at the top of Step 3.5)

```
Before I build HTML, want me to add 3–4 EBM extension slides at the end?
Each slide answers one question this paper raises but doesn't fully address,
verified via OpenEvidence. Axes: therapy / prognosis / diagnosis.

  a) Yes — propose candidate questions and we'll pick together
  b) Yes — just pick for me, use defaults
  c) No — skip, go straight to HTML
```

Default (if the user takes `e) Decide for me` earlier in the interview): **a**.

### Proposing candidates

If the user picks (a), propose a **bundle of 4 questions** as a single table, one question per axis plus a wildcard. Format:

| # | Axis | Flavor | Candidate question | Why this one |
|---|---|---|---|---|
| 1 | Diagnosis | A | <question> | <why this over other diagnosis Qs> |
| 2 | Therapy | B | <question> | <why this is the evidence-deepener slot> |
| 3 | Therapy | A | <question> | <why a second therapy Q rather than covering other axis> |
| 4 | Prognosis | A | <question> | <why this over other prognosis Qs> |

**Flavor rule**: mainly **A** (clinician's next-question — "what would I Google after closing this paper?"), with **at least one B** (evidence-deepener — "what does stronger downstream evidence say about the paper's weakest-evidence recommendation?"). Pure B bundles come across as methodology lectures; a single B gives the deck depth without losing the practical bent.

**Axis rule**: therapy / prognosis / diagnosis should all be represented when possible. If the paper is lopsided (pure diagnostic review, pure prognostic study), it's fine to double up on the dominant axis — say so in the "Why this one" column.

**Question-selection heuristics** (apply in priority order):
1. The paper names a gap explicitly ("no RCT exists for X", "optimal duration unclear") — turn that into a question.
2. The paper gives weak / narrative evidence for a point a clinician would actually apply ("IDSA suggests 2-week oral step-down in selected cases" → B-flavor on oral step-down trials).
3. The paper mentions recurrence / long-term outcome / surveillance in one line — audiences always want the numbers.
4. The paper's algorithm has a threshold (72h, 6 weeks, 50% rule) that's cohort-derived — B-flavor on the evidence level.
5. Avoid questions the paper answers fully — the step is extension, not redundancy check.

After the user picks, revise the bundle if asked, then move to execution.

## Execution

For each approved question, call `mcp__openevidence__oe_ask` with:

- `question`: the full English question as shown in the slide (not a paraphrase).
- `timeout_sec`: 180 (OE light responses typically land in 20–60s; 180 leaves margin for the slow path).
- `save_artifacts`: true (default).

Record `article_id` for each question — these are needed if the user later asks for follow-up queries (`original_article_id` param).

**Artifact placement**: OE persists to `%TEMP%\openevidence-mcp\<article_id>\`. Leave them there; the slide renders from your synthesis, not from the raw artifact dir. Do not copy artifacts into the deck project unless the user asks — it'd bloat `_private/` or the git repo.

## Per-slide rendering

Each extension question becomes one slide. Use the V4 (Finding) or V3 (Concept) archetype from `slide-patterns.md`, whichever fits the answer shape:

- **V4 · Finding** — when OE returns a clear headline number or effect size. Big-stat style: question as slide title, one or two numbers with short labels, one emphasis line. Example: *"How often does SEA recur after cure?"* → 3–10% recurrence (various cohorts), median <12 months, mostly same organism.
- **V3 · Concept** — when the answer is a principle / decision rule / 2×2 logic, not a number. Text-heavy, with structural typography.

### Slide-title rule for extension slides

The slide title **is the question itself**, phrased as a question (ends with `?`). This is an explicit exception to the deck-wide rule "slide title is a statement or question" — here it's always the question form, because the narrative function of the slide is *the listener considering the question before hearing the answer*. Example: "Does oral step-down change outcomes in SEA?" (title) → answer on the slide body.

### Content template

Each extension slide has:

1. **Eyebrow**: `Extension · <axis> · <N> of <total>` (e.g., `Extension · Therapy · 2 of 4`)
2. **Slide title**: the question verbatim, in question form.
3. **Body**: OE answer synthesis in ≤40 words (keep the deck-wide rule). Lead with the bottom-line number or rule; follow with one caveat or qualifier.
4. **Emphasis line** (optional): a one-sentence takeaway the audience should remember.
5. **Citation footer**: 2–3 of the strongest OE citations in author-year form. Not numbered. Not `[1][2][3]`. Format: `(Alton 2015 · Spine J; Darouiche 2006 · NEJM)`. Full bibliography entries go on the References slide at the end; extension slides share the deck's reference list, they don't maintain their own.

### Placement in the deck

Insert extension slides **before the References slide** (which is always last). Renumber footer strips accordingly. If the deck has a "Take-home" or "Takeaways" slide (archetype V7), put the extension block **between** the take-home slide and the references — the take-home is still about what the paper says, the extension is what lies beyond, and references anchor both.

Mark each extension slide with `data-extension="true"` on the `<section>` element so the HTML and the PPTX builder can apply a subtly different visual cue (e.g., dashed top-rule, or a 2% muted background) to signal *"this is not from the paper itself"*. Don't make it jarring — the audience should be able to tell without it being announced.

## Outline-stage update

When Step 3.5 completes, update `outline.md`:

- Add entries for the extension slides (one per question).
- Under each, include the `article_id` in the speaker-note hint so Step 4 can trace back to the OE artifact if the text needs refinement.
- Re-confirm the total slide count with the user — the extension round adds 3–4 slides and that may push the deck over the agreed length.

## Example (SEA journal club · Tande 2026, v0.6.0 reference run)

Bundle proposed to user (axis mix deliberately lopsided toward therapy because the paper is therapy-heavy):

| # | Axis | Flavor | Question |
|---|---|---|---|
| 1 | Diagnosis | A | Do I need whole-spine MRI for suspected SEA? What's the skip-lesion miss rate on targeted MRI? |
| 2 | Therapy | B | Does 6-week IV antibiotics remain necessary? What do OVIVA and later step-down evidence say about SEA specifically? |
| 3 | Therapy | A | After MSSA is confirmed, how quickly can vancomycin be de-escalated to nafcillin/cefazolin, and on what criteria? |
| 4 | Prognosis | A | What is the SEA recurrence rate after apparent cure, and when does it typically occur? |

User approved; the four slides became 28–31 of the 31-slide deck (slide 32 being References).

## What to hand off to Step 4

When running the HTML build:

- `outline.md` updated with extension entries + `article_id` trace.
- `design_brief.json` amended with `extension_questions` array (question text + axis + flavor + article_id).
- OE artifacts stay in temp dir — the synthesis is already in the outline.

Step 4 HTML builder reads the extension entries like any other slide but applies the `data-extension="true"` marker + question-form title exception documented above.
