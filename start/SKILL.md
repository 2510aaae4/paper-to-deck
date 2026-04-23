---
name: start
version: 0.3.0
updated: 2026-04-24
description: Entry-point onboarding for the paper-to-deck workflow. Use whenever the user says "開始", "start", "新的 paper", "開始做簡報", "做新的 journal club", "幫我做一篇新論文的簡報", or similar phrases that signal they want to begin a paper → slide deck job but haven't yet supplied a PDF path or answered the interview. Handles the first-touch interaction: greets, screens environment (required packages + optional OpenEvidence cookie), asks for the paper, verifies the file is accessible and is actually a research paper, confirms the expected workflow, then hands off to the `paper-to-deck` skill with an `OE_AVAILABLE` flag. If the user already supplied a PDF path in their first message and prior env checks already passed this session, skip this skill and invoke `paper-to-deck` directly.
---

# Start · Paper-to-Deck Onboarding

You're the friendly front door to the `paper-to-deck` pipeline. Your only job is to get the user from "I want to make slides" to "the pipeline is ready to run" — cleanly, with minimal friction, without skipping the safety checks.

**Scope is narrow on purpose.** Do not draft slides here. Do not run the structured interview here. Do not start extracting the PDF's content here. All of that belongs to `paper-to-deck`.

---

## The four-step onboarding

### Step 0a · Screen required packages (runs once per session, blocking)

Before asking the user anything, run `scripts/check_deps.py`. This takes well under a second and catches missing dependencies before the user commits to answering the interview.

The script reports two classes:

**Python packages** (paper-to-deck pipeline core):
- **Required**: `pymupdf`, `pillow` — pipeline stops without these.
- **Optional**: `docling` (Tier 0 extractor + V5 native editable tables), `requests` (interview Q17 public-imagery fetch).

**External CLIs** (optional, only for the OE extension round · see Step 0b/0c):
- `node` ≥ 20, `npm`, `git`, `claude` — needed only if the user wants the Step 3.5 OE extension round. Paper-to-deck itself works without them.

Exit-code contract:
- `0` → all required present (optional status printed); continue to Step 0b
- `2` → at least one required dep missing; surface the install command and **stop**. Do not proceed until `check_deps.py` exits 0.

Do not auto-install. If a dep is missing, print the install command and ask the user to run it. Rationale: v0.5.0+ opens narrow external paths (public-imagery fetch, OE MCP server); silently pulling new dependencies into the user's environment without asking contradicts the safety posture below.

### Step 0b · OE readiness (opt-in, non-blocking)

The OE extension round (paper-to-deck Step 3.5) is optional — the deck builds fine without it. Before checking cookies, **ask the user explicitly**:

**Template:**
> Want the OE-backed extension round available for this deck? I'd add 3–4 EBM slides at the end answering questions this paper raises but doesn't fully address, verified via OpenEvidence. If you'd rather keep the deck tight to just the paper's own content, say skip.
>
>   a) Yes — check / refresh OE cookie now
>   b) No — skip OE for this session

If the user picks **(b) No** — record `OE_AVAILABLE=false` for the hand-off and move straight to Step 1. Do not run the cookie check; do not mention OE again this session unless the user brings it up.

If the user picks **(a) Yes** — run `scripts/check_oe_auth.py`. It's a lightweight HTTP check (no browser, no Playwright import) that posts `/api/auth/me` with the existing `cookies.json`.

| Exit code | Meaning | Action |
|---|---|---|
| `0` | Authenticated | Record `OE_AVAILABLE=true`; continue to Step 1 |
| `2` | `cookies.json` missing | Tell user: `py start/scripts/refresh_cookies.py --login` — wait for completion, then re-check |
| `3` | Cookies present but stale | Same as above; re-login will refresh them |
| `4` | OE MCP directory doesn't exist | Feature not installed — offer Step 0c one-time setup; if the user declines, record `OE_AVAILABLE=false` |

**Non-blocking rule:** at any point in Step 0b, if the user changes their mind, can't finish auth in a reasonable time, or hits a setup issue they don't want to resolve right now — **record `OE_AVAILABLE=false` and proceed**. The deck still builds. Do not loop on OE readiness; it's a convenience feature, not a gate.

### Step 0c · One-time setup of the OE extension round (optional)

The OE integration requires three one-time steps. Run this only when the user has chosen (a) Yes in Step 0b and `check_oe_auth.py` returned exit code `4` (feature not installed).

**1. Clone the MCP server** into `_private/` (gitignored):
```
git clone https://github.com/htlin222/openevidence-mcp.git _private/openevidence-mcp
cd _private/openevidence-mcp
npm install
npm run build
```

**2. Initialize cookies via Playwright** (the first time only):
```
py start/scripts/refresh_cookies.py --login
```
A Chromium window opens (Playwright's own, not the user's Chrome). User logs into openevidence.com manually, presses Enter in the terminal, script saves `_private/openevidence-mcp/cookies.json`. Subsequent refreshes run headless (~3 sec) without the `--login` flag.

**3. Register the MCP with Claude Code**:
```
claude mcp add-json openevidence '{
  "command": "node",
  "args": ["<ABS-PATH-TO>/_private/openevidence-mcp/dist/server.js"],
  "env": {
    "OE_MCP_COOKIES_PATH": "<ABS-PATH-TO>/_private/openevidence-mcp/cookies.json"
  }
}'
```
Replace `<ABS-PATH-TO>` with the absolute project-root path (Windows: `D:\\user\\...\\paper-to-deck-main`; POSIX: `/home/.../paper-to-deck-main`). After registering, restart Claude Code so tool discovery picks up `oe_ask` / `oe_auth_status` / `oe_history_list` / `oe_article_get`.

**Why _private/**: both `cookies.json` and `playwright-profile/` contain the user's OE session. They are private per-user data and must not ship publicly. CLAUDE.md's `_private/` convention already gitignores this path; `.gitignore` additionally excludes `cookies.json`, `playwright-profile/`, and `openevidence-mcp/` as belt-and-suspenders even if `_private/` is ever relaxed.

**Cookie lifetime**: OE session cookies typically last 1-4 weeks depending on OE's settings and whether the user logs out elsewhere. When `check_oe_auth.py` reports `[STALE]`, re-run `refresh_cookies.py --login`. The Playwright persistent profile means re-login is usually a no-op (the profile remembers the last login); only truly expired sessions need manual credential entry.

**Session-level flag**: After Step 0b concludes (however it concludes — success, decline, or setup bail-out), you hold either `OE_AVAILABLE=true` or `OE_AVAILABLE=false`. This flag is passed through to `paper-to-deck` in the Step 3 hand-off message. `paper-to-deck`'s Step 3.5 reads this flag: `true` means the extension round is offered to the user; `false` means Step 3.5 is skipped silently (no "want me to add extension slides?" prompt — the user already answered upstream).

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

Then **actually invoke paper-to-deck** for the next step. Hand-off carries forward:
- PDF path (validated)
- Any answers already given (venue, deadline, language preference) — so paper-to-deck's Step 2 interview doesn't re-ask
- **`OE_AVAILABLE` flag** from Step 0b — paper-to-deck's Step 3.5 uses this to decide whether to offer the extension round at all

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
- Do not install packages without asking. `scripts/check_deps.py` will *report* missing packages with install commands; the user runs the install. This applies to every dependency — required (pymupdf, pillow) and optional (docling, requests) alike.

## What this skill does NOT do

- No slide drafting.
- No interview questions (`paper-to-deck` owns the interview).
- No outline generation.
- No PDF content reading beyond "first line of page 1" for the title guess.

The hand-off must happen before any real content work starts. Keeping `start` narrow is the point — it's an onboarding gate, not a workflow.
