# Windows Setup & Gotchas

This reference collects Windows-specific friction points encountered when running `paper-to-deck` end-to-end. Read this first on any Windows machine, or before debugging a script that "works on my colleague's Mac".

---

## 1 · Python `print()` crashes with `UnicodeEncodeError: cp950`

**Symptom:**
```
UnicodeEncodeError: 'cp950' codec can't encode character '✓'
in position 0: illegal multibyte sequence
```

**Cause:** Windows Python in Traditional-Chinese locale uses **cp950 (Big5)** as the default stdout encoding. Any character outside Big5 — checkmarks (`✓`), arrows (`→`), bullet points (`•`), em-dashes when inside a console print — crashes the entire script. This is distinct from the file encoding; reading/writing UTF-8 files works fine. The crash is at the `print()` boundary.

**Fixes, in order of preference:**

1. **Use only ASCII in script `print()` output**: `[OK]`, `->`, `*`, `--`. This is the zero-setup option and the recommended default for scripts that ship as skill artifacts.

2. **Force UTF-8 stdout at script start**:
   ```python
   import sys
   sys.stdout.reconfigure(encoding="utf-8")
   ```
   Requires Python 3.7+. Works but breaks non-UTF-8-aware consumers of the script's stdout.

3. **Set environment variable before run** (affects all Python):
   ```
   set PYTHONIOENCODING=utf-8
   python your_script.py
   ```

4. **Write to a file, don't print**: `Path("log.txt").write_text(msg, encoding="utf-8")`. Zero risk.

**Rule for this skill**: all scripts in `scripts/` emit only ASCII to stdout. Unicode goes to files.

---

## 2 · Installing `pymupdf` / `pdfplumber` on Windows

**The common failures:**

- `pymupdf` sometimes fails to install without the Microsoft Visual C++ Build Tools. Error message points to `fitz` native compilation.
  - **Fix**: `pip install --upgrade pip`, then `pip install pymupdf` will usually pull a prebuilt wheel. If not: install VS Build Tools (with "Desktop development with C++" workload).
- `pdfplumber` pulls `pdfminer.six` which is pure-Python and should install cleanly. If it complains about `cryptography`, that's a real compile — use `pip install --only-binary=:all: cryptography` to force wheel.

**Known-good versions for this skill** (as of 2026-04):
- `pymupdf >= 1.24` (uses `page.get_pixmap(clip=rect, dpi=...)`)
- `python-pptx >= 1.0` (needed for correct 16:9 slide setup)
- `pillow >= 10.0`

---

## 3 · LibreOffice headless for PPTX → PNG verification

Used by `references/verification.md` to produce rasters from generated `.pptx` for automated visual inspection.

**Install**: `winget install TheDocumentFoundation.LibreOffice`

**Invocation (Git Bash / PowerShell)**:
```
soffice --headless --convert-to png --outdir out/ deck.pptx
```

**Known quirks on Windows**:
- `soffice` may not be on PATH. Common location: `C:\Program Files\LibreOffice\program\soffice.exe`. Either add to PATH or call the full path.
- If multiple Office products are installed, soffice may be aliased. `where soffice` / `Get-Command soffice` confirms which you're hitting.
- LibreOffice renders fonts using *its own* font cache. A font installed since LibreOffice was launched needs `soffice --terminate_after_init` to flush, or a full LibreOffice restart.

---

## 4 · Shell-script portability (`.sh` files)

If the skill ever ships `.sh` pipelines (audio mixing, video export from `huashu-design` components, etc.):

- **Git Bash** is the de-facto Unix shell on Windows. Install via Git for Windows.
- PowerShell's `$(npm root -g)` is **not** the same as Bash's — PowerShell parses `$(...)` differently. Wrap with `bash -c "..."` or use `%APPDATA%\npm\node_modules` directly.
- Path separators: Bash on Windows handles both `C:\Users\...` and `/c/Users/...`. Prefer forward slashes inside scripts; they work in both shells.
- `ffmpeg` install: `winget install Gyan.FFmpeg`. Needs PATH refresh after install (restart terminal).

**Rule for this skill**: if you're writing a build step, prefer Python or Node over `.sh`. They run identically on both OSes without a Bash wrapper.

---

## 5 · Opening an HTML preview from Python

**Cross-platform snippet** (avoid `subprocess.run(['open', ...])` which is macOS-only):

```python
import webbrowser, pathlib
url = pathlib.Path("deck.html").resolve().as_uri()
webbrowser.open(url)
```

This uses the OS default browser handler on Windows, macOS, and Linux.

---

## 6a · `huggingface_hub` WinError 1314 without Developer Mode

**Symptom** (first observed 2026-04-23, `docling 2.90.0` + `huggingface_hub 1.11.0`):
```
[WARN] docling unavailable or failed: [WinError 1314] 用戶端沒有這項特殊權限。:
  '..\\..\\blobs\\2c5b...' -> 'C:\\Users\\dr\\.cache\\huggingface\\hub\\
  models--docling-project--docling-layout-heron\\snapshots\\...\\README.md'
```

The warning printed just above it tells you the mechanism:
```
To support symlinks on Windows, you either need to activate Developer Mode
or to run Python as an administrator.
```

**Cause:** `huggingface_hub` stores downloaded models as blobs and uses symlinks in `snapshots/<revision>/` to point at the blobs. Symlink creation on Windows requires either (a) Developer Mode on or (b) admin privileges. Without either, the final step of the model download fails — *after* blobs have already downloaded, leaving a half-built cache that `docling` can't use.

**Fix (one-time, preferred):** enable **Developer Mode**:
1. Settings → Privacy & Security → For developers
2. Toggle "Developer Mode" to On
3. Confirm the warning dialog

No reboot, no admin password needed. Persistent across updates. Every `huggingface_hub` download afterwards creates symlinks cleanly.

**If the first docling run already aborted**: delete the partial cache before retrying. The half-built tree otherwise makes docling think the model is present:
```
rm -rf ~/.cache/huggingface/hub/models--docling-project--docling-layout-heron
```
Then re-run `extract_paper.py`; the model re-downloads (~400 MB).

**Why not run as admin every time**: it works, but elevated shells are a bad default (credentials risk, shell history in admin context, and the cache ends up owned by the admin profile rather than the user). Developer Mode is the correct fix.

**Why not set an env var**: `huggingface_hub` 1.11.0 has no env var to force copy-fallback when symlinks fail. Newer versions have automatic fallback, but 1.11 (bundled with `docling 2.90.0`) does not. If you're on a later version and the symptom disappears, mark this entry as historical.

---

## 6b · Docling `std::bad_alloc` on text-heavy later pages

**Symptom** (first observed 2026-04-23 on a CID SRMA, 14-page PDF):
```
Stage preprocess failed for run 1, pages [7]: std::bad_alloc
Stage preprocess failed for run 1, pages [8]: std::bad_alloc
...
Stage preprocess failed for run 1, pages [14]: std::bad_alloc
[INFO] docling found 2 pictures (post-filter), 1 tables
```

The layout model's preprocessor ran out of memory on pages 7–14 — the reference-list-heavy back half of the PDF. Tier 0 output was limited to pages 1–6; any figure/table on a failed page (Fig 3 on page 11 in the observed case) fell back to Tier 2 (caption-anchored crop). Pipeline still produced valid output; nothing was dropped.

**Why this happens:** `docling-ibm-models` uses a layout segmentation model whose memory grows with page complexity. Text-dense reference pages (small font, many columns of citations) can trip the allocator, especially on 8 GB / 16 GB machines running other apps.

**Mitigations, not yet wired into the skill:**
- Limit docling to the pages that actually have figures / tables (the caption index built by `_build_caption_index` already knows these). This trades a small scan cost for avoiding the heavy preprocessor on reference pages.
- Run docling with `PdfPipelineOptions.do_ocr = False` when the PDF has a text layer (we already know it does, per `full_text`). OCR adds memory pressure.
- Increase Windows page file / close other apps before running.

For now, the pipeline's graceful Tier 0 → Tier 2 fallback handles this well enough; add to this log when the workaround becomes worth the code complexity.

---

## 6 · Path handling in prompts and skills

When the user provides a Windows path in a prompt (e.g. `D:\papers\foo.pdf`), the backslashes survive intact through to Python — but any intermediate shell invocation will munge them. In this skill's scripts:

- Accept paths as `pathlib.Path` arguments, not raw strings.
- Always `.resolve()` before passing to external tools.
- When writing paths into generated files (e.g. the `deck.html`'s `<img src="figures/fig-01.png">`), use forward slashes. Browsers accept them on Windows; backslashes cause fragile quoting issues.

---

## 7 · Known version drift (living log)

This section is a lab-notebook-style log. Every time a tool version change causes a behavior shift in this skill's pipeline, add a row. Include: date observed, tool, versions, symptom, workaround. Keep newest at top.

| Date | Tool | Versions | Symptom | Workaround |
|---|---|---|---|---|
| 2026-04-23 | `docling-ibm-models` preprocessor | docling 2.90.0 | `std::bad_alloc` on text-dense reference-list pages; Tier 0 silently skips those pages, Tier 2 fallback picks up | See §6b. Skill's fallback chain handles it; no code change yet. |
| 2026-04-23 | `huggingface_hub` | 1.11.0 | `WinError 1314` creating symlinks in `~/.cache/huggingface/hub/.../snapshots/` because Windows blocks symlink creation without Developer Mode or admin | Enable Windows Developer Mode (Settings → Privacy & Security → For developers). See §6a. |
| 2026-04-22 | Python stdout on Windows Traditional-Chinese locale (second sighting) | cp950 default | `start/scripts/validate_pdf.py` printing a PDF title line containing em-space `U+2003` crashed despite ASCII-only `[OK]` markers, because the extracted *data* was not ASCII-safe | Added `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at script top AND collapsed unicode whitespace with `" ".join(s.split())`. The rule "emit only ASCII" applies to extracted data too — literal markers are not enough. |
| 2026-04-22 | Python stdout on Windows Traditional-Chinese locale | cp950 default | `print("✓ ...")` raises `UnicodeEncodeError` even though file I/O is UTF-8 | All scripts in `scripts/` emit ASCII only to stdout. See §1 above. |
| 2026-04-22 | `pymupdf` | 1.25.5 | `page.get_images()` returns empty list on Elsevier-family PDFs despite visible figures | Fall back to caption-anchored page crop — see `pdf-extraction.md` Tier 2. Behavior stems from the publisher's vector-compositing pipeline, not a pymupdf bug. |
| 2026-04-22 | `python-pptx` | 1.0.2 | OOXML `<a:rPr spc="...">` accepts any integer without validation; calling `spc = letter_spacing * 100` when `letter_spacing` was intended as em-scaled produced 22pt per-character tracking | Use multiplier of 10 instead. See `pptx-gotchas.md` §1. |
| placeholder | Windows Terminal Preview | older builds | emoji in `print()` mangled even after `PYTHONIOENCODING=utf-8` | ASCII only — already the skill's rule |

**How to use this log**: When writing a new script for this skill, check this table first. If your task involves one of the listed tools, you already know what not to step on. When a version drift bites you that's not listed here, add it — future-you or the next collaborator will thank you.
