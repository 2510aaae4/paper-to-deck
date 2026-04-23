"""Refresh cookies.json for openevidence-mcp using Playwright with a persistent profile.

Design rationale:
  - Chrome 127+ uses App-Bound Encryption on Windows -> browser_cookie3 needs admin.
  - Playwright ships its own Chromium (independent of the user's everyday Chrome)
    -> no DPAPI dance, no UAC prompt, no admin shell.
  - A persistent user-data-dir means the user logs in ONCE; subsequent refreshes
    run headless in ~3 seconds.

Project layout (this script is `start/scripts/refresh_cookies.py`):
  <project-root>/
  +- start/
  |   +- scripts/
  |       +- refresh_cookies.py        (this file)
  |       +- check_oe_auth.py
  +- _private/                          <- gitignored
      +- openevidence-mcp/
          +- dist/server.js
          +- cookies.json              <- OUTPUT (gitignored)
          +- playwright-profile/       <- persistent profile (gitignored)

Usage:
  py start/scripts/refresh_cookies.py --login                       # default channel (bundled Chromium)
  py start/scripts/refresh_cookies.py --login --channel chrome      # use installed Chrome (avoids Google OAuth block)
  py start/scripts/refresh_cookies.py --login --channel msedge      # use installed Edge (same idea)
  py start/scripts/refresh_cookies.py                               # headless refresh, ~3 sec
  py start/scripts/refresh_cookies.py --force                       # re-login even if session still valid
  py start/scripts/refresh_cookies.py --mcp-path <dir>              # override MCP location

Note on --channel:
  Google blocks Google-OAuth sign-in from bundled Chromium ("security risk"
  banner). Using --channel chrome (or msedge) drives the user's installed Chrome
  binary, which Google detects more leniently. If the OE account uses
  email/password (not Google sign-in), the default channel usually works.

Exit codes:
    0  cookies.json written successfully
    2  not authenticated and not running with --login
    3  no openevidence.com cookies after login (login may have failed silently)
    4  stdin closed (cannot wait for user Enter in interactive mode)
    5  still not authenticated after interactive login attempt
    6  playwright not installed or MCP path missing
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

# ---------------------------------------------------------------------------
# Path resolution - everything lives inside project root
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent             # start/scripts/
PROJECT_ROOT = HERE.parent.parent                   # project root
DEFAULT_MCP_DIR = PROJECT_ROOT / "_private" / "openevidence-mcp"

OE_HOME = "https://www.openevidence.com/"
OE_AUTH_API = "https://www.openevidence.com/api/auth/me"


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def is_authenticated(ctx) -> bool:
    try:
        response = ctx.request.get(OE_AUTH_API, timeout=10000)
        if response.status != 200:
            return False
        try:
            body = response.json()
        except Exception:
            return False
        if not body:
            return False
        return (body.get("user") is not None) or ("email" in body) or ("id" in body)
    except Exception:
        return False


def extract_and_save(ctx, cookies_path: Path) -> int:
    state = ctx.storage_state()
    oe_cookies = [c for c in state["cookies"] if "openevidence.com" in c["domain"]]
    if not oe_cookies:
        print("[ERR] No openevidence.com cookies in context. Login may have failed.")
        return 3
    # storage-state format (openevidence-mcp accepts object-with-cookies-array)
    out = {"cookies": oe_cookies}
    cookies_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK]  Wrote {cookies_path.name} with {len(oe_cookies)} cookie(s)")
    # Report earliest expiry so user can estimate re-login cadence
    expires = [c.get("expires") for c in oe_cookies if c.get("expires") and c.get("expires") > 0]
    if expires:
        from datetime import datetime, timezone
        soonest = min(expires)
        dt = datetime.fromtimestamp(soonest, tz=timezone.utc).astimezone()
        print(f"      Earliest cookie expires: {dt.strftime('%Y-%m-%d %H:%M %z')}")
    return 0


def main(mcp_dir: Path, interactive: bool, force: bool, channel: str | None) -> int:
    if not mcp_dir.exists():
        print(f"[ERR] MCP directory not found: {mcp_dir}")
        print(f"      Install openevidence-mcp first:")
        print(f"        git clone https://github.com/htlin222/openevidence-mcp.git {mcp_dir}")
        print(f"        cd {mcp_dir} && npm install && npm run build")
        return 6

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print("[ERR] playwright not installed. Run:")
        print("        py -m pip install --user playwright")
        print("        py -m playwright install chromium")
        return 6

    # Channel-specific profile dir: bundled Chromium stores data in a format
    # Chrome doesn't like and vice-versa. Keeping profiles separate avoids corruption.
    profile_name = "playwright-profile" if not channel else f"playwright-profile-{channel}"
    profile_dir = mcp_dir / profile_name
    cookies_path = mcp_dir / "cookies.json"
    profile_dir.mkdir(parents=True, exist_ok=True)

    launch_kwargs = {
        "user_data_dir": str(profile_dir),
        "headless": not interactive,
        "viewport": {"width": 1200, "height": 850},
    }
    if channel:
        launch_kwargs["channel"] = channel

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(**launch_kwargs)
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            try:
                page.goto(OE_HOME, timeout=20000)
                page.wait_for_load_state("networkidle", timeout=10000)
            except PWTimeout:
                print("[WARN] OE page load timed out. Continuing with current state.")

            authed = is_authenticated(ctx)
            if authed and not force:
                print("[OK]  Already authenticated from persistent profile.")
                return extract_and_save(ctx, cookies_path)

            if not interactive:
                print("[MISS] Not authenticated, and running non-interactive.")
                print("       Re-run with --login to open a browser and log in manually.")
                return 2

            if authed and force:
                print("[INFO] --force: logging in again even though auth is valid.")
            else:
                print("[INFO] Not authenticated. A Chromium window has opened.")
            print()
            print("      1. Log in to OpenEvidence in the browser window")
            print("      2. Return here and press Enter when done")
            print()
            try:
                input("      Press Enter after logging in... ")
            except EOFError:
                print("[ERR]  stdin closed; cannot wait for login confirmation.")
                return 4

            try:
                page.goto(OE_HOME, timeout=20000)
                page.wait_for_load_state("networkidle", timeout=10000)
            except PWTimeout:
                pass  # still check auth below

            if not is_authenticated(ctx):
                print("[ERR]  Still not authenticated. Check login in the browser and retry.")
                return 5

            print("[OK]  Login confirmed.")
            return extract_and_save(ctx, cookies_path)
        finally:
            ctx.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--login", action="store_true",
                    help="Show browser for manual login (first run or re-auth).")
    ap.add_argument("--force", action="store_true",
                    help="Force re-login even if current profile is authenticated.")
    ap.add_argument("--mcp-path", type=Path, default=DEFAULT_MCP_DIR,
                    help=f"Path to openevidence-mcp install directory "
                         f"(default: {DEFAULT_MCP_DIR})")
    ap.add_argument("--channel", choices=["chrome", "msedge", "chromium"],
                    default=None,
                    help="Browser channel to launch. Default = Playwright's bundled "
                         "Chromium. Use 'chrome' or 'msedge' to drive the user's "
                         "installed browser (avoids Google OAuth automation-block).")
    args = ap.parse_args()
    sys.exit(main(mcp_dir=args.mcp_path.resolve(),
                  interactive=args.login,
                  force=args.force,
                  channel=args.channel))
