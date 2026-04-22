# Evals · `paper-to-deck`

This directory is the skill's memory for **what a correct run looks like**. Each eval captures a real paper + interview + expected output, so future skill revisions can be re-run against it and regressions caught.

## Files

- **`evals.json`** — the eval case library. One entry per paper we've run the skill on. Each entry records: the user's prompt, the interview answers, what files should be produced, design invariants that must hold, and known limitations.
- **`runs/`** (created on first run) — per-eval output workspace. One subdirectory per eval ID, with the actual outputs from the most recent skill execution, plus a `grading.md` noting what passed or failed the invariant checks.

## Philosophy

An eval isn't a unit test. Paper-to-deck outputs are design artifacts — judged mostly by a human eye. But some properties are objectively checkable without a human:

- Did the script produce the expected files?
- Are the structural invariants met (slide count, figure count, bilingual pattern correct)?
- Do the automated verification checks (`references/verification.md` Tier A) pass?

Those are what the eval harness should catch. Design-quality judgment stays with the human review.

## When to add a new eval

Whenever a new paper exposes a behavior the current evals don't exercise:
- Different publisher (Nature, IEEE, arXiv) — tests extraction tiers
- Different length format (lightning talk, long seminar) — tests pattern mix
- Different language setting (Chinese slides, bilingual) — tests language handling
- Different content type (theory-heavy, equation-heavy, many-tables) — tests content rendering

`evals.json`'s `candidate_next_evals` section tracks what we haven't covered yet. Pick from there when you have a real paper that fits.

## When NOT to add a new eval

- Minor variations of existing cases (same publisher, same format) — redundant.
- Hypothetical cases without a real paper file — evals should be driven by real incidents, not imagined ones.

## How regressions show up

Every eval entry has a `regression_signals` block listing behaviors that would indicate a recent skill change broke something. When a skill change is made, re-run the affected eval and check those signals first — they encode the hard-won lessons (like "cover slide MUST show paper title" per user pushback in v0.2.0).

## Running an eval

There's no automated runner yet — for now, the loop is manual:

1. Copy `evals.json` entry `N` to a fresh workspace (`runs/eval-N/`).
2. Execute the skill on the specified paper with the specified interview answers.
3. Compare outputs to `expected_outputs`.
4. Check `regression_signals` — any hit means a regression.
5. Record observations in `runs/eval-N/grading.md`.

When the skill matures enough, this loop becomes a Python script. For now, the manual version is enough — we're running it once per skill release, not continuously.
