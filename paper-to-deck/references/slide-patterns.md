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
