# CHANGELOG · `start`

## v0.2.0 — 2026-04-23 · Step 0 dependency screen

### Added
- `scripts/check_deps.py` — runs first thing in every session. Reports `pymupdf` / `pillow` (required) and `docling` / `requests` (optional) install status. Exit 0 when required deps present; exit 2 when required deps missing. Prints the specific `py -m pip install --user <name>` command per missing dep so the user can paste-and-run.
- `SKILL.md` Step 0 now sits before the paper question. The skill will not advance to Step 1 until `check_deps.py` exits 0.

### Changed
- Safety posture bullet re "install packages" now names the four tracked deps explicitly and flags that optional deps (docling, requests) are still user-consent gated — the skill reports, the user installs.

### Why this version exists
The first real v0.5.0 paper run (SRMA on PICC infection prevention, CID 2026) exposed that `docling` being absent silently disabled the entire V5 native-editable-table feature — `_parse_table_structure()` needs docling's HTML output, and without it never writes `tbl-NN.json`. The user has no visible signal until deck-build time when the native-table emit silently no-ops. The fix is to surface dependency status *before* the user commits to the workflow, so they can install up-front or accept the degraded feature set knowingly. `requests` was bundled into the same check because it's the only other v0.5.0 optional dep and the pattern is identical.

---

## v0.1.0 — 2026-04-22 · Initial release

### Added
- `SKILL.md` — onboarding gate for `paper-to-deck`. Three-step flow (ask → validate → confirm + hand off). Explicit scope limitation: no slide drafting, no interview questions, no content extraction beyond title guess.
- `scripts/validate_pdf.py` — four-check validator: file exists, magic bytes are `%PDF`, has text layer, page count in 2–60 range. Returns distinct exit codes (1–4) so the SKILL can route the user to the right fix for each failure mode.

### Companion dependency
- Hands off to `paper-to-deck >= 0.3.0` (the skill living at `../paper-to-deck/`). Answers gathered here (PDF path, venue context, deadline, language preference) are context the `paper-to-deck` interview in Step 2 should consume without re-asking.

### Lesson captured on first run
Testing `validate_pdf.py` on an NEJM paper immediately re-exposed the cp950 encoding bug (second sighting, now logged in `paper-to-deck/references/windows-setup.md` §7). The lesson: "emit only ASCII to stdout" applies to extracted *data* (titles, captions, publisher strings) as much as to literal markers. ASCII-only print statements aren't enough if you're interpolating unicode-containing data into them. Fix: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at script top + collapse unicode whitespace via `" ".join(s.split())` before printing extracted text.
