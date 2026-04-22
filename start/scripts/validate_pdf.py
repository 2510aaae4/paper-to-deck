"""
validate_pdf.py — Four-check validation for a candidate paper PDF.

Usage:
    python validate_pdf.py <pdf-path>

Exit codes:
    0 — all checks passed; PDF is ready for paper-to-deck
    1 — file doesn't exist
    2 — file exists but isn't a PDF
    3 — PDF has no text layer (probably scanned)
    4 — page count outside 2-60 range (probably not a research paper)

Output is ASCII-only to stdout (Windows cp950 safe — see
paper-to-deck/references/windows-setup.md).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Force UTF-8 stdout even on Windows cp950 consoles. Belt-and-suspenders:
# reconfigure if possible; fall back to errors="replace" for characters that
# still can't be encoded. See paper-to-deck/references/windows-setup.md §1.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

EXIT_OK = 0
EXIT_MISSING = 1
EXIT_NOT_PDF = 2
EXIT_NO_TEXT = 3
EXIT_ODD_LENGTH = 4


def report(status: str, msg: str) -> None:
    """Print status in a consistent ASCII-only format."""
    print(f"[{status}] {msg}")


def first_nonempty_line(text: str, limit: int = 200) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s:
            # Collapse any unicode whitespace/separators (em-space U+2003 et al.)
            # to regular spaces so downstream print/encode is predictable.
            s = " ".join(s.split())
            return s[:limit]
    return ""


def guess_publisher(text_head: str, filename: str) -> str:
    """Best-effort publisher fingerprint from first-page text or filename."""
    head = text_head.lower()
    name = filename.lower()
    if "arxiv:" in head or "arxiv.org" in head:
        return "arXiv preprint"
    if "1-s2.0-" in name or "sciencedirect" in head:
        return "Elsevier (Lancet/Cell/similar)"
    if "nejm.org" in head or "n engl j med" in head:
        return "NEJM"
    if "nature.com" in head or "doi.org/10.1038" in head:
        return "Nature / Springer"
    if "jamanetwork" in head or "jama." in head:
        return "JAMA"
    if "ieee" in head:
        return "IEEE"
    if "acm reference format" in head or "doi.org/10.1145" in head:
        return "ACM"
    if "creative commons" in head or "plos" in head:
        return "Open-access (PLOS/BMC/similar)"
    return "unknown publisher"


def validate(pdf_path: Path) -> int:
    # Check 1 — file exists
    if not pdf_path.exists():
        report("FAIL", f"File not found: {pdf_path}")
        report("HINT", "Check the path. On Windows, copy-paste the full path from File Explorer's address bar.")
        return EXIT_MISSING

    if not pdf_path.is_file():
        report("FAIL", f"Path is not a file: {pdf_path}")
        return EXIT_MISSING

    # Check 2 — is actually a PDF (magic bytes)
    try:
        with pdf_path.open("rb") as f:
            magic = f.read(4)
    except OSError as e:
        report("FAIL", f"Cannot read file: {e}")
        return EXIT_MISSING

    if magic != b"%PDF":
        report("FAIL", f"File doesn't look like a PDF (first 4 bytes: {magic!r}).")
        report("HINT", "If this is a .docx or .txt, convert it first (Save As PDF in Word/Preview).")
        return EXIT_NOT_PDF

    # Open with pymupdf for deeper checks
    try:
        import fitz
    except ImportError:
        report("FAIL", "pymupdf not installed. Run: pip install pymupdf")
        return EXIT_NOT_PDF

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        report("FAIL", f"Cannot open as PDF (may be encrypted or corrupt): {e}")
        return EXIT_NOT_PDF

    page_count = doc.page_count
    first_page_text = doc[0].get_text() if page_count > 0 else ""

    # Check 3 — has a text layer
    if not first_page_text.strip():
        report("FAIL", "PDF has no text layer on page 1 (probably scanned).")
        report("HINT", "Run OCR first: ocrmypdf input.pdf output.pdf")
        doc.close()
        return EXIT_NO_TEXT

    # Check 4 — reasonable paper length
    if page_count < 2:
        report("WARN", f"Only {page_count} page — very short for a paper.")
        doc.close()
        return EXIT_ODD_LENGTH
    if page_count > 60:
        report("WARN", f"{page_count} pages — unusually long for a paper.")
        report("HINT", "If this is a book, thesis, or handout, paper-to-deck is not the right tool.")
        doc.close()
        return EXIT_ODD_LENGTH

    # All good — print a friendly summary
    title_guess = first_nonempty_line(first_page_text)
    publisher = guess_publisher(first_page_text[:2000], pdf_path.name)
    report("OK", f"Valid research paper PDF.")
    print()
    print(f"  Path:       {pdf_path.resolve()}")
    print(f"  Pages:      {page_count}")
    print(f"  Publisher:  {publisher}")
    print(f"  Title hint: {title_guess}")
    print()
    print("Ready for paper-to-deck. Next step: the structured interview.")
    doc.close()
    return EXIT_OK


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a paper PDF for paper-to-deck.")
    ap.add_argument("pdf_path", type=Path)
    args = ap.parse_args()
    return validate(args.pdf_path)


if __name__ == "__main__":
    sys.exit(main())
