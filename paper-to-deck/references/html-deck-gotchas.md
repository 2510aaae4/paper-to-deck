# HTML Deck Gotchas

Technical pitfalls encountered when generating `deck.html` (Step 4). These are the HTML/CSS analogue of `pptx-gotchas.md`: each entry is a real bug that shipped or nearly shipped, with no console error and no automated signal. Read this before writing or modifying the deck HTML.

---

## 1 · CSS specificity · display rules on un-qualified modifier classes silently override state

**Symptom**: User opens the deck, presses `→`, and reports that "slides 2 and 3 look identical to slide 1" — or sees the cover title overlapping the content of every slide. No console error. Keyboard navigation JS is firing; slide index updates; `.active` class toggles correctly. But visually, the first slide never disappears.

**Cause**: State-dependent display rules (`.slide.active { display: block }`) and layout-modifier rules (`.cover { display: flex }`) have the **same specificity** (one class each). When the modifier is declared later in the stylesheet, it wins the cascade — forever. So the cover keeps its `display: flex` even when the JS removes its `.active` class, while the next slide correctly becomes `.active` and also displays. Two slides visible at once, cover content wins the z-order.

**Why this slips through every gate**:
- No console warning. No JS error. Lighthouse/axe don't flag it.
- The deck builder's own Chrome MCP screenshot looks like "a slide" — because cover content is showing.
- The bug only manifests when the user navigates AWAY from slide 1. Slide 1 itself looks fine.

**Correct**: Any rule that sets `display:` on a modifier class must be qualified with the state class so it only fires when that state is active:

```css
/* WRONG — overrides .slide { display:none } unconditionally */
.cover { display: flex; padding: 120px; }

/* CORRECT — display only applies when cover is the active slide */
.slide.cover { padding: 120px; }
.slide.cover.active { display: flex; flex-direction: column; }
```

Equivalently: never put `display:` on an un-qualified modifier when there's a state class that also controls display. Keep layout props (padding, flex-direction, background) on the modifier; keep display on the state-qualified selector.

**How to detect before the user sees it**:
- Open the deck, immediately press `→`. Confirm slide 1 disappears. This is a 3-second manual check that catches the bug every time.
- Automated: render slides 1 and 2 to PNG (e.g., Playwright) and assert their pixel diff exceeds a threshold. Identical first-pixel-row on a slide-2 render is the visible signature.
- Mental cascade walk: for the cover slide specifically, trace what `display:` value wins. If both `.slide { display:none }` and `.cover { display:flex }` are at class-specificity, the later-declared one is final — regardless of `.active` state.

**Reading this paper outside a high-volume center**: if a user reports "all slides look the same," check CSS first. JS navigation failure is the second suspect, not the first — state classes work; cascade bugs don't announce themselves.

---

## 2 · UI verification is the user's job — do not self-verify via Chrome MCP

**Symptom**: Skill runner spends time spinning up local HTTP servers + Chrome MCP sessions to "preview the first 3 slides" before handing the file to the user. The screenshots may even look fine. But the bug (§1 above) remains invisible to the runner because Chrome MCP sees the same broken layout the user will — and the runner has no reference for "what slide 2 is supposed to look like" to notice the collision.

**Cause**: The skill runner is not the judge of UI correctness. Different fonts, OS rendering, zoom levels, and color calibration make Chrome-MCP-in-a-VM's rendering non-authoritative. Worse, self-verification delays the handoff without actually catching the class of bug (CSS cascade, font fallback, pixel-level alignment) that visual QA is supposed to catch.

**Correct**: After writing `deck.html`, write a one-line message to the user with:
- the file path
- what specifically to check (e.g., "open, press → to confirm slide 1 hides; spot-check cover + one figure slide + one matrix slide")
- an instruction to tell the runner which slide is wrong if any

Then **stop**. Wait for the user's feedback before continuing to Step 5 (PPTX). Do not start a local server + Chrome session to "preview" — that burns time and obscures who is responsible for visual QA.

**Exception**: when debugging a specific layout bug the user has already reported and described, Chrome MCP + local server is a legitimate focused debug tool. But it is never the default gate.

**Why this matters operationally**: the ORCHESTRA deck session (2026-04-23) hit this directly — the runner tried to screenshot slides 2 and 3 via Chrome MCP, saw plausible-looking content (which was actually cover bleed-through from gotcha §1), and was ready to move on. The user had to open the HTML independently, see slides 2 and 3 looking like cover, and ask "why do these three pages look the same?" to surface the bug. Time was lost on the back-and-forth. Had the runner handed the file off directly — "open deck.html, press → twice, confirm the slides change" — the user would have caught the CSS cascade bug in 5 seconds.

---

## General rule · The first keyboard arrow is the cheapest QA

The single most valuable manual check on any HTML deck, from the user's side:

> **Open the file. Press `→` once. Confirm slide 1 fully disappears.**

If slide 1 content is still visible, there is a CSS cascade bug — usually §1 above. Every other keyboard / nav / JS issue pales in comparison to a stale slide 1, because cover content is typographically dominant (large h1) and will obscure whatever is on slide 2.

Document this in the hand-off message every time.
