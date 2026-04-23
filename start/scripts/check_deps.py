"""
check_deps.py - Dependency screen for the paper-to-deck pipeline.

Run this at the start of every new session, BEFORE invoking extract_paper.py.
It inspects the active Python environment for required and optional packages,
reports their status to stdout, and exits non-zero only when a *required*
package is missing.

Philosophy:
  - Required missing  = stop; the user must install before we can proceed.
  - Optional missing  = warn; the pipeline will work but some features (V5
                        native tables, Q17 public-imagery fetch) will be
                        silently disabled.
  - Never auto-install. The install command is printed; the user runs it.

Exit codes:
    0  all required packages present (optional may be missing, reported)
    2  one or more required packages missing

Windows cp950 safety: stdout is ASCII-only.
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


@dataclass
class Dep:
    module: str            # importable module name
    pip_name: str          # pip install name (often same as module)
    required: bool
    purpose: str           # one-line description for the user
    install_hint: str = ""  # extra install note (e.g. size, platform)


# Ordered by criticality, most important first
DEPS = [
    Dep(
        module="fitz",  # pymupdf imports as fitz
        pip_name="pymupdf",
        required=True,
        purpose="PDF text + image extraction (core of extract_paper.py)",
    ),
    Dep(
        module="PIL",
        pip_name="pillow",
        required=True,
        purpose="Image rotation + format conversion (landscape tables)",
    ),
    Dep(
        module="docling",
        pip_name="docling",
        required=False,
        purpose="Tier 0 extractor. Enables native editable PPT tables "
                "(V5 archetype) via structured HTML + tbl-NN.json output.",
        install_hint="~500 MB model download on first run. MIT licensed.",
    ),
    Dep(
        module="requests",
        pip_name="requests",
        required=False,
        purpose="Fetching public-domain contextual imagery "
                "(interview Q17, Wikimedia / NIH Open-i / CDC PHIL).",
    ),
]


def check() -> tuple[list[Dep], list[Dep]]:
    """Return (missing_required, missing_optional)."""
    missing_required: list[Dep] = []
    missing_optional: list[Dep] = []
    for dep in DEPS:
        try:
            importlib.import_module(dep.module)
        except ImportError:
            if dep.required:
                missing_required.append(dep)
            else:
                missing_optional.append(dep)
    return missing_required, missing_optional


def report() -> int:
    missing_required, missing_optional = check()

    # Compact status line for present packages
    present = [d for d in DEPS if d not in missing_required + missing_optional]
    for dep in present:
        tag = "[REQ]" if dep.required else "[OPT]"
        print(f"  OK  {tag}  {dep.pip_name}")

    if missing_required:
        print()
        print("[BLOCK] Required packages are missing. Install before continuing:")
        for dep in missing_required:
            print(f"    py -m pip install --user {dep.pip_name}")
            print(f"        ({dep.purpose})")
        print()
        print("Re-run this script after installing.")
        return 2

    if missing_optional:
        print()
        print("[WARN]  Optional packages missing. Pipeline will run, but:")
        for dep in missing_optional:
            print(f"  - {dep.pip_name} is not installed")
            print(f"    Purpose: {dep.purpose}")
            if dep.install_hint:
                print(f"    Install: py -m pip install --user {dep.pip_name}"
                      f"    ({dep.install_hint})")
            else:
                print(f"    Install: py -m pip install --user {dep.pip_name}")
        print()
        print("Proceeding is safe. Install optional packages later if you want")
        print("the features above.")
    else:
        print()
        print("[OK] All dependencies present. Ready for extract_paper.py.")

    return 0


if __name__ == "__main__":
    sys.exit(report())
