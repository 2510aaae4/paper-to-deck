# Figure Attribution & Fair Use

Embedding a journal's figures in a slide deck is the default for any serious academic talk. It's also the single most common point where well-meaning researchers create IP exposure. This reference is operational — when does fair use cover the use, what attribution format minimizes risk, and when should the figure be redrawn instead of embedded.

This is not legal advice. The defaults here reflect common academic practice; when the situation is high-stakes (commercial audiences, paid events, public recordings), the user should consult their institution.

---

## Four presentation contexts, four defaults

The decision to embed vs. redraw depends on who sees the deck, not on which paper's figure you're using.

### Context 1 · Internal lab meeting / journal club
**Default: embed with short attribution.** This is the clearest fair-use scenario — small closed audience, educational purpose, non-commercial, the deck is not distributed. Attribution format: small caption beneath figure reading `Figure N, from FirstAuthor et al. Journal 2025`.

Lock-in rules: do not upload the deck to a shared drive accessible to the whole org; do not post on Slack channels with >20 people; do not send by email chain that may forward. Store on personal device or in a closed shared folder.

### Context 2 · Departmental seminar / grand rounds
**Default: embed with full citation.** Attribution format: figure number + full author list (or "et al." if ≥4 authors) + journal + year + page range. Include on every figure, either in slide caption or (preferred) on the final references slide cross-keyed with in-slide markers.

Add the DOI once at the end. If the audience includes visitors from outside the institution, treat as Context 3.

### Context 3 · Public seminar / conference session
**Default: embed, but be ready to withdraw.** Most journals' author agreements allow figure reuse in academic talks at scientific conferences — but the exact permission varies by publisher. If the talk is recorded and posted publicly (YouTube, conference website), the calculus changes: recorded distribution can fall outside "academic presentation" carve-outs.

Pragmatic rules:
- For **well-established open-access journals** (PLOS, eLife, most BMC titles, Frontiers): figures are typically CC-BY. Free to reuse with attribution.
- For **subscription journals** (Nature, Science, Cell, Lancet, NEJM, IEEE Trans.): figures are reusable under "fair use" for in-person presentation, but public video posting *may* require permission. Many publishers offer a free "reuse in presentation" license through RightsLink — 60 seconds to click through.
- If recording is planned and you haven't gotten explicit permission: **redraw the figure** (see §Redraw decision).

### Context 4 · Published derivatives (book, blog, slide share)
**Default: obtain written permission OR redraw.** Any deck posted on SlideShare, embedded in a paper, included in a thesis bound for library deposit, or compiled into a book chapter is a published derivative. The author retains copyright on their figures (unless assigned to the publisher, which is the usual case for subscription journals), and publishers' permission is typically required.

RightsLink requests for "republication in a book" cost money; for a thesis, most journals waive the fee. For a blog: redraw.

---

## Attribution format specification

When embedding an original figure, use this format, adapted to the venue:

**Minimal** (Context 1, on the slide directly, 16px or ~9pt in a 1920×1080 deck):
```
Fig N, FirstAuthor 2025
```

**Standard** (Context 2, beneath the figure, 18px / 10pt):
```
Figure N reproduced from FirstAuthor X et al. Journal 2025;XXX:YYY–ZZZ.
```

**Full** (Context 3, on a dedicated references slide keyed by in-slide markers):
```
[Fig N]  Reproduced from FirstAuthor A, SecondAuthor B, ThirdAuthor C.
         Paper title goes here.
         Journal 2025;XXX:YYY–ZZZ. doi:10.xxxx/placeholder.
         Used with permission (license ID XXXXXXXX) / under fair use for
         academic presentation.
```

Include the license ID on any figure where permission was formally obtained.

**Never**:
- Crop out the author's figure caption text without replacement. The caption identifies the figure in the source — losing it makes attribution ambiguous.
- Modify the figure (recolor, crop to change meaning, add/remove elements) and then attribute it as the author's work. Either attribute the modification ("Figure N, adapted from FirstAuthor 2025 — labels added") or redraw.

---

## The redraw decision

Ask these in order. First "yes" answer chooses the action.

1. **Is the figure's content mostly data (chart, bar graph, line plot) with few stylistic elements?** → **Redraw** with matplotlib/D3/Graphpad. Data isn't copyrightable; the specific visual rendering is. A fresh rendering from the paper's reported numbers sidesteps IP entirely and usually looks better on a slide anyway.

2. **Is the figure a schematic / diagram you can reproduce from the paper's description?** → **Redraw**, in the deck's own typography and color system. This is the best case — gains IP safety AND visual consistency across the deck.

3. **Is the figure a clinical image (histology, radiograph, gel), microscopy, or photographic result?** → **Embed** with attribution. These are not reproducible from description; you need the authentic image.

4. **Is the figure a stylized illustration that would take significant effort to redraw (complex flow diagrams with many labels, multi-panel composites)?** → **Judgment call**. For Context 1–2, embed. For Context 3–4, weigh time-to-redraw against permission-request time.

5. **Is the figure likely under restrictive copyright (subscription journal, non-transformative use, may be recorded)?** → **Redraw or get permission.**

---

## When embedding is forced by quality

Some figures cannot be usefully redrawn — complex biological pathway diagrams, histology micrographs, structural biology renderings. For these:

- Accept that redrawing degrades the teaching value.
- Embed, attribute fully, and if the recording concern is live — either cut the slide before recording or replace with a redrawn simplified version that references the original (with a "see Fig N in FirstAuthor 2025 for detail" pointer).

---

## The "I'll just add this figure to every slide for consistency" trap

**Don't.** Some presenters add the journal's logo or a mini "cover" thumbnail to every slide. This is slop — it's decorative, it adds no information, and repeated use of a publisher's mark across many slides starts looking like endorsement. One attribution per figure, on that figure's slide, is enough.

For a deck running several figures from the same paper, the running footer (`FirstAuthor et al. · Journal 2025`) doubles as an attribution reminder without slide-by-slide repetition of the full citation.

---

## Rule summary for this skill

When the skill builds a deck from a paper's PDF and embeds the paper's figures:

- Default assumption: **Context 1–2** (lab meeting / departmental talk). Embed with standard attribution format.
- Always write the attribution caption beneath the figure at ≥18px equivalent.
- Always include the full citation on the final slide or in the chrome footer on every figure slide.
- Flag to the user in the end-of-run summary: "These 4 figures are embedded from the paper. If this talk will be publicly recorded or posted, consider redrawing Figures X and Y (the schematics) and obtaining RightsLink permission for Figure Z (the data plot). The micrograph in Figure W cannot be redrawn — request permission if needed."
- Default to **Context 3** behavior (stricter) only if the user mentions "conference talk", "recorded", "public", "keynote", "webinar" in the interview.
