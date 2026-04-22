# Citation Format on Slides

Citations on slides have a different job than citations in papers. In a paper, `[12]` is a pointer into a reference list the reader has beside them. On a slide, `[12]` is a visual artifact the audience can't resolve — they have no reference list, they're not going to ask you for it. So slide citations must carry meaning on their own, or they're noise.

This reference gives concrete formats by context, not principles.

---

## Two hard rules

1. **Never use numbered citations (`[1]`, `[12]`, `[21,22]`) on slides.** They're information-free to the audience. The exception is when recreating the paper's own figure with its original numbering intact — in that case the numbers are part of the figure, not the slide's text.

2. **Use author-year for everything meaningful, or no citation at all.** "Smith 2023" beats `[7]`. "Recent work" beats "Smith 2023, Jones 2024, Chen 2024, Park 2024, Lee 2025" — if you need more than two author-year tags inline, summarize verbally ("several recent studies").

---

## Five slide contexts, five formats

### 1 · The paper you're presenting (the whole deck is about it)

Put the citation **once** on the cover slide and **once** in the chrome footer on every content slide. Format for the footer:

```
FirstAuthor et al. · Journal 2025
```

Keep it short. Full bibliographic info lives on the cover and takeaway slide.

Do **not** repeat the full `(Smith, Jones, and Chen, 2025, The Lancet, Volume 405, pages 257–272)` on every slide. That's slop (looks like legal boilerplate, adds no information).

### 2 · Contextual / background citations (not the paper's own)

When citing prior work that the paper builds on, or baseline comparisons, use `(Author Year)` inline at the point of mention:

> Before 2015, only class X existed for broad coverage of pathogen Y (Pankey 2005).

Or, less cluttered, in a small callout at slide bottom keyed to the topic:

> Data from Pankey 2005; XYZ trial (Secondary et al. 2023)

The callout version works when multiple claims on one slide each have a source — collecting them at the bottom avoids littering citations through the body text.

### 3 · Figure reproduced from the paper being presented

On the figure slide itself, beneath the figure image:

```
Figure 3, FirstAuthor et al. Journal 2025
```

18px, muted color (not accent), no italics. If the deck is going to be recorded or public, use the fuller form from `figure-attribution.md`.

### 4 · Figure or data from a *different* paper

```
Figure 2 reproduced from Secondary et al. XYZ trial, Journal 2023
```

Include the study shorthand (`ATTACK trial`) when the audience will know it by that name — this is more useful than the citation. If the audience wouldn't recognize the trial name, drop it.

### 5 · Table data summarized from multiple papers

Either:
- Put a single source line beneath the table: `Compiled from PrimaryReview 2025 and relevant society guidelines`
- Or, if the table aggregates many sources, put row-level citations in a right-most "source" column in tiny type (14–16px).

Don't put `[1][2][3]`-style numbers in table cells. If you need to track which cell came from which source at the table-construction stage, keep that in a separate working notes file, not on the slide.

---

## References slide (end of deck)

Many presenters make a final "References" slide listing 30+ papers at 10pt. **Don't.** Rules:

- **If the deck is a review of ONE paper**: the cover + takeaway slide already carry the full citation. A references slide is redundant. Skip.
- **If the talk cites ≥5 outside papers**: put a references slide with author-year list, organized by topic (not alphabetical). Use 18–20pt, not 10pt — if it's not readable, it's not there for the audience, it's there for plausible deniability.
- **If the talk is recorded or will be distributed**: include a references slide with full citations, as a record. Design it as a slow-pace readable slide, not a wall of text.

Format for a references slide:

```
References

FirstAuthor A, SecondAuthor B, ThirdAuthor C. Paper title here.
  Journal Name 2025;123:101–120. doi:10.xxxx/placeholder

OtherAuthor D et al. Secondary study title.
  Other Journal 2023;45:1000–1020.

GuidelineGroup. Society clinical guidance 2024.
  Guidelines Journal 2024;10(1):e1–e49.
```

Use hanging indent so author names are easy to scan. Group by topic with a small accent eyebrow if >8 references.

---

## The speaker-notes alternative

For citations that matter to *you* but not to the audience, put them in speaker notes, not on the slide:

> Speaker note: The 30–50% mortality figure comes from Paul et al. 2018 (Pseudomonas bacteremia) and Lemos et al. 2014 (CRAB cohort). If asked, cite both.

This keeps the slide clean and equips you to answer "where did you get that number?" without the audience seeing a citation wall.

---

## Venue-specific conventions (brief)

Different communities have different norms for inline citation style. Don't overthink this, but be aware:

- **Medicine** (NEJM, Lancet, JAMA): superscript numeric in papers, author-year on slides by common convention.
- **Biology / life sciences** (Nature, Cell): author-year both in papers and slides.
- **Computer science / ML** (ACM, IEEE, NeurIPS): numeric in papers, **often numeric even on slides** — but the rule above still applies (numbers alone are useless). Follow the "citation + first-author name" shortcut: "[3, Vaswani et al.]".
- **Physics / chemistry**: numeric citations common. Same fix — "[5, Johnson group]".

When in doubt, author-year wins cross-venue.

---

## The footer citation template for this skill

Default chrome footer format used throughout this skill's generated decks:

```
[lead author] et al. · [journal] [year]                           [page] / [total]
```

Examples:
- `FirstAuthor et al. · Journal 2025                                     12 / 20`
- `Vaswani et al. · NeurIPS 2017                                    05 / 18`

This fits in a 20px muted line at the bottom of every slide, is readable at projection distance, doubles as attribution and progress indicator. When a slide cites additional work beyond the paper itself, add a second line or replace the footer with the more specific source — but always keep the citation compact.
