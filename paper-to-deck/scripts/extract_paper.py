"""
extract_paper.py - Academic PDF to structured JSON + figure/table images.

Usage:
    python extract_paper.py <pdf-path> --out-dir <project-dir>

Dependencies:
    pip install pymupdf pillow

Produces in <out-dir>:
    paper.json            - structured metadata + artifact index
    figures/fig-NN.png    - each figure, one image per Figure N caption
    figures/fig-NN.txt    - sidecar caption text (UTF-8)
    tables/tbl-NN.png     - each table rendered as an image
    tables/tbl-NN.txt     - sidecar caption text (UTF-8)
    pages/page-NN.png     - host-page renders for any figure/table page
                            (so user can re-crop manually if crop is wrong)

Extraction strategy per artifact (documented in references/pdf-extraction.md):
    Tier 1: page.get_images() for embedded raster figures (rare in journal PDFs)
    Tier 2: caption-anchored page crop - find "Figure N:" / "Table N:" text
            line, crop the area above the caption
    Tier 2b: FACING-PAGE detection - if caption contains "(facing page)",
             the actual figure is on the OPPOSITE page (NEJM convention:
             caption on odd page, figure on preceding even page)
    Tier 3: full-page render (fallback when tiers 1+2 fail; user crops manually)

Windows cp950 safety: all stdout is ASCII. Unicode goes to files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Force UTF-8 stdout on Windows cp950 locales - belt and suspenders.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def extract(pdf_path: Path, out_dir: Path) -> dict:
    try:
        import fitz
    except ImportError:
        sys.exit("Missing dependency: pip install pymupdf")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "figures").mkdir(exist_ok=True)
    (out_dir / "tables").mkdir(exist_ok=True)
    (out_dir / "pages").mkdir(exist_ok=True)

    doc = fitz.open(pdf_path)
    full_text = "\n".join(page.get_text() for page in doc)

    if not full_text.strip():
        sys.exit("PDF appears to be image-only (no text layer). Run OCR first "
                 "(e.g. ocrmypdf) and retry.")

    # Save full text for downstream tools (outline generation, grep)
    (out_dir / "full_text.txt").write_text(
        "\n".join(f"\n\n===== PAGE {i+1} =====\n\n{p.get_text()}"
                  for i, p in enumerate(doc)),
        encoding="utf-8"
    )

    # Figure / table extraction: try docling (Tier 0) first; fall back to
    # our built-in Tier 1/2/2b/2c/3 cropping logic per-artifact for anything
    # docling misses. See references/external-extractors.md and
    # references/pdf-extraction.md.
    figures, tables = _extract_artifacts(doc, pdf_path, out_dir)

    paper = {
        "source_pdf": str(pdf_path),
        "page_count": doc.page_count,
        "title": _guess_title(doc),
        "authors": _guess_authors(full_text),
        "year": _guess_year(full_text),
        "venue": None,
        "abstract": _extract_abstract(full_text),
        "sections": _split_sections(full_text),
        "figures": figures,
        "tables": tables,
        "citations": _find_citations(full_text),
    }

    (out_dir / "paper.json").write_text(
        json.dumps(paper, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[OK] paper.json       -> {out_dir / 'paper.json'}")
    print(f"[OK] figures/         -> {len(paper['figures'])} image(s)")
    print(f"[OK] tables/          -> {len(paper['tables'])} image(s)")
    print(f"[OK] pages/           -> sidecars for all artifact host pages")
    print(f"[OK] full_text.txt    -> {len(full_text)} chars")
    print(f"[OK] sections         -> {len(paper['sections'])} detected")
    print(f"[OK] citations        -> {len(paper['citations'])} detected")
    for fig in paper["figures"]:
        print(f"     figure {fig['num']}: page {fig['host_page']}  [{fig['tier']}]")
    for tbl in paper["tables"]:
        print(f"     table  {tbl['num']}: page {tbl['host_page']}  [{tbl['tier']}]")
    return paper


# -------------------- figure / table extraction --------------------

# Tier 0: docling (optional). If unavailable or fails, fall through to our
# per-artifact Tier 1/2/2b/2c/3 cropping. See external-extractors.md for
# the full integration rationale.
try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    DOCLING_AVAILABLE = True
except Exception:
    DOCLING_AVAILABLE = False


def _extract_artifacts(doc, pdf_path: Path, out_dir: Path) -> tuple[list, list]:
    """
    Orchestrator: try docling first; fall back per-artifact to our built-in
    cropping for anything docling misses. Always enriches with caption text
    from our caption-anchored scan (docling's caption retrieval is unreliable
    on journal PDFs).
    """
    # Always scan paper for authoritative caption index (cheap, useful either way)
    fig_index = _build_caption_index(doc, "Figure")  # {num: (cap_page, host_page, caption)}
    tbl_index = _build_caption_index(doc, "Table")   # {num: (cap_page, host_page, caption)}

    # Try docling for tight-cropped images
    docling_artifacts = None
    if DOCLING_AVAILABLE:
        try:
            docling_artifacts = _try_docling(pdf_path, out_dir)
        except Exception as e:
            print(f"[WARN] docling unavailable or failed: {e}")
            print(f"       falling back to built-in extractor (Tier 1/2/2b/2c)")

    figures = _materialise_figures(doc, out_dir, fig_index, docling_artifacts)
    tables  = _materialise_tables (doc, out_dir, tbl_index, docling_artifacts)
    return figures, tables


def _try_docling(pdf_path: Path, out_dir: Path) -> dict | None:
    """
    Run docling once, return {"pictures": [...], "tables": [...]} where each
    entry has keys: page, image_path (PIL saved to tmp), html (tables only),
    width, height, area. Filters junk (< 200 px on either axis).
    Returns None if docling errored or yielded nothing useful.
    """
    print(f"[INFO] Trying docling (Tier 0)...")
    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = 2.0
    converter = DocumentConverter(format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
    })
    result = converter.convert(pdf_path)
    ddoc = result.document

    # Stage docling images under pages/_docling_cache/ so we can reuse them
    cache = out_dir / "pages" / "_docling_cache"
    cache.mkdir(parents=True, exist_ok=True)

    pictures = []
    for i, pic in enumerate(ddoc.pictures, 1):
        try:
            pil = pic.get_image(ddoc)
        except Exception:
            continue
        if pil is None:
            continue
        # Junk filter: logos / footer icons are tiny
        if pil.width < 200 or pil.height < 200:
            continue
        page = pic.prov[0].page_no if pic.prov else None
        if page is None:
            continue
        path = cache / f"docling-pic-{i:03d}.png"
        pil.save(path, optimize=True)
        pictures.append({
            "page": page,
            "image_path": path,
            "width": pil.width,
            "height": pil.height,
            "area": pil.width * pil.height,
        })

    tables = []
    for i, tbl in enumerate(ddoc.tables, 1):
        try:
            html = tbl.export_to_html(doc=ddoc)
        except Exception:
            html = ""
        page = tbl.prov[0].page_no if tbl.prov else None
        if page is None:
            continue
        path_png = cache / f"docling-tbl-{i:03d}.png"
        try:
            pil = tbl.get_image(ddoc)
            if pil is not None:
                pil.save(path_png, optimize=True)
                w, h = pil.size
            else:
                w, h = 0, 0
        except Exception:
            w, h = 0, 0
        tables.append({
            "page": page,
            "image_path": path_png if path_png.exists() else None,
            "html": html,
            "width": w,
            "height": h,
            "area": w * h,
        })

    print(f"[INFO] docling found {len(pictures)} pictures (post-filter), "
          f"{len(tables)} tables")
    return {"pictures": pictures, "tables": tables}


def _build_caption_index(doc, kind: str) -> dict[int, tuple[int, int, str]]:
    """
    Scan the whole PDF for 'Figure N' / 'Table N' captions.
    Returns {num: (caption_page, host_page, full_caption)}.

    For figures with '(facing page)' hint, host_page is resolved via
    drawings-density tiebreak against neighbour pages.
    """
    index: dict[int, tuple[int, int, str]] = {}
    patterns = (r"(?m)^\s*(?:Figure|Fig\.?)\s+(\d+)[:\.\s]" if kind == "Figure"
                else r"(?m)^\s*Table\s+(\d+)[:\.\s]")
    kind_pattern = r"(?:Figure|Fig\.?)" if kind == "Figure" else "Table"

    for page_num, page in enumerate(doc, 1):
        for m in re.finditer(patterns, page.get_text(), re.I):
            num = int(m.group(1))
            if num in index:
                continue
            y, _ = _find_caption_y(page, kind_pattern, num)
            if y is None:
                continue
            full_cap = _full_caption_from_page(page, num, kind)
            host_page = page_num

            # Facing-page resolution for figures
            if kind == "Figure" and _is_facing_page(full_cap) and page_num > 1:
                prev_density = _page_drawings_density(doc[page_num - 2])
                next_density = _page_drawings_density(doc[page_num]) if page_num < doc.page_count else 0
                host_page = page_num - 1 if prev_density >= next_density else page_num + 1

            index[num] = (page_num, host_page, full_cap)
    return index


def _materialise_figures(doc, out_dir: Path, fig_index: dict,
                         docling_artifacts: dict | None) -> list[dict]:
    """
    For each paper-declared figure, produce an output PNG + caption sidecar.
    Prefer docling's image if host_page matches; else fall back to our
    per-figure cropping tiers.
    """
    results = []
    docling_pics = list(docling_artifacts["pictures"]) if docling_artifacts else []

    for num in sorted(fig_index.keys()):
        cap_page, host_page, caption = fig_index[num]
        # Match docling picture by host_page (prefer the LARGEST candidate on that page)
        matched = [p for p in docling_pics if p["page"] == host_page]
        matched.sort(key=lambda p: -p["area"])
        out_png = out_dir / "figures" / f"fig-{num:02d}.png"

        if matched:
            src = matched[0]
            # Copy from docling cache to final path
            import shutil
            shutil.copyfile(src["image_path"], out_png)
            tier = f"Tier 0 (docling, {src['width']}x{src['height']})"
            w, h = src["width"], src["height"]
            # consume so we don't match twice
            docling_pics.remove(src)
        else:
            # Fall back per-figure to our built-in cropping
            tier, w, h = _fallback_extract_figure(doc, num, cap_page, host_page,
                                                   caption, out_png)

        (out_dir / "figures" / f"fig-{num:02d}.txt").write_text(caption, encoding="utf-8")
        _save_host_page(doc, host_page, out_dir)
        if host_page != cap_page:
            _save_host_page(doc, cap_page, out_dir)

        results.append({
            "num": num, "caption": caption[:500],
            "caption_page": cap_page, "host_page": host_page,
            "tier": tier, "image": f"figures/fig-{num:02d}.png",
            "image_width": w, "image_height": h,
        })
    return results


def _fallback_extract_figure(doc, num, cap_page, host_page, caption, out_png):
    """Per-figure fallback when docling didn't provide an image."""
    import fitz
    fig_page = doc[host_page - 1]
    is_facing = host_page != cap_page
    cap_y, _ = _find_caption_y(doc[cap_page - 1], r"(?:Figure|Fig\.?)", num)

    if is_facing or cap_y is None or cap_y <= 200:
        rect = fitz.Rect(20, 60, fig_page.rect.width - 20, fig_page.rect.height * 0.96)
        pix = fig_page.get_pixmap(clip=rect, dpi=220)
        tier = "Tier 2b (facing page)" if is_facing else "Tier 3 (full-page fallback)"
    else:
        rect = fitz.Rect(20, 90, fig_page.rect.width - 20, cap_y - 4)
        pix = fig_page.get_pixmap(clip=rect, dpi=220)
        tier = "Tier 2 (caption-anchored)"
    pix.save(str(out_png))
    return tier, pix.width, pix.height


def _materialise_tables(doc, out_dir: Path, tbl_index: dict,
                        docling_artifacts: dict | None) -> list[dict]:
    """For each paper-declared table, write PNG + caption + (if available) HTML."""
    results = []
    docling_tbls = list(docling_artifacts["tables"]) if docling_artifacts else []

    for num in sorted(tbl_index.keys()):
        cap_page, host_page, caption = tbl_index[num]
        matched = [t for t in docling_tbls if t["page"] == host_page]
        matched.sort(key=lambda t: -t["area"])
        out_png = out_dir / "tables" / f"tbl-{num:02d}.png"
        out_html = out_dir / "tables" / f"tbl-{num:02d}.html"
        rotation = 0

        # Even if docling's image failed, its HTML is still useful — save it
        # independently; always use our Tier 2/2c cropping for the PNG when
        # docling's image is missing (more reliable on landscape NEJM tables).
        if matched and matched[0]["image_path"] is not None:
            src = matched[0]
            import shutil
            shutil.copyfile(src["image_path"], out_png)
            w, h = src["width"], src["height"]
            tier = f"Tier 0 (docling, {w}x{h})"
            if src["html"]:
                out_html.write_text(src["html"], encoding="utf-8")
            docling_tbls.remove(src)
        else:
            # Save HTML if docling had it, even though image comes from fallback
            if matched and matched[0]["html"]:
                out_html.write_text(matched[0]["html"], encoding="utf-8")
                docling_tbls.remove(matched[0])
            # Fall back: use our Tier 2 / 2c logic
            tier, w, h, rotation = _fallback_extract_table(doc, num, cap_page, caption, out_png)

        (out_dir / "tables" / f"tbl-{num:02d}.txt").write_text(caption, encoding="utf-8")
        _save_host_page(doc, cap_page, out_dir)

        entry = {
            "num": num, "caption": caption[:500],
            "host_page": cap_page, "tier": tier,
            "rotation": rotation,
            "image": f"tables/tbl-{num:02d}.png",
            "image_width": w, "image_height": h,
        }
        if out_html.exists():
            entry["html"] = f"tables/tbl-{num:02d}.html"
        results.append(entry)
    return results


def _fallback_extract_table(doc, num, cap_page, caption, out_png):
    """Per-table fallback when docling didn't provide an image."""
    page = doc[cap_page - 1]
    cap_y, _ = _find_caption_y(page, "Table", num)
    if cap_y is None:
        cap_y = 60
    is_landscape, rotation = _detect_landscape_on_page(page, cap_y)
    if is_landscape:
        pix = page.get_pixmap(dpi=220)
        tmp = out_png.with_name(out_png.stem + "_tmp.png")
        pix.save(str(tmp))
        from PIL import Image
        img = Image.open(tmp).rotate(-rotation, expand=True, resample=Image.BICUBIC)
        img.save(out_png, optimize=True)
        tmp.unlink()
        return f"Tier 2c (landscape, rotated {rotation:+d} deg)", img.width, img.height, rotation
    import fitz
    rect = fitz.Rect(20, max(60, cap_y - 10), page.rect.width - 20, page.rect.height * 0.96)
    pix = page.get_pixmap(clip=rect, dpi=220)
    pix.save(str(out_png))
    return "Tier 2 (caption-anchored, below)", pix.width, pix.height, 0


def _find_caption_y(page, needle_prefix: str, number: int):
    """
    Locate the y-coordinate of a caption line starting with "Figure N" or
    "Table N" on this page. Returns (y, full_caption_text) or (None, None).
    """
    pattern = re.compile(rf"^\s*{needle_prefix}\s*{number}[:\.\s]", re.I)
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(s["text"] for s in line.get("spans", []))
            if pattern.search(text):
                # Grab the full caption (this line + following lines until blank)
                return line["bbox"][1], text.strip()
    return None, None


def _full_caption_from_page(page, num: int, kind: str) -> str:
    """
    Read the full caption paragraph for Figure/Table N on this page.
    Returns empty string if not found.
    """
    needle = rf"^\s*{kind}\s*{num}[:\.\s]"
    page_text = page.get_text()
    m = re.search(needle, page_text, re.M | re.I)
    if not m:
        return ""
    start = m.start()
    # Caption typically ends at first double-newline or paragraph break
    rest = page_text[start:]
    # Heuristic: stop at blank line or at start of next major block
    parts = re.split(r"\n\s*\n", rest, maxsplit=1)
    caption = re.sub(r"\s+", " ", parts[0].strip())
    return caption[:800]


def _is_facing_page(caption: str) -> bool:
    """Detect '(facing page)' hint used by NEJM etc."""
    return bool(re.search(r"\(facing\s+page\)", caption, re.I))


def _page_drawings_density(page) -> int:
    """Higher drawings count = more visual content."""
    try:
        return len(page.get_drawings())
    except Exception:
        return 0


def _save_host_page(doc, page_num: int, out_dir: Path) -> Path:
    """Render and save the full host page as a sidecar PNG."""
    path = out_dir / "pages" / f"page-{page_num:02d}.png"
    if path.exists():
        return path
    pix = doc[page_num - 1].get_pixmap(dpi=200)
    pix.save(str(path))
    return path


def _crop_above_caption(page, caption_y: float, dpi: int = 220):
    """Crop the page region from top margin to just above the caption."""
    import fitz
    rect = fitz.Rect(20, 90, page.rect.width - 20, caption_y - 4)
    return page.get_pixmap(clip=rect, dpi=dpi)


def _crop_full_page(page, dpi: int = 220):
    """Fallback: render the whole page (minus chrome margins)."""
    import fitz
    rect = fitz.Rect(20, 60, page.rect.width - 20, page.rect.height * 0.96)
    return page.get_pixmap(clip=rect, dpi=dpi)


def _detect_landscape_on_page(page, caption_y: float) -> tuple[bool, int]:
    """
    Detect whether a Table is rotated 90° (landscape on a portrait page).
    Two signals: text-direction vote (when PDF stores rotation honestly)
    and geometric signature (caption in bottom 45% + narrow body y-range,
    needed for NEJM-style layouts where `dir` vectors lie).
    Returns (is_landscape, rotation_degrees). Rotation convention:
    positive = content rotated CCW; caller rotates -rotation in PIL.
    """
    page_h = page.rect.height
    dirs = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span["bbox"][1] < caption_y + 4:
                    continue
                if span["bbox"][1] > page_h * 0.93:
                    continue
                if len(span.get("text", "").strip()) >= 2:
                    dirs.append(span.get("dir", (1.0, 0.0)))
    if dirs:
        total = len(dirs)
        horiz = sum(1 for d in dirs if abs(d[0]) > 0.7)
        ccw   = sum(1 for d in dirs if d[1] < -0.7)
        cw    = sum(1 for d in dirs if d[1] >  0.7)
        if (total - horiz) / total >= 0.55:
            return True, (90 if ccw >= cw else -90)
    if caption_y / page_h > 0.55:
        body_ys = []
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    y = span["bbox"][1]
                    if y < caption_y + 10 or y > page_h * 0.93:
                        continue
                    if len(span.get("text", "").strip()) >= 2:
                        body_ys.append(y)
        if body_ys and (max(body_ys) - min(body_ys)) < 200:
            return True, 90
    return False, 0


# -------------------- metadata parsing --------------------

def _guess_title(doc) -> str:
    """Largest-font non-header text on page 1 is usually the title."""
    page = doc[0]
    blocks = page.get_text("dict")["blocks"]
    candidates = []
    for b in blocks:
        if b.get("type") != 0:
            continue
        for line in b.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if 5 < len(text) < 250:
                    candidates.append((span["size"], text, span["bbox"][1]))
    if not candidates:
        return ""
    candidates.sort(key=lambda x: (-x[0], x[2]))
    top_size = candidates[0][0]
    title_parts = [t for sz, t, _ in candidates if abs(sz - top_size) < 0.5][:3]
    return " ".join(title_parts).strip()


def _guess_authors(text: str) -> list[str]:
    head = text[:800]
    m = re.search(r"(?:\n|^)([A-Z][a-zA-Z\.\-]+(?:\s+[A-Z][a-zA-Z\.\-]+)+"
                  r"(?:[,\s]+(?:and\s+)?[A-Z][a-zA-Z\.\-]+(?:\s+[A-Z][a-zA-Z\.\-]+)+)+)",
                  head)
    if not m:
        return []
    parts = re.split(r",\s*|\s+and\s+", m.group(1))
    return [p.strip() for p in parts if p.strip()]


def _guess_year(text: str) -> int | None:
    for m in re.finditer(r"\b(19|20)\d{2}\b", text[:2000]):
        y = int(m.group())
        if 1990 <= y <= 2030:
            return y
    return None


def _extract_abstract(text: str) -> str:
    m = re.search(r"(?is)\bAbstract\b\s*[:\-]?\s*\n?(.+?)"
                  r"(?=\n\s*(?:1\.?\s+Introduction|Introduction|Keywords|1\s+Introduction)\b)",
                  text)
    if m:
        return re.sub(r"\s+", " ", m.group(1).strip())[:3000]
    return ""


def _split_sections(text: str) -> list[dict]:
    pattern = re.compile(r"(?m)^\s*(\d+(?:\.\d+)?)\s+([A-Z][A-Za-z \-&]{2,60})\s*$")
    matches = list(pattern.finditer(text))
    sections = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = re.sub(r"\s+", " ", text[start:end].strip())
        sections.append({
            "number": m.group(1),
            "title": m.group(2).strip(),
            "body_preview": body[:500],
            "body_length": len(body),
        })
    return sections


def _find_citations(text: str) -> list[str]:
    pattern = re.compile(r"\b([A-Z][a-z]+(?:\s+(?:et\s+al\.|and\s+[A-Z][a-z]+))?)[\s,]+\(?(\d{4})\)?")
    seen = set()
    out = []
    for m in pattern.finditer(text):
        key = f"{m.group(1)} {m.group(2)}"
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out[:200]


def main():
    ap = argparse.ArgumentParser(description="Extract paper content from PDF.")
    ap.add_argument("pdf_path", type=Path)
    ap.add_argument("--out-dir", type=Path, default=Path("."))
    args = ap.parse_args()

    if not args.pdf_path.exists():
        sys.exit(f"PDF not found: {args.pdf_path}")

    extract(args.pdf_path, args.out_dir)


if __name__ == "__main__":
    main()
