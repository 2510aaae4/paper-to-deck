"""Quick check · is the openevidence-mcp cookies.json still valid?

Reads cookies.json from the MCP directory, posts /api/auth/me with those cookies,
reports authenticated status + earliest cookie expiry. No browser launch, no
Playwright dependency -- purely a requests.Session check.

Use this before starting an audit-oe workflow so you know whether you need to
re-run refresh_cookies.py first. Typical output:

  [OK]    authenticated as <email>
          earliest cookie expires: 2026-05-08 15:30 +0800 (15 days from now)

Or:

  [MISS]  cookies.json not found at <path>
          Run: py start/scripts/refresh_cookies.py --login

Or:

  [STALE] cookies are present but auth check failed (HTTP 401)
          Run: py start/scripts/refresh_cookies.py --login

Exit codes:
    0  authenticated (ready to call oe_ask via MCP)
    2  cookies.json missing
    3  cookies present but stale (OE rejected them)
    4  MCP directory missing entirely
    6  requests not installed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent
DEFAULT_MCP_DIR = PROJECT_ROOT / "_private" / "openevidence-mcp"

OE_AUTH_API = "https://www.openevidence.com/api/auth/me"


def load_cookies(cookies_path: Path) -> dict:
    """Return dict suitable for requests' cookies= parameter.
    Accepts storage-state format {cookies: [...]} or plain array [...]."""
    raw = json.loads(cookies_path.read_text(encoding="utf-8"))
    items = raw.get("cookies", raw) if isinstance(raw, dict) else raw
    return {c["name"]: c["value"] for c in items if "name" in c and "value" in c}


def earliest_expiry(cookies_path: Path):
    raw = json.loads(cookies_path.read_text(encoding="utf-8"))
    items = raw.get("cookies", raw) if isinstance(raw, dict) else raw
    expires = []
    for c in items:
        exp = c.get("expires") or c.get("expirationDate")
        if isinstance(exp, (int, float)) and exp > 0:
            expires.append(exp)
    if not expires:
        return None
    from datetime import datetime, timezone
    ts = min(expires)
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()


def main(mcp_dir: Path) -> int:
    if not mcp_dir.exists():
        print(f"[ABSENT] MCP not installed at {mcp_dir}")
        print("         This is fine if you do not use the OE citation-audit feature.")
        print("         To enable, see start/SKILL.md Step 0c.")
        return 4

    cookies_path = mcp_dir / "cookies.json"
    if not cookies_path.exists():
        print(f"[MISS]   cookies.json not found at {cookies_path}")
        print("         Run: py start/scripts/refresh_cookies.py --login")
        return 2

    try:
        import requests
    except ImportError:
        print("[ERR]   requests not installed. Run: py -m pip install --user requests")
        return 6

    cookies = load_cookies(cookies_path)
    try:
        r = requests.get(OE_AUTH_API, cookies=cookies, timeout=10)
    except requests.RequestException as e:
        safe = str(e).encode("ascii", "replace").decode("ascii")[:200]
        print(f"[ERR]   HTTP request failed: {safe}")
        return 3

    if r.status_code != 200:
        print(f"[STALE]  auth check returned HTTP {r.status_code}")
        print("         Run: py start/scripts/refresh_cookies.py --login")
        return 3

    try:
        body = r.json()
    except Exception:
        body = {}
    identity = body.get("email") or body.get("user", {}).get("email") or body.get("id") or "<unknown>"
    print(f"[OK]     authenticated as {identity}")

    expiry = earliest_expiry(cookies_path)
    if expiry:
        from datetime import datetime, timezone
        now = datetime.now(tz=timezone.utc).astimezone()
        days = (expiry - now).days
        print(f"         earliest cookie expires: {expiry.strftime('%Y-%m-%d %H:%M %z')} "
              f"({days} days from now)")
        if days <= 2:
            print("         [WARN] expiring soon -- consider running refresh_cookies.py --login")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mcp-path", type=Path, default=DEFAULT_MCP_DIR,
                    help=f"Path to openevidence-mcp install directory "
                         f"(default: {DEFAULT_MCP_DIR})")
    args = ap.parse_args()
    sys.exit(main(mcp_dir=args.mcp_path.resolve()))
