# Equations on Slides

Equation fidelity is the silent failure mode of paper-to-deck workflows. The HTML deck renders MathJax cleanly in a browser; the PPTX export strips it; the user walks into the talk with equations that look like plain `\frac{d}{dt}` strings. This reference documents the decision tree and the three practical rendering paths.

Before anything else: **ask the user whether equations matter for this talk.** Many review articles and clinical papers can be presented without any equation on screen — the equation's role is in the speaker's verbal explanation, not the slide. If this is the case, skip equation rendering entirely. Less is more.

---

## When equations belong on slides

| Paper type | Equations on slides? |
|---|---|
| Clinical review (MDR infections, treatment guidelines) | **No** — usually zero math slides |
| Epidemiology / biostatistics paper | **Sometimes** — for key statistical models (Cox proportional hazards, multilevel models), one slide of equation + interpretation |
| Machine learning / theory paper | **Yes** — often the method slide *is* the equation |
| Physics / chemistry / engineering | **Yes** — core equations for the result usually needed |
| Math-adjacent CS (algorithms) | **Maybe** — pseudocode often serves better than formal notation |

If the user is unsure, default to **omit from slides, cover in speaker notes**. Adding an equation where the audience can't follow it degrades the talk.

---

## The three rendering paths

Given that an equation *does* belong on a slide, these are the three options, ranked by output quality and effort.

### Path 1 · Raster from PDF (fastest, lowest fidelity)

Extract the equation as an image directly from the paper's PDF, embed in the slide.

```python
import fitz
# For equation on page 5, roughly centered at y=340, ~30px tall
clip = fitz.Rect(90, 330, 500, 370)
pix = doc[4].get_pixmap(clip=clip, dpi=300)
pix.save("eq-01.png")
```

**Pros**: Perfect visual fidelity to the paper. Fast.
**Cons**: Raster scales badly on projection. Often has adjacent text from the PDF leaking into the crop. Not editable in PowerPoint. May have copyright implications (see `figure-attribution.md`).

**Use when**: Equation is complex typography (stacked fractions, tensor notation) AND audience needs to see the paper's exact rendering AND the talk is Context 1–2 (internal).

### Path 2 · Retype in LaTeX, render via `matplotlib`

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 2))
ax.axis("off")
ax.text(0.5, 0.5,
        r"$\hat{y} = \mathrm{argmax}_{y} \; P(y \mid x; \theta)$",
        ha="center", va="center", fontsize=42, usetex=False)
plt.savefig("eq-01.png", dpi=300, bbox_inches="tight",
            transparent=True, pad_inches=0.1)
```

**Pros**: Clean typography, can match slide's font-size scheme, transparent background blends with slide. No copyright concerns — you retyped the math from first principles.
**Cons**: matplotlib's MathText supports a subset of LaTeX, not the full TeX ecosystem. Complex cases (aligned equations, custom operators, mathbb) may not render. Requires local `python` + `matplotlib` + optionally TeX if `usetex=True`.

**Matplotlib MathText limitations to know:**
- No `\begin{align}` environments — use `\\` line breaks with `ha="center"` instead.
- `\mathbb{R}` needs `\mathbb` support which is off by default. Enable `rcParams["mathtext.fallback"] = "cm"` or use Unicode (`ℝ`).
- Custom macros from paper preambles are unavailable — rewrite them in their expanded form.

**Use when**: Single equations of moderate complexity, you want editable-looking output, the talk is going public (recorded).

### Path 3 · LaTeX Beamer output (nuclear option, best fidelity)

Abandon the HTML → PPTX pipeline for math-heavy papers and build the deck directly in LaTeX Beamer → PDF.

**When to recommend this to the user:**
- ≥5 equations in the deck.
- Equations use `\begin{align}`, chemical notation (mhchem), quantum mechanics notation (braket), category theory commutative diagrams, or any niche LaTeX package.
- Audience is a theoretical physics / pure math / theoretical CS crowd that will actually parse the equation on screen.

**Trade-off being explicit about**: Beamer loses the design polish we've built into the HTML deck — no `deck_stage.js` micro-interactions, no modern typography scheme, default Beamer themes look dated. The user is trading visual polish for mathematical fidelity.

If the user chooses this path, the skill's role shifts: still run the interview and produce the outline, then hand off the outline to the existing `claude-scientific-writer:venue-templates` or `claude-scientific-writer:latex-posters` skill for rendering. Don't try to handle full Beamer layout in `paper-to-deck` itself — it's out of scope.

---

## The MathJax → SVG → embed path (don't)

There's a tempting middle ground: render MathJax in a headless browser, capture the SVG, embed the SVG in PowerPoint. **Don't use this route.**

- MathJax SVG output is not round-trip editable in PowerPoint (the text is outlined as paths).
- The SVG files are large and blow up the PPTX size.
- PowerPoint sometimes renders embedded SVG math with anti-aliasing artifacts that look worse than the raster alternative.

Skip it. Use matplotlib (path 2) instead — same typographic quality, saner pipeline.

---

## Equation numbering on slides

Do not carry over the paper's equation numbers (`(3.14)`) onto slides unless you're referring back to them multiple times. A single equation on a slide doesn't need a number; two equations can use `(1)` and `(2)` inline. Never use the paper's `(3.14.a)` deep numbering — it confuses the audience.

Similarly, don't renumber equations to match slide numbers. Equations on slides are standalone; the paper's numbering system is for the paper.

---

## In-slide layout rules

- **Equation should occupy 60–80% of slide width, centered horizontally.** Too small = unreadable at back of room. Too large = no room for interpretation text.
- **Title above + interpretation below**: "What the equation says in one sentence" belongs beneath the equation at 24–28pt, not as a running comment on each symbol.
- **Do not explain notation inline on the slide.** Symbol meanings go in speaker notes. If the audience doesn't know the notation, adding `$y_{ij}$ = outcome for subject i on trial j` next to the equation turns the slide into a reference card — slop.
- **One equation per slide, maximum two.** If the derivation has six steps, the slide shows start and end (or the key inequality); the intermediate steps are in speaker voice.

---

## When to flag equation issues to the user

During the interview (`interview.md`), if `paper.json` indicates the paper has >3 equations in the abstract or methods section, add a paper-specific question:

> This paper uses several equations in its methods. Three approaches:
> a) Include key equations on slides, retyped (adds build time)
> b) No equations on slides — cover in verbal explanation only
> c) This paper needs LaTeX Beamer output, not PPTX (switch pipeline)

Default for clinical/review papers: (b). Default for theory papers: (a). Never silently pick (c) — switching pipelines changes the deliverable format and should be a conscious choice.

---

## The brute-force fallback

If an equation refuses to render in any path above (obscure notation, custom macros, the user provides a paper that uses TikZ for diagrams that happen to contain equations), the fallback is unsentimental:

1. Screenshot the equation at high resolution from the PDF.
2. Place as an image on the slide with attribution in the caption.
3. Note in the summary that this equation is not editable — the user must re-export from PDF if the paper revises.

This is what everyone does when LaTeX rendering fails at 9pm the night before the talk. Just do it, move on.
