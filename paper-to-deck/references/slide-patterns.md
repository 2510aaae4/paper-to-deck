# 8 Canonical Research-Slide Patterns

Most research decks are combinations of these 8 patterns. Knowing the pattern tells you the layout and the speaker-note shape. Patterns are listed in the **default narrative order**; most decks use 5–7 of them.

## Universal rules before you touch any pattern

These apply to every slide regardless of which pattern it instantiates. They're the most common failure modes in draft decks.

1. **Title is an argument, not a label** — for content slides (everything after the cover). Write titles as statements or questions: "Carbapenemase type drives the drug choice" (argument) beats "CRE Treatment" (label). "Figure 3" / "Methods" / "Results" are labels. The **cover slide is an exception** — its job is to let the audience immediately identify which paper is being discussed, so showing the paper title prominently is correct, not slop.

2. **Body text ≤ 40 words per slide.** If a slide is denser than this, one of three things is true: it wants to be two slides, the detail belongs in speaker notes, or you haven't decided what the one main point is. Resolve before building.

3. **Figure attribution goes in the caption, not the title.** The audience doesn't need to know which figure number in the paper this is. The title is the insight; `(Figure 3)` sits quietly in the caption line beneath the image.

4. **If the layout invites density, use a denser discipline.** Two-column "what is it / why it matters" layouts are density traps. Use them only with one-line drug-row lists, 2–3 short bullets, or single-phrase statements per column. Never full paragraphs in both columns.

---

## P1 · Hook
**When**: Slide 1 (after or in place of a title slide). **Not** the paper's title card.

**Purpose**: Earn the next 30 seconds of attention. The title slide is bureaucratic; the hook is editorial.

**Content options**:
- A single striking number from the paper ("87.3% accuracy on X — up from the previous 62%")
- A one-sentence problem statement that resonates with the audience's daily pain
- A before/after figure (system without method vs. with method)
- A counterintuitive finding stated as a question

**Layout**: Big type, minimal text, optional single figure. Title goes at the bottom as a footnote, not at the top.

**Speaker note shape**: Set the stakes. Why should they care. ~30 seconds.

---

## P2 · Context
**When**: After hook, before the research question. Skip if audience is deeply in-domain.

**Purpose**: Give the listener the minimum mental model to understand why the research question is a question.

**Content options**:
- A visual taxonomy (tree / 2×2 / timeline) placing this paper in the field
- A single equation / concept defining the setup
- The key prior result the paper builds on (1 citation, shown clearly)

**Layout**: Diagram dominates, 2–3 bullet captions.

**Speaker note shape**: "Here's what's known, here's what's missing." ~45 seconds.

---

## P3 · Research question
**When**: After context. Sometimes merged with Context into one slide.

**Purpose**: State precisely what the paper is trying to answer. The slide everyone will screenshot.

**Content**: A single crisp question or hypothesis, large type, no figure. Optional tiny diagram showing the boundary of the question.

**Layout**: Mostly empty slide, one question in 48–60px type, centered.

**Speaker note shape**: "After this slide, the rest of the talk is the answer." ~20 seconds.

---

## P4 · Method
**When**: Variable — skip if audience doesn't need reproducibility; expand to 3 slides if they do.

**Purpose**: Explain the how at the resolution the audience needs.

**Content options** (by depth):
- Light: One diagram of the pipeline with 3–5 named stages
- Medium: Pipeline diagram + one slide zooming into the novel component
- Deep: Pipeline + novel component + key equations + pseudocode

**Layout**: Diagram dominates. Bullets only label diagram parts — no free-standing bullet lists.

**Speaker note shape**: "Here's what's new vs. what's standard." Lean into the novel part.

**Anti-pattern to avoid**: reproducing the paper's Figure 1 (usually too detailed for a slide) without simplification.

---

## P5 · Key result
**When**: The heart of the talk. Usually 1–3 slides.

**Purpose**: Show, don't tell, the main finding.

**Content options**:
- The hero figure from the paper, re-cropped to fit slide format
- A bar chart of the headline metric with 1–3 baselines
- A qualitative example (for generative work: input → output comparison)
- A table — but **only if** the rows can be read at 24px from the back of the room (usually ≤ 4 rows)

**Layout**: Figure takes ~70% of slide width. Left or right side holds a 1-sentence "so what" — what the figure means, not what the figure shows.

**Speaker note shape**: "The number to remember is X." State it out loud. Explain what the baselines mean.

---

## P6 · Discussion / Deeper finding
**When**: After key result, before limitations. Optional.

**Purpose**: The interpretation layer — the "here's why this result is interesting" that distinguishes a talk from a results dump.

**Content options**:
- An unexpected secondary finding (ablation, edge case, failure mode)
- A connection to an adjacent field
- A proposed mechanism / why the method works

**Layout**: Text-heavier than result slides. One supporting figure optional.

**Speaker note shape**: "You wouldn't have known this from just reading the abstract."

---

## P7 · Limitations
**When**: Before takeaway. Academic audiences expect it; skip for promotional contexts.

**Purpose**: Build credibility by acknowledging boundaries honestly.

**Content**: 2–4 bullet points, each 1 sentence. No apologizing, no overclaiming.

**Layout**: Text-only is fine. Can merge with "Future work" if both are short.

**Speaker note shape**: "Here's where this doesn't apply yet." ~30 seconds.

**Anti-pattern**: overselling limitations to preempt reviewer concerns — makes the work sound weaker than it is.

---

## P8 · Takeaway
**When**: Last content slide (before Q&A / thanks).

**Purpose**: The one thing they remember walking out.

**Content**: 1–3 bullet points. Echo the hook if possible — closes the loop.

**Layout**: Same typography as the hook for visual symmetry. Add a single "find the code / paper" URL at bottom.

**Speaker note shape**: "If you leave with just one thing..."

**Anti-pattern**: restating the abstract as bullet points. The takeaway is editorial, not a recap.

---

---

## P9 · Thematic review layout (non-IMRAD papers)
**When**: The paper is a review, survey, or meta-analysis covering many primary studies. The IMRAD narrative arc (P1–P8) does not apply — there is no single research question, no one method, no one key result. Instead, the paper is organized by themes, mechanisms, or domains.

**Purpose**: Present the review's conceptual structure in a way the audience can navigate. A review talk is a map, not a story.

**Content structure**: Treat each major theme of the review as a "chapter" of the deck. Within each theme, use:
- A theme-opening slide with the theme's question or claim stated in one line (title).
- 1–3 content slides elaborating the theme (can still use P4 Method / P5 Key Result internally if the theme has a canonical study).
- A transition to the next theme — either a verbal bridge or a single bridge slide.

**Layout**: Consider including a "table of contents" slide after the cover — a small matrix listing the themes with brief one-line descriptions, that the audience sees once and can recall when you reference "moving on to theme 3". Avoid elaborate navigation UI — a simple numbered list is enough.

**Speaker note shape**: Each theme-opening slide needs a 20–30 second "why this theme matters in the field" preamble, not an information dump. The content slides within the theme can have regular talk-track density.

**Anti-pattern**: Treating a review like a primary paper and forcing an IMRAD arc onto it. This produces a slide deck with a fake "research question" that the paper never asked, and a "key result" that doesn't exist. Review talks are navigation exercises, not argument builds.

**Example structure for a 5-theme review**:
- Slide 1: Cover
- Slide 2: Hook (single striking number or claim from the review)
- Slide 3: Map (the 5 themes listed)
- Slides 4–6: Theme 1 (open + 1–2 content slides)
- Slides 7–9: Theme 2
- Slides 10–12: Theme 3
- Slides 13–15: Theme 4
- Slides 16–18: Theme 5
- Slide 19: Cross-theme synthesis (if the review offers one)
- Slide 20: Takeaway

In practice, for a clinical review this skill built during development, the mapping was collapsed — context / mechanisms / diagnosis / treatment / prevention treated as one flow with treatment expanded. This works when themes are naturally sequential. For reviews with parallel themes (e.g. "five emerging technologies in X"), keep them visually parallel — one slide structure per theme.

---

## Choosing a pattern mix

| Format | Typical pattern sequence |
|---|---|
| 5-min lightning | P1 → P3 → P5 → P8 |
| 15-min conference | P1 → P2 → P3 → P4 → P5 → P7 → P8 |
| 30-min seminar | P1 → P2 → P3 → P4 (expanded to 2–3 slides) → P5 (2–3 slides) → P6 → P7 → P8 |
| Journal club (primary research) | P1 → P3 → P4 → P5 → P6 → P7 → P8 (heavier on method and limitations) |
| Journal club (review/survey paper) | **P9** — abandon IMRAD; use thematic structure. See P9 above. |
| Overview 1–3 slides | P1 merged with P3; one slide on P5; one slide on P8 |

## Transition rule

Between every two slides, ask: does the speaker have a clean sentence connecting them? If not, one of the two slides is in the wrong place or shouldn't exist. This is the single best test for narrative coherence.

---

# Medical-teaching visual archetypes

P1–P9 above are **narrative** patterns (what story each slide tells). This section covers **visual** archetypes (how each slide is laid out) for the medical-teaching style introduced in v0.5.0. Narrative and visual are independent — a P5 Key Result slide can be rendered as either V4 Finding or V5 Table, for example.

The archetypes below were reverse-engineered from two NCKU 內科 Year Review reference decks (infectious disease and endocrinology). They're not the only valid visual vocabulary — but when the user opts into the medical-teaching theme, these are the building blocks.

## Palette

| Token | Hex | Role |
|---|---|---|
| `text.body` | `#000000` | Main text |
| `accent.red` | `#D62027` | Eyebrows, emphasised words, warnings |
| `structure.teal` | `#1E4A5F` | Cover block, branded footer, secondary eyebrow |
| `pastel.pink` | `#F8D7DA` | Takeaways grid, concept blocks |
| `pastel.green` | `#D4EDDA` | Takeaways grid, concept blocks |
| `pastel.yellow` | `#FFF3CD` | Takeaways grid, concept blocks |
| `pastel.cream` | `#FAEBD7` | Takeaways grid, concept blocks |
| `pastel.blue` | `#D0E7F5` | Takeaways grid, concept blocks |
| `text.muted` | `#6C757D` | Citations, footnotes, attributions |

Do **not** introduce additional hues without amending this table. Consistency across a deck is worth more than variety within it.

## Typography

- **Display** (slide title, cover title, eyebrows): Inter Black / Arial Black for Latin; Taipei Sans TC Beta Bold for Traditional Chinese. Sizes: cover 60–80pt; slide title 40–60pt; eyebrow 16–20pt.
- **Body**: same family, Regular or Medium. Size 24–28pt; never below 20pt on a content slide.
- **Citation / footnote**: same family, 10–12pt, `text.muted` colour.
- **Mixed-language runs** (EN + ZH on the same line): use the Traditional Chinese font family's Latin glyphs, not a separate Latin fallback — mixed-font runs produce inconsistent x-heights that look amateurish.

## Archetypes

### V1 · Cover — three variants

Pick one per deck via interview Q15:

**V1a · Mascot cover** (deck-1 flavour)
- Top eyebrow: journal / venue name (centred, `text.muted`, ~28pt)
- Middle: paper title in `structure.teal`, centred, ~70pt bold
- Lower-left: mascot figure (cartoon character, paper thumbnail, organism illustration) — occupies ~30% width
- Lower-right: author block, right-aligned, ~24pt (name / division / institution)

**V1b · Teal-block cover** (deck-2 flavour)
- Top third: solid `structure.teal` rectangle, full width
- Inside the rectangle: eyebrow top-left (white, ~28pt); paper title centred (white, ~60pt bold)
- Lower two-thirds: white background with institution logo (left) + large author name (right), ~40pt bold
- Bottom-right: date, ~16pt `text.muted`

**V1c · Minimal cover**
- Paper title centred, black, ~60pt bold
- Author block beneath, 3 lines, ~24pt
- No mascot, no institutional branding
- Use when the paper is a serious primary trial (mortality RCT, safety study) where mascot levity would be inappropriate

### V2 · Part divider (opt-in)

When: deck has ≥ 20 slides and the user kept part-divider toggle on. Used to separate major narrative sections ("Part 1: Background" → "Part 2: Methods" → "Part 3: Key findings").

- Red eyebrow top-left: "Part N: short-description" (~20pt, `accent.red`, bold)
- Middle: section title, centred, black bold, ~50pt
- Optional: a single supporting image below the title (paper schematic, chapter-opening figure), ≤ 40% slide height

Skip for decks under 20 slides — dividers eat slides the audience doesn't need.

### V3 · Concept slide

Best for definitions, frameworks, mnemonic-heavy teaching (5R, 6P, ABCD checklists).

- Red eyebrow top-left (optional section label)
- Black bold title, centred or left-aligned — usually a question ("What is X?") or a definition stub
- Two-column body:
  - Left: bullet list with the **first letter of each mnemonic** bolded in `accent.red` (e.g. `P`enetration / `P`orin / `P`ump)
  - Right: pastel-filled illustrative blocks or a textbook-style diagram
- No citation if the definition is general; include if from a specific textbook

### V4 · Finding slide

For primary and secondary results. The title does the thesis work.

- Title: black bold declarative statement (20–60pt depending on length). "Late-career physicians prescribe longer courses" beats "Physician career stage vs. prescribing duration".
- Body: large figure (chart, forest plot, scatter) at ~70–85% slide width
- Right or below the figure: a short legend / key number in a small pastel block
- Bottom-left citation: 10pt `text.muted`, one line (e.g. `Clin Infect Dis. 2019;69(9):1467–1475.`)
- No separate "results" label — the title is the result

### V5 · Table slide

For comparative data, drug selection tables, penetration/dose references.

- Title: bold black, often with a superscript footnote marker for the bilingual note
- Native editable PPT table (not a crop) — see `pptx-gotchas.md` on table-cell run formatting
- Header row: coloured fill (green = favourable, red = unfavourable, teal = neutral category)
- Below the table:
  - Citation(s), 10pt `text.muted`
  - Optional bilingual clinical note: a single sentence in the user's interview-chosen body language explaining *why this table matters at the bedside*. When body language is "mixed", the clinical note is Chinese; when pure EN, omit the note.

### V6 · Collage slide

For historical context, multi-subpanel comparison, "here are the three key guidelines" screenshots.

- Title: bold black, centred
- Grid: 2, 3, 4, or 6 images (subpanel split, guideline screenshots, or historical collage)
- Each image has a small caption below: 1 line, ~12pt
- One overarching citation bottom-left if all images share a source

### V7 · Key Takeaways grid (opt-in)

Replaces a single-slide "Conclusion". When the interview toggles this on, the final content slide becomes a 6–8 pastel-tile grid.

- Small italic eyebrow above the title: the framing sentence ("Every prescription matters — we are the guardians of antibiotic effectiveness")
- Title: "Key Takeaways" (or Chinese equivalent), ~50pt bold
- Grid: 2×3, 2×4, or 3×3 depending on item count
- Each tile: one pastel fill colour, a bold mini-headline (~22pt), 2–3 short lines (~16pt)
- Below the grid: optional closing italic line, centred

Anti-pattern: dumping every slide's takeaway into the grid. Pick the 6–8 that matter; the rest belong in the body slides.

### V8 · Branded footer strip (opt-in, across all body slides)

When the user supplies institution / division text in Q16, every body slide (not cover, not takeaways) gets a `structure.teal` horizontal strip at the bottom:

- Strip: 20–25pt tall, full-width, `structure.teal` fill
- Text: white, left-aligned, 14pt (e.g. "College of Medicine, National Cheng Kung University")
- Optional right-aligned: small institution logo

Do not combine with V2 part-divider strip (two structural strips on one slide looks busy — drop the footer on divider slides).

## Pop-culture memes and manual-only imagery

The medical-teaching style treats memes / pop-culture images as a legitimate mnemonic device (Shrek → acromegaly facial features; Jurassic Park raptor → virulence analogy). These images are **copyrighted** and the skill does **not** fetch them. When the user's imagery candidate list includes a meme slot:

- Agent marks the slide `[manual-only: insert meme for <concept>]` in outline
- HTML and PPTX render a placeholder rectangle with the description
- Agent does not substitute a generated-image approximation; memes only land through the user's own manual paste

## When to use which archetype

| Narrative pattern | Default visual archetype | When to deviate |
|---|---|---|
| P1 Hook | V4 (Finding) or V1 (oversized cover) | — |
| P2 Context | V3 (Concept) or V6 (Collage) | V6 when historical |
| P3 Question | V3 centred, text-only | Use V4 if a one-image setup is clearer |
| P4 Method | V3 two-column or V6 subpanel | — |
| P5 Key result | V4 (Finding) | V5 if the result lives in a table |
| P6 Discussion | V3 or V4 | — |
| P7 Limitations | V3 bullet-only, no figure | — |
| P8 Takeaway | V7 (Takeaways grid) if ≥ 6 points; else V3 | — |
| P9 Thematic review | Map slide = V3; theme opens = V1b-style mini | — |

## Opt-in summary (controlled by interview Q14–Q17)

| Toggle | Interview question | Default | Effect if on |
|---|---|---|---|
| Visual scheme | Q14 | crimson-blue | Swap palette tokens for deck-2-flavour teal-first |
| Cover template | Q15 | V1a mascot | V1b teal-block / V1c minimal |
| Branded footer | Q16 | off | V8 strip on every body slide |
| Body language | Q17 | EN | ZH or mixed (EN key terms red + ZH prose) |
| Takeaways grid | derived from Q4 and slide count | off | V7 replaces final content slide |

Part dividers (V2) are auto-enabled when deck length ≥ 20 slides; can be suppressed in Q15 free-response.
