"""
search_public_imagery.py - Fetch public-domain contextual imagery from a
small whitelist of sources (Wikimedia Commons / NIH Open-i / CDC PHIL /
WHO), filtered by Creative Commons licence.

Workflow (invoked after interview Q17):

    python search_public_imagery.py \
        --candidates imagery_candidates.json \
        --approved c01,c03,c05 \
        --out-dir public_imagery \
        --mode strict

Produces one `<id>.png` + `<id>.attribution.json` per approved candidate
that yields a licence-acceptable hit. Candidates marked `manual_only` are
always skipped here; the agent leaves them as placeholders in the deck.

Dependencies:
    pip install requests pillow

No extra network domains beyond the allowlist are contacted. If you see a
NotInAllowlistError raised, either fix the call-site or edit
`references/public-imagery.md` + add the new source here (and document the
driver incident in CHANGELOG.md).

Windows cp950 safety: all stdout is ASCII. Data (caption, author) goes to
JSON files as UTF-8.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import quote

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ---------- allowlist ----------

ALLOWED_HOSTS = {
    "commons.wikimedia.org",
    "upload.wikimedia.org",  # Wikimedia serves image binaries here
    "openi.nlm.nih.gov",
    "phil.cdc.gov",
    "www.who.int",
}

# Licence tokens that pass strict mode
STRICT_LICENCES = {
    "cc0", "pd", "publicdomain", "public domain",
    "cc-by", "cc by", "ccby",
    "cc-by-sa", "cc by-sa", "ccbysa",
    "us-gov", "usgov", "u.s. government work",
}

# Additionally allowed in loose mode
LOOSE_EXTRA = {
    "cc-by-nc", "cc by-nc", "ccbync",
}


class NotInAllowlistError(RuntimeError):
    pass


@dataclass
class SearchHit:
    source: str
    source_url: str
    image_url: str
    licence: str
    author: str
    title: str


# ---------- dispatcher ----------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", type=Path, required=True,
                    help="Path to imagery_candidates.json")
    ap.add_argument("--approved", type=str, default="",
                    help="Comma-separated candidate IDs to fetch")
    ap.add_argument("--out-dir", type=Path, default=Path("public_imagery"))
    ap.add_argument("--mode", choices=("strict", "loose"), default="strict")
    ap.add_argument("--dry-run", action="store_true",
                    help="Search but don't download")
    args = ap.parse_args()

    approved = {s.strip() for s in args.approved.split(",") if s.strip()}
    if not approved:
        print("[INFO] no candidates approved; nothing to do.")
        return 0

    data = json.loads(args.candidates.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("[ERR] candidates file is not a list")
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)

    total = hits = skipped = 0
    for cand in data:
        cid = cand.get("id")
        if cid not in approved:
            continue
        total += 1
        if cand.get("manual_only"):
            print(f"[SKIP] {cid}: manual_only (pop-culture / copyrighted) -- leaving placeholder")
            skipped += 1
            continue
        result = _search_one(cand, args.mode, args.out_dir, dry_run=args.dry_run)
        if result is None:
            print(f"[SKIP] {cid}: no CC-licensed match")
            skipped += 1
        else:
            print(f"[OK]   {cid}: {result['licence']} from {result['source']}")
            hits += 1

    print(f"[DONE] approved={total}  fetched={hits}  skipped={skipped}")
    return 0


def _search_one(cand: dict, mode: str, out_dir: Path, dry_run: bool = False) -> dict | None:
    """Dispatch to the suggested source; fall back through allowlist."""
    sources_to_try = [cand.get("source_hint", "wikimedia-commons")]
    for fallback in ("wikimedia-commons", "nih-open-i", "cdc-phil", "who"):
        if fallback not in sources_to_try:
            sources_to_try.append(fallback)

    for source in sources_to_try:
        try:
            hit = _search(source, cand["suggested_query"])
        except NotInAllowlistError as e:
            print(f"[ERR] allowlist violation: {e}")
            return None
        except Exception as e:
            print(f"[WARN] {source} search failed for {cand['id']}: {e}")
            continue
        if hit is None:
            continue
        if not _licence_passes(hit.licence, mode):
            print(f"[INFO] {cand['id']}: {source} hit has licence '{hit.licence}' -- rejected by {mode}")
            continue
        # Licence OK: download + save attribution
        if dry_run:
            return _attribution_dict(hit, cand)
        img_path = out_dir / f"{cand['id']}.png"
        try:
            _download(hit.image_url, img_path)
        except Exception as e:
            print(f"[WARN] download failed for {cand['id']}: {e}")
            continue
        attr_path = out_dir / f"{cand['id']}.attribution.json"
        attr = _attribution_dict(hit, cand)
        attr_path.write_text(json.dumps(attr, indent=2, ensure_ascii=False),
                             encoding="utf-8")
        return attr
    return None


def _attribution_dict(hit: SearchHit, cand: dict) -> dict:
    from datetime import datetime, timezone
    return {
        "candidate_id": cand["id"],
        "slide_anchor": cand.get("slide_anchor", ""),
        "source": hit.source,
        "source_url": hit.source_url,
        "licence": hit.licence,
        "author": hit.author,
        "title": hit.title,
        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rationale": cand.get("rationale", ""),
    }


# ---------- licence filter ----------

def _licence_passes(licence_raw: str, mode: str) -> bool:
    """
    Normalise + check against allowlist.

    Strategy: tokenise on non-alphanumeric, then classify the token set.
    This avoids substring false positives like 'CC BY-NC' matching 'CC BY'.
    """
    if not licence_raw:
        return False
    # Split on any non-word run; collapse case
    tokens = [t for t in re.split(r"[^a-z0-9]+", licence_raw.lower()) if t]
    tset = set(tokens)

    # Always reject ND + "all rights reserved" + copyrighted
    if "nd" in tset or "noderivatives" in tset or "noderivs" in tset:
        return False
    if "copyrighted" in tset or "proprietary" in tset:
        return False
    if "all" in tset and "rights" in tset and "reserved" in tset:
        return False

    # Public domain / US-gov shortcuts
    if "cc0" in tset or "pdm" in tset:
        return True
    if "public" in tset and "domain" in tset:
        return True
    if "us" in tset and ("gov" in tset or "government" in tset):
        return True
    if tset.issuperset({"u", "s", "government"}) or \
       tset.issuperset({"usgov"}):
        return True

    # CC family: must start with "cc" and "by"
    if "cc" in tset and "by" in tset:
        is_nc = "nc" in tset
        # strict rejects NC; loose accepts NC
        if is_nc and mode != "loose":
            return False
        # Accept CC BY / CC BY-SA (and CC BY-NC in loose mode)
        return True

    return False


# ---------- source-specific searches ----------

def _require_allowlisted(url: str) -> None:
    import urllib.parse as urlparse
    host = urlparse.urlparse(url).hostname or ""
    if host not in ALLOWED_HOSTS:
        raise NotInAllowlistError(host)


def _search(source: str, query: str) -> SearchHit | None:
    if source == "wikimedia-commons":
        return _search_wikimedia(query)
    if source == "nih-open-i":
        return _search_openi(query)
    if source == "cdc-phil":
        return _search_cdc_phil(query)
    if source == "who":
        return _search_who(query)
    print(f"[WARN] unknown source '{source}', skipping")
    return None


def _search_wikimedia(query: str) -> SearchHit | None:
    """
    Wikimedia Commons MediaWiki API.
    Returns the first image result with a parseable licence.
    """
    import requests
    api = "https://commons.wikimedia.org/w/api.php"
    _require_allowlisted(api)
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap|drawing",
        "gsrnamespace": "6",  # File: namespace
        "gsrlimit": 5,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iilimit": 1,
    }
    r = requests.get(api, params=params, timeout=20,
                     headers={"User-Agent": "paper-to-deck/0.5 (research; contact via project repo)"})
    r.raise_for_status()
    pages = (r.json().get("query") or {}).get("pages", {})
    for page_id, page in pages.items():
        info_list = page.get("imageinfo") or []
        if not info_list:
            continue
        info = info_list[0]
        extmeta = info.get("extmetadata", {}) or {}
        licence = (extmeta.get("LicenseShortName") or {}).get("value") or \
                  (extmeta.get("License") or {}).get("value") or ""
        image_url = info.get("url", "")
        if not image_url:
            continue
        _require_allowlisted(image_url)
        title = page.get("title", "").replace("File:", "")
        author = (extmeta.get("Artist") or {}).get("value") or ""
        # Strip HTML from author field (Wikimedia returns rich HTML)
        author = re.sub(r"<[^>]+>", "", author).strip()
        source_url = info.get("descriptionurl", "")
        return SearchHit(
            source="wikimedia-commons",
            source_url=source_url,
            image_url=image_url,
            licence=licence,
            author=author or "Unknown",
            title=title,
        )
    return None


def _search_openi(query: str) -> SearchHit | None:
    """NIH Open-i REST API."""
    import requests
    api = "https://openi.nlm.nih.gov/api/search"
    _require_allowlisted(api)
    params = {"query": query, "it": "x,g,c,m,mc,p,ph,u", "m": "1", "n": "5"}
    r = requests.get(api, params=params, timeout=20)
    r.raise_for_status()
    results = r.json().get("list", [])
    for rec in results:
        image_url = rec.get("imgLarge") or rec.get("imgMedium") or ""
        if not image_url.startswith("http"):
            image_url = "https://openi.nlm.nih.gov" + image_url
        _require_allowlisted(image_url)
        licence = rec.get("license") or rec.get("image_license") or ""
        return SearchHit(
            source="nih-open-i",
            source_url=rec.get("detailed_query_url", ""),
            image_url=image_url,
            licence=licence,
            author=rec.get("authors", "") or rec.get("author", ""),
            title=rec.get("title", "") or rec.get("image_caption", ""),
        )
    return None


def _search_cdc_phil(query: str) -> SearchHit | None:
    """
    CDC Public Health Image Library doesn't publish a JSON API; search is
    via HTML query. Images are US-federal public domain. This is a
    lightweight scrape of the approved search endpoint -- not a broad
    crawl. If CDC restructures the site and breaks this, skip and let the
    user surface images manually.
    """
    import requests
    from html.parser import HTMLParser
    url = f"https://phil.cdc.gov/Search.aspx?SearchCriteria={quote(query)}"
    _require_allowlisted(url)
    try:
        r = requests.get(url, timeout=20,
                         headers={"User-Agent": "paper-to-deck/0.5"})
        r.raise_for_status()
    except Exception:
        return None

    class FirstThumbParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.found = None
            self.first_title = None

        def handle_starttag(self, tag, attrs):
            if self.found:
                return
            a = dict(attrs)
            if tag == "img":
                src = a.get("src", "")
                if "thumbs" in src.lower() or "images" in src.lower():
                    self.found = src
                    self.first_title = a.get("alt") or a.get("title") or ""

    parser = FirstThumbParser()
    parser.feed(r.text)
    if not parser.found:
        return None
    img = parser.found
    if img.startswith("/"):
        img = "https://phil.cdc.gov" + img
    _require_allowlisted(img)
    return SearchHit(
        source="cdc-phil",
        source_url=url,
        image_url=img,
        licence="U.S. Government Work",
        author="CDC Public Health Image Library",
        title=parser.first_title or query,
    )


def _search_who(query: str) -> SearchHit | None:
    """
    WHO image search is not a structured API; per-page licence varies.
    Conservative default: return None so that WHO imagery only enters the
    deck when the user pastes it manually with verified licence. Future
    iterations can add a curated list of WHO open-resource pages.
    """
    return None


# ---------- download ----------

def _download(url: str, dest: Path) -> None:
    import requests
    _require_allowlisted(url)
    r = requests.get(url, timeout=30, stream=True,
                     headers={"User-Agent": "paper-to-deck/0.5"})
    r.raise_for_status()
    with dest.open("wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)


if __name__ == "__main__":
    sys.exit(main())
