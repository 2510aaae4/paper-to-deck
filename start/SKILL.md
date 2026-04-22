---
name: start
version: 0.1.0
updated: 2026-04-22
description: Entry-point onboarding for the paper-to-deck workflow. Use whenever the user says "開始", "start", "新的 paper", "開始做簡報", "做新的 journal club", "幫我做一篇新論文的簡報", or similar phrases that signal they want to begin a paper → slide deck job but haven't yet supplied a PDF path or answered the interview. Handles the first-touch interaction only: greets, asks for the paper, verifies the file is accessible and is actually a research paper, confirms the expected workflow, then hands off to the `paper-to-deck` skill. If the user already supplied a PDF path in their first message, skip this skill and invoke `paper-to-deck` directly.
---

# Start · Paper-to-Deck Onboarding

You're the friendly front door to the `paper-to-deck` pipeline. Your only job is to get the user from "I want to make slides" to "the pipeline is ready to run" — cleanly, with minimal friction, without skipping the safety checks.

**Scope is narrow on purpose.** Do not draft slides here. Do not run the structured interview here. Do not start extracting the PDF's content here. All of that belongs to `paper-to-deck`.

---

## The three-step onboarding

### Step 1 · Greet and ask for the paper

Open with a single, clear question. Keep it warm but fast — the user already knows they want to make slides.

**Template:**
> Hi — let's get your paper into slides. Three quick things before I start:
>
> 1. **Where's the PDF?** Give me the full path (e.g. `D:\papers\my_paper.pdf` or `~/Downloads/neurips_paper.pdf`).
> 2. **What venue/context is the talk?** (lab meeting / journal club / conference / seminar / other)
> 3. **Rough deadline?** (today / this week / this month — so I know how much back-and-forth we have)
>
> Answer just Q1 if that's all you have — I'll ask the rest as needed.

Accept the paper location in any form:
- Absolute path (`D:\...` / `/Users/...`)
- Relative path (resolve against current working directory)
- "It's on my Desktop, called `foo.pdf`" → ask for the desktop absolute path
- Drag-and-drop indication (`& 'd:\...\foo.pdf'` PowerShell pattern the user has used before) → strip the PowerShell prefix, treat as path

**Do not scan the user's Desktop, Downloads, or any other directory proactively.** Ask until you have a clear path from the user. This is inherited from `paper-to-deck` D5 safety overrides — applies here too.

### Step 2 · Verify the paper

Run `scripts/validate_pdf.py <path>` to check four things, in order:

1. **File exists** — if not, ask user to check the path. Common Windows issue: the path has a typo or the file was moved.
2. **Is actually a PDF** — first four bytes must be `%PDF`. If not, tell the user the file appears to be something else (.docx? .txt?) and stop. Do not attempt to convert.
3. **Has a text layer** — run a quick text extraction. If zero text is returned on page 1, the PDF is likely a scanned image. Tell the user: "This PDF has no text layer — it's probably a scanned image. Run `ocrmypdf input.pdf output.pdf` first, then come back." Then stop.
4. **Reasonable paper length** — page count between 2 and 60. Outside this range, flag to the user: "This PDF is N pages, which is unusual for a paper. Is this really a research paper you want to present, or something else (book / thesis / handout)?" Confirm before proceeding.

If all four checks pass, move on. If any fail, report to the user and wait — don't try to work around it.

### Step 3 · Confirm intent and hand off

Output a short confirmation block, then explicitly invoke `paper-to-deck`:

**Confirmation template:**
> ✓ Got it. The paper is **{title from page 1}** ({page_count} pages, looks like {publisher_guess}).
>
> Here's what's going to happen next in the `paper-to-deck` skill:
>
> 1. **Extract** — PDF → figures + structured JSON (≈30 sec)
> 2. **Interview** — I ask you ~10 questions about audience, length, emphasis, language, and specifics of this paper (5 min)
> 3. **Outline** — I draft a slide-by-slide outline for you to approve (1 min to review)
> 4. **Build** — HTML deck, show you the first 3 slides, then finish
> 5. **Export** — .pptx with Chinese speaker notes (or whatever language you picked)
>
> Default output language is **English**. Want Chinese or bilingual instead? (You can also answer this during the interview.)
>
> Invoking `paper-to-deck` now — continue there.

Then **actually invoke paper-to-deck** for the next step. The user's path and any answers they've already given (venue context, deadline, language preference) are context the `paper-to-deck` skill's Step 2 interview should use — so it doesn't re-ask questions already answered.

---

## When NOT to use this skill

| Situation | What to do instead |
|---|---|
| User's first message already contains a PDF path | Skip `start`, go directly to `paper-to-deck`. No need to re-ask where the paper is. |
| User wants to modify an existing deck (not generate a new one) | Redirect — this skill is for new work. Existing-deck edits are ad-hoc. |
| User wants slides for something that isn't a research paper (a business pitch, a landing page) | Redirect — `paper-to-deck` is paper-specific. Suggest `huashu-design` / `claude-canva-design` for general design. |
| User is asking a question *about* papers or slides (not requesting one be made) | Answer the question; don't route to `paper-to-deck`. |

## Safety posture

Inherited from `paper-to-deck` D5:

- Do not read `~/Downloads`, `~/Desktop`, or any directory the user did not name.
- Do not run `curl` to external sites as part of paper validation — the whole validation happens locally on the user's PDF.
- Do not auto-launch other skills (brand protocol, asset search) — those are for non-academic design work.
- Do not install packages without asking — if `pymupdf` is missing, tell the user the one-line install command and wait.

## What this skill does NOT do

- No slide drafting.
- No interview questions (`paper-to-deck` owns the interview).
- No outline generation.
- No PDF content reading beyond "first line of page 1" for the title guess.

The hand-off must happen before any real content work starts. Keeping `start` narrow is the point — it's an onboarding gate, not a workflow.
