# Interview · Question Bank

The interview is the single most important step. It turns a vague "make slides" request into a concrete design contract. **Always ask at least 10 questions; at least 4 must be paper-specific.**

Questions should be presented all at once (not sequentially) so the user can batch-answer. Each question offers 3 suggested options + "Other" + "Decide for me".

Organize the 10 final questions across these 6 categories. Pull from the banks below, and **write 4+ paper-specific questions** by substituting concrete artifacts from `paper.json` (section names, figure numbers, table labels, specific claims).

---

## Category A · Audience (pick 1–2)

### A1. Who's the audience?
- a) Same field, same subfield — peers who know the jargon
- b) Same field, different subfield — need mild context
- c) Broader field (e.g., "ML researchers" when paper is on a niche ML topic)
- d) Non-expert (e.g., undergrads, general science audience)

### A2. What's their relationship to the work?
- a) Colleagues evaluating methodology (journal club)
- b) Students learning (seminar / lecture)
- c) Reviewers / advisors (formal evaluation)
- d) Conference attendees (promoting the work)

### A3. What do they already know coming in?
- a) They've read the abstract only
- b) They've skimmed the paper
- c) They haven't seen it at all
- d) They know the area but not this paper specifically

---

## Category B · Format & length (pick 1–2)

### B1. How long is the talk?
- a) 5 min lightning talk / poster pitch (3–6 slides)
- b) 15 min conference talk (10–15 slides)
- c) 30–45 min seminar / journal club (20–30 slides)
- d) Custom — I'll tell you slide count directly

### B2. Presentation context?
- a) Live presenter + Q&A — speaker notes matter
- b) Standalone / async viewing — slides must be self-explanatory
- c) Background screen while presenter talks — minimal text
- d) Handout / print too (need denser slides)

### B3. Questions from audience expected?
- a) Yes, many — leave hooks in limitations slide
- b) Yes, few — standard Q&A at end
- c) Probably none — structured briefing

---

## Category C · Emphasis (pick 2)

### C1. What's the single most important thing the audience should leave remembering?
- a) The main result (X outperforms Y by Z on benchmark B)
- b) The method / technique itself (how they did it)
- c) The framing / new perspective (a shift in how the field thinks)
- d) The implication / what this means going forward
- e) Other — you tell me

### C2. Methods depth?
- a) Deep — audience will want to reproduce (method-heavy talk, 30%+ slides on method)
- b) Medium — one clear method slide, focus shifts to results
- c) Light — treat method as a black box, just say what it does

### C3. Results coverage?
- a) Show all main results + ablations
- b) Show main results only, mention ablations verbally
- c) Show one hero result + one surprising secondary result
- d) Let me pick 2 figures from the paper manually

### C4. Related work?
- a) Dedicated slide with citation grid
- b) Woven into context slide, no separate slide
- c) Skip — audience knows the area

---

## Category D · Design style (pick 1–2)

### D1. Visual style?
- a) Conservative academic — white background, serif, minimal color (matches most journal venues)
- b) Modern minimal — lots of whitespace, single accent color, sans-serif, magazine-like
- c) Lab branded — match a provided template (ask user for template)
- d) Bold / editorial — oversized typography, asymmetric layouts (for public talks)

### D2. Figure treatment?
- a) Leave figures as-is from the paper (preserve authorial intent)
- b) Re-crop / re-color to match deck palette (risk: distorts original)
- c) Simplify / redraw (only if I have confirmation from you — high risk)

### D3. Color accent?
- a) Match the dominant color in Figure 1 (auto-detected)
- b) Default muted navy (`oklch(0.45 0.15 250)`)
- c) I'll give you a hex value
- d) Match a venue (e.g., NeurIPS dark blue, Nature black+red)

---

## Category E · Language (mandatory)

### E1. Output language?
- a) English (default)
- b) Chinese (全中文)
- c) Bilingual — English slide titles + Chinese body
- d) Bilingual — Chinese slide titles + English body (for international audience with Chinese speaker)

### E2. Speaker notes language?
- a) Same as slides
- b) Chinese (even if slides are English) — most useful for Chinese-speaker practicing
- c) English (even if slides are Chinese)
- d) No speaker notes needed

---

## Category F · Typography (mandatory, ask AFTER all category A–E questions)

This question comes **last** in the interview, after audience / format / emphasis / design / language are settled. By then the user has enough design context to make an informed font choice; asking too early produces weak answers.

### F1. Slide font?
- a) **Taipei Sans TC Beta** — default. Clean, legible, loads from jsdelivr, handles both Latin and Traditional Chinese without fallback drift. Matches the house style decks this skill has produced before.
- b) **Microsoft JhengHei** — safest for Windows audiences where the Beta font may not be installed locally. Fallback-friendly for PowerPoint.
- c) **Noto Sans TC** — if you want a slightly more open feel; requires Google Fonts load in HTML or local install for PPTX.
- d) **Serif preferred** (e.g. Source Han Serif TC / Noto Serif TC) — for editorial or medical-review tone; pairs well with modern minimal style when prose-heavy.
- e) **Custom** — tell me the font name and whether it's installed locally or needs a web source.
- f) Decide for me — I'll use Taipei Sans TC Beta (the house default).

**When telling the user about this question, present it as:** "Last one — what font? Default is Taipei Sans TC Beta; other options if you want a different feel."

---

## Category G · Paper-specific (write ≥ 4 of these)

These must be generated per paper. Look at `paper.json` and pick concrete handles. Templates:

### G-template · Lead result
> The paper reports multiple results — `<list top 2–3 headline numbers from the abstract>`. Which one leads?
- a) `<result 1>`
- b) `<result 2>`
- c) `<result 3>`
- d) Mix — tell me the ordering

### G-template · Which ablation
> Table `<N>` shows ablations on `<list conditions>`. Which matters most to your audience?
- a) `<condition 1>`
- b) `<condition 2>`
- c) All of them (one slide each)
- d) None — cut ablations

### G-template · Lead figure
> The paper has `<count>` figures. Pick the hero for slide 1:
- a) Figure 1 (`<caption summary>`)
- b) Figure `<N>` (`<caption summary>`)
- c) Figure `<M>` (`<caption summary>`)
- d) Make a new title slide without a figure

### G-template · Contribution framing
> The abstract lists these contributions: `<bullet list>`. Which is the real novelty to lead with?
- a) `<contribution 1>`
- b) `<contribution 2>`
- c) `<contribution 3>`
- d) Different framing — I'll tell you

### G-template · Method complexity
> The method section has `<N>` subsections (`<list names>`). Which need to be on slides?
- a) All of them
- b) Just `<section name>` — the key innovation
- c) A diagram replacing them all
- d) Verbal only, no method slide

### G-template · Baseline comparison
> The paper compares against these baselines: `<list>`. Do you want:
- a) All baselines on one slide (full table)
- b) Just the strongest baseline (for a clean bar chart)
- c) A curated subset — tell me which
- d) Skip baselines entirely

### G-template · Limitation emphasis
> The paper acknowledges these limitations: `<list or "none stated explicitly">`. In the talk:
- a) Dedicated limitations slide (academic honesty)
- b) Woven into discussion, no separate slide
- c) Skip — audience will ask about them in Q&A
- d) Reframe as "future work" (softer)

---

## Presenting the questions

After extracting the paper, write your chosen questions (minimum 10) in this single-message format. **Typography is always last** — it comes after the user has answered everything else, when they have enough context to make an informed font choice.

```
I've read the paper. Before I draft slides, I need your input on N decisions.
(Answers are letters, e.g., "Q1: a, Q2: c, Q3: Other — ...")

**Audience**
Q1. ...
Q2. ...

**Format**
Q3. ...

**Emphasis**
Q4. ...
Q5. ...

**Design style**
Q6. ...

**Language**
Q7. ...
Q8. ...

**Paper-specific**
Q9. ...
Q10. ...
Q11. ...
Q12. ...   ← at least 4 paper-specific questions

**Typography** (last — default font is Taipei Sans TC Beta, other options if you want a different feel)
Q13. ...

If any question doesn't matter, answer "e) Decide for me" and I'll use the default.
```

Wait for all answers. Do not proceed to outline until the user has responded. If the user answers the earlier questions but forgets Typography, ask it once before moving on — don't just assume the default silently (the point of the question is to give them the option).
