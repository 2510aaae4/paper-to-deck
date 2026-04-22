# Academic Slide Anti-Slop

Academic slide slop has its own flavor, distinct from SaaS/marketing slop. Read this before writing any slide content. Each entry lists the pattern, why it fails, and the fix.

## The 10 worst academic slide slop patterns

### 1 · Wall of bullets
**Pattern**: 6+ bullet points on one slide, each a full sentence, filling the slide top to bottom.

**Why it fails**: The audience reads ahead of the speaker; nobody follows the voice; bullets 3–6 get no attention.

**Fix**: One slide, one message. If you have 6 things to say, that's 6 slides — or, more likely, 2 slides with 3 shorter bullets each, or a diagram.

---

### 2 · Figure crammed 4-per-slide
**Pattern**: Paper's Figure 3 had four subplots; presenter dumps all four on one slide at 25% size each.

**Why it fails**: Nobody in the back row can read axis labels at 8px. The information density that works in a printed paper does not work in a talk.

**Fix**: Pick the subplot that carries the message. If all four matter, that's 2–4 slides, one subplot each. If nothing can be cut, crop axes to remove redundancy.

---

### 3 · Citation vomit
**Pattern**: "Many prior works have addressed this [1][2][3][4][5][6][7][8]." Numbers scattered mid-sentence, no author names.

**Why it fails**: Citation numbers are meaningless on slides — nobody has the references page in front of them. They add visual noise without information.

**Fix**: Use author-year inline for the 1–2 papers that actually matter: "Smith 2023 showed X; Chen 2024 extended to Y." For broader surveys, say "~20 papers since 2020" verbally and show a count, not a list.

---

### 4 · Generic "Conclusion" slide restating abstract
**Pattern**: Final slide titled "Conclusion" with 3 bullets that literally paraphrase the abstract.

**Why it fails**: The audience already heard the content; restating it verbatim wastes the closing moment.

**Fix**: Takeaway (pattern P8) should be editorial — one sentence they'll remember tomorrow. Echo the hook if possible. "We showed X" is fine; "We showed X, which means Y for field Z" is better.

---

### 5 · Overselling limitations
**Pattern**: Limitations slide with 6 bullets, hedging heavily ("though our method only works on English text, and only with GPUs, and only for inputs shorter than..."). Sounds like a cover letter.

**Why it fails**: Academic honesty is a signal of confidence — overdoing it inverts the signal.

**Fix**: 2–3 genuine limitations. Stated simply. No apologizing.

---

### 6 · Title slide with only authors and affiliations
**Pattern**: 5 minutes of setup, slide 1 shows paper title + 6 author names + 3 lab logos + venue + date. Nothing else.

**Why it fails**: Burns the opening 10 seconds on metadata nobody asked for. The hook (P1) belongs here.

**Fix**: If bureaucratic required, put a tiny author/affiliation footer on slide 1 and use the rest of the slide for the hook. Or: put the metadata on a separate "thanks" slide at the end.

---

### 7 · Equations as images from the PDF
**Pattern**: Screenshot of equation from the paper, pasted at low resolution, often with surrounding paper text still visible in the margins.

**Why it fails**: Looks unprofessional, aliases badly when projected, signals "I didn't retype this."

**Fix**: Re-type in the deck's math renderer, or crop tightly and upsample. For PPTX outputs without LaTeX support, rasterize equations at 300 DPI before embedding.

---

### 8 · Results table with 15 rows and 8 columns
**Pattern**: Entire paper Table 2 pasted at 10px font.

**Why it fails**: Unreadable at projection distance. The audience gets the signal "there is data" but no specific data.

**Fix**: Bar chart of the one column that matters. Or the top 3 rows only. Or two separate slides for two result categories.

---

### 9 · Generic stock imagery as filler
**Pattern**: A slide about NLP decorated with a stock photo of a brain with glowing circuits. A slide about biology with a generic DNA helix. A slide about climate with a polar bear.

**Why it fails**: Decorative stock images add no information and signal AI-generated content. The audience tunes out.

**Fix**: Either a real figure from the paper or no image. Text with good typography beats bad decoration.

---

### 10 · "Figure N · Topic" as the slide's main title
**Pattern**: A slide that shows one of the paper's figures titles it `Figure 3 · The New Antibiotic Arsenal`, with the insight relegated to a subtitle or side-panel caption.

**Why it fails**: The audience doesn't have the paper's figure numbering as context. "Figure 3" reads as a data-artifact label, not an argument. It trains the audience to treat the slide as a reference lookup instead of a point in your argument.

**Fix**: The slide title is the **insight**, not the artifact. The topic stays as an eyebrow if needed. The figure number belongs in the caption attribution beneath the image, small — where anyone who wants to cross-reference can find it.

```
BAD                                 GOOD
─────────────────────────────────   ─────────────────────────────────
eyebrow: Figure 3 · New drugs       eyebrow: The new antibiotic arsenal
title:   Grouped by mechanism...    title:   Grouped by mechanism, not
                                             by approval year
                                    caption: ...from Fig 3, FirstAuthor 2025
```

Apply this to every figure slide. Resist "Figure N" appearing anywhere above the image — it pulls attention away from the argument.

---

### 11 · Bullets as information transfer
**Pattern**: Body text on a slide reaches 100+ words. Two-column layouts especially enable this — each column becomes its own paragraph block, and the slide ends up denser than the paper's abstract.

**Why it fails**: Bullets are **orientation cues**, not a delivery medium. The audience reads ahead of you, then tunes out. Everything load-bearing has to come from your voice, which means the slide isn't helping — it's competing.

**Fix**: Rule of thumb — **≤ 40 words of body text per slide**. If a slide exceeds this, one of these is happening:
- It wants to be two slides (split it)
- The detail belongs in speaker notes (move it)
- You haven't decided what the one main point is (decide)

Layouts that invite density (two-column paragraphs, three-column cards with prose) need especially tight discipline. In those layouts, prefer:
- Single-line drug/term + one-word role ("ceftolozane-tazobactam · workhorse")
- 2–3 short bullets instead of paragraphs
- A short phrase with one bolded highlight rather than a full sentence

If the rich context matters for the talk, it matters in the voice — so it goes in speaker notes, not on the slide.

---

### 12 · "Thank you / Questions?" slide
**Pattern**: Final slide with only "Thank you!" and/or "Questions?" in a large font.

**Why it fails**: Wasted real estate during Q&A — this slide stays on screen for 5+ minutes while people ask questions. Make it useful.

**Fix**: Leave the takeaway (P8) slide on screen during Q&A. Or repeat the hook slide. Or show contact + paper/code URL in readable size.

---

## Slop detectors (run these before finalizing)

Before declaring the deck done, scan every slide and check:

| Check | Pass criterion |
|---|---|
| Main message | Can you state it in one sentence? If no, the slide has no point. |
| Readability from the back | Smallest text ≥ 24px. Smallest figure label ≥ 18px. |
| Citation format | No bare `[N]` numbers. Author-year or nothing. |
| Color | One accent color only. Not a rainbow. Grayscale for everything else. |
| Decoration | Zero emoji, zero stock icons, zero gradient backgrounds. |
| Figure origin | Every figure is from the paper, or a clearly-labeled placeholder. |
| Bullet count | No slide has >5 bullets. Prefer ≤3. |
| **Word count** | **Body text ≤ 40 words per slide. Titles ≤ 12 words. If a slide exceeds, split or move detail to notes.** |
| **Title is an argument** | **Every slide title is a statement or question, not a topic label. "Figure 3" / "Methods" / "Results" are labels, not titles.** |
| Transition | Speaker has a clean sentence connecting this slide to the next. |

If any check fails, fix it before moving to PPTX export.

## One-thousand-nos principle

For every "yes, add this" impulse, there should be ~1000 "no" impulses. Restraint is the scarce skill — not ideas. A slide deck is good because of what it excludes.
