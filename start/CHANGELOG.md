# CHANGELOG · `start`

## v0.1.0 — 2026-04-22 · Initial release

### Added
- `SKILL.md` — onboarding gate for `paper-to-deck`. Three-step flow (ask → validate → confirm + hand off). Explicit scope limitation: no slide drafting, no interview questions, no content extraction beyond title guess.
- `scripts/validate_pdf.py` — four-check validator: file exists, magic bytes are `%PDF`, has text layer, page count in 2–60 range. Returns distinct exit codes (1–4) so the SKILL can route the user to the right fix for each failure mode.

### Companion dependency
- Hands off to `paper-to-deck >= 0.3.0` (the skill living at `../paper-to-deck/`). Answers gathered here (PDF path, venue context, deadline, language preference) are context the `paper-to-deck` interview in Step 2 should consume without re-asking.

### Lesson captured on first run
Testing `validate_pdf.py` on an NEJM paper immediately re-exposed the cp950 encoding bug (second sighting, now logged in `paper-to-deck/references/windows-setup.md` §7). The lesson: "emit only ASCII to stdout" applies to extracted *data* (titles, captions, publisher strings) as much as to literal markers. ASCII-only print statements aren't enough if you're interpolating unicode-containing data into them. Fix: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at script top + collapse unicode whitespace via `" ".join(s.split())` before printing extracted text.
