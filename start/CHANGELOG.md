# CHANGELOG · `start`

## v0.3.1 — 2026-04-24 · Env check restructure · OE becomes explicit opt-in

### Changed
- `SKILL.md` frontmatter: version → 0.3.1; `updated` → 2026-04-24; description rewritten to name the new responsibility (env screen: packages + OE cookie opt-in + `OE_AVAILABLE` hand-off flag).
- `SKILL.md` Step 0 relabelled **Step 0a** for consistency with the new Step 0b.
- `SKILL.md` Step 0b rewritten: was "auto-run check_oe_auth.py if the feature is enabled"; now **ask the user explicitly** whether they want the OE extension round available for this deck, then check cookies only on Yes. On No — record `OE_AVAILABLE=false` and move straight to Step 1 without mentioning OE again. This is the user-requested behaviour change.
- `SKILL.md` Step 0c reframed as "run only when user said Yes in 0b and auth check exited `4` (not installed)". Title changed from "citation audit" to "extension round" per the v0.6.0 reframing in paper-to-deck.
- `SKILL.md` Step 3 hand-off: now explicitly carries `OE_AVAILABLE` through to paper-to-deck alongside the PDF path and any interview-level answers already given. paper-to-deck Step 3.5 reads this flag instead of running its own auth check.
- Non-blocking rule made explicit: at any point in 0b, if the user can't or won't complete auth, record `false` and proceed. OE is a convenience, not a gate; the deck builds fine without it.

### Why this version exists
The user observed (2026-04-24) that env checks were scattered — `check_deps.py` at start, `check_oe_auth.py` only if a hidden feature flag tripped, cookie refresh as a separate manual step. The request was to bundle all environment screening at the start of the session and to make OE **explicitly opt-in** rather than auto-detected from filesystem presence. An implicit "if the folder exists, run the check" is too magical: new users don't know why their session is asking them about cookies, and returning users might want to skip OE for a particular deck even if the feature is installed.

Making OE opt-in also makes the skip path clean. Previously, `paper-to-deck` Step 3.5 had to do its own auth check and decide whether to offer the extension round. Now the decision is made upstream in `start`, carried forward via one flag, and `paper-to-deck` just reads it. Fewer decision points, less prompting.

### Known limitations
- `OE_AVAILABLE` is a session-local flag in the hand-off message, not a persisted file. If the conversation context compacts or is resumed later, the flag may be lost; `paper-to-deck` Step 3.5 has a belt-and-suspenders `oe_auth_status` re-check for safety. Persisting the flag to disk is possible but adds a file that'd need to be gitignored and cleaned up per deck — deferred until the flag loss actually happens.
- Step 0c auto-trigger (user said Yes in 0b, exit `4` from check_oe_auth.py) points the user at git clone + npm install + MCP registration — a meaningful chunk of first-time setup. Users who bail out mid-way will end up with `OE_AVAILABLE=false` and a half-cloned MCP dir. The skill must not loop on retry; if the user bails, respect `false` and move on.

---

## v0.3.0 — 2026-04-23 · OpenEvidence citation-audit integration · cookie flow in start

### Added
- `scripts/refresh_cookies.py` — Playwright-based auto-refresher for `_private/openevidence-mcp/cookies.json`. Uses a persistent user-data-dir (`playwright-profile/`, gitignored) so the user logs into OE once, then subsequent refreshes run headless in ~3 seconds. `--login` shows a visible Chromium window for first-time auth; `--force` re-logs even when session is valid; `--mcp-path` overrides the default install location.
- `scripts/check_oe_auth.py` — lightweight per-session check (no Playwright, no browser). Reads `cookies.json`, posts `/api/auth/me` via `requests`, reports `[OK]`/`[STALE]`/`[MISS]`/`[ABSENT]` + earliest-cookie-expiry-date + days-from-now warning if < 2 days.
- `scripts/check_deps.py` gained a new **External CLIs** section (OPT class): `node` ≥ 20, `npm`, `git`, `claude`. Reports version for each when present; printed install hint when missing. All OPT — absence only blocks the OE audit feature, not the paper-to-deck core pipeline.
- `SKILL.md` Step 0 split into 0 (python deps) + 0b (cookie per-session check) + 0c (one-time OE MCP install instructions). 0b runs only if the user enabled the audit feature; 0c is documentation for first-time setup.

### Changed
- MCP server install location moved from `C:\Users\user\tools\openevidence-mcp\` (scattered outside project) to `<project-root>/_private/openevidence-mcp/` (inside project but gitignored). Reason: this repo ships on GitHub; external tooling scattered outside project is hard to reproduce for other users. The `_private/` convention from CLAUDE.md already shields sensitive data, and `.gitignore` got three extra belt-and-suspenders patterns (`cookies.json`, `playwright-profile/`, `openevidence-mcp/`) for defense-in-depth.
- `.gitignore` · added `tande-2026-spinal-epidural-abscess/` (per the slug convention), `cookies.json`, `playwright-profile/`, `openevidence-mcp/`.

### Why this version exists
Two events drove this release. First, exploring the audit-oe-skill (htlin222) for citation verification revealed it requires an OpenEvidence MCP server — and OE has **no public API**, so the only path is an unofficial MCP that reuses cookies from a logged-in browser session. That cookie path is brittle (Chrome 127+ App-Bound Encryption blocks `browser_cookie3` without admin; cookies expire on OE's schedule) so a proper Playwright-based refresher is the user-experience difference between "re-export every 1-2 weeks using a browser extension" and "one script call, headless after first login".

Second, the user flagged that this repo will go public on GitHub. The initial MCP install at `C:\Users\user\tools\` was invisible to paper-to-deck users; the second version moves everything into the project with strict gitignore so the install is reproducible for other users while their personal session data stays private.

### Known limitations
- The `claude mcp add-json` command in the SKILL.md Step 0c template uses absolute paths, not `${PWD}`-style relatives. Reason: Claude Code's MCP registration stores the raw path; a relative path would bind to whatever directory Claude Code launched from. Users must edit the path once per machine.
- If Chrome 127+ ships changes that break the Playwright Chromium 1208 bundled with the user's playwright-python, the install command `py -m playwright install chromium` must be re-run to fetch a newer bundle. This isn't specific to this feature — it's a general Playwright lifecycle event.
- The persistent profile at `_private/openevidence-mcp/playwright-profile/` grows as Chromium accumulates cache/history. Not an operational problem at current scale, but future iterations may want a "clean profile" flag that wipes it (currently requires manual `rm -rf`).
- `check_oe_auth.py` depends on `requests`, which `check_deps.py` currently marks as OPT (only needed for interview Q17). If the user disables Q17 imagery and uninstalls requests, `check_oe_auth.py` will say `[ERR] requests not installed`. Not a blocker — install requests if you want the auth check.

---

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
