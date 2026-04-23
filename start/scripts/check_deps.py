"""
check_deps.py - Dependency screen for the paper-to-deck pipeline.

Run this at the start of every new session, BEFORE invoking extract_paper.py.
It inspects the active environment for required and optional packages + external
CLI tools, reports status to stdout, and exits non-zero only when a *required*
dependency is missing.

Philosophy:
  - Required missing  = stop; the user must install before we can proceed.
  - Optional missing  = warn; the pipeline will work but some features
                        (V5 native tables, Q17 public-imagery fetch,
                        OpenEvidence citation-audit MCP) will be silently
                        disabled.
  - Never auto-install. The install command is printed; the user runs it.

Dependency classes:
  - Python package (importable module)    -- via importlib
  - External binary (command on PATH)     -- via shutil.which + `--version`

Exit codes:
    0  all required dependencies present (optional may be missing, reported)
    2  one or more required dependencies missing

Windows cp950 safety: stdout is ASCII-only.
"""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


@dataclass
class PyDep:
    module: str            # importable module name
    pip_name: str          # pip install name (often same as module)
    required: bool
    purpose: str           # one-line description
    install_hint: str = "" # extra install note (size, platform)

    def check(self) -> bool:
        try:
            importlib.import_module(self.module)
            return True
        except ImportError:
            return False

    def install_cmd(self) -> str:
        return f"py -m pip install --user {self.pip_name}"

    def label(self) -> str:
        return self.pip_name


@dataclass
class BinDep:
    cmd: str               # command to look for on PATH
    version_args: list     # args to get version (["--version"] usually)
    required: bool
    purpose: str
    install_hint: str = "" # how to install
    min_version: Optional[str] = None  # e.g. "20.0.0" for Node

    def check(self) -> bool:
        return shutil.which(self.cmd) is not None

    def version(self) -> str:
        """Return version string, or '?' if cannot determine."""
        try:
            result = subprocess.run(
                [self.cmd] + self.version_args,
                capture_output=True, text=True, timeout=5
            )
            return (result.stdout or result.stderr).strip().splitlines()[0]
        except Exception:
            return "?"

    def install_cmd(self) -> str:
        return self.install_hint or f"(install {self.cmd})"

    def label(self) -> str:
        return self.cmd


# =========================================================================
# Dependency registry
# =========================================================================

PY_DEPS = [
    PyDep(module="fitz", pip_name="pymupdf", required=True,
          purpose="PDF text + image extraction (core of extract_paper.py)"),
    PyDep(module="PIL", pip_name="pillow", required=True,
          purpose="Image rotation + format conversion (landscape tables)"),
    PyDep(module="docling", pip_name="docling", required=False,
          purpose="Tier 0 extractor. Enables native editable PPT tables "
                  "(V5 archetype) via structured HTML + tbl-NN.json output.",
          install_hint="~500 MB model download on first run. MIT licensed."),
    PyDep(module="requests", pip_name="requests", required=False,
          purpose="Fetching public-domain contextual imagery "
                  "(interview Q17, Wikimedia / NIH Open-i / CDC PHIL)."),
]

BIN_DEPS = [
    BinDep(cmd="node", version_args=["--version"], required=False,
           purpose="Required to run OpenEvidence MCP server "
                   "(citation-audit integration post-deck). Need Node >= 20.",
           install_hint="Install Node.js 20+ from https://nodejs.org "
                        "(or winget install OpenJS.NodeJS.LTS on Windows)",
           min_version="20.0.0"),
    BinDep(cmd="npm", version_args=["--version"], required=False,
           purpose="Package manager for OpenEvidence MCP server build "
                   "(ships with Node.js).",
           install_hint="Comes with Node.js"),
    BinDep(cmd="git", version_args=["--version"], required=False,
           purpose="Clone the OpenEvidence MCP server repo "
                   "(htlin222/openevidence-mcp).",
           install_hint="Install Git for Windows from https://git-scm.com "
                        "(or winget install Git.Git)"),
    BinDep(cmd="claude", version_args=["--version"], required=False,
           purpose="Claude Code CLI, needed to register the OE MCP server "
                   "via `claude mcp add-json`.",
           install_hint="Already present if you are running Claude Code "
                        "(skip if not using Claude Code)"),
]


# =========================================================================
# Reporting
# =========================================================================

def check_all() -> tuple[list, list]:
    """Return (missing_required, missing_optional) across all dep classes."""
    missing_required, missing_optional = [], []
    for dep in PY_DEPS + BIN_DEPS:
        if not dep.check():
            if dep.required:
                missing_required.append(dep)
            else:
                missing_optional.append(dep)
    return missing_required, missing_optional


def report() -> int:
    missing_required, missing_optional = check_all()
    all_deps = PY_DEPS + BIN_DEPS
    present = [d for d in all_deps if d not in missing_required + missing_optional]

    # Section: Python packages (pipeline core)
    print("-- Python packages (paper-to-deck pipeline) --")
    for dep in PY_DEPS:
        if dep in missing_required:
            print(f"  MISS [REQ]  {dep.label():15s} <-- blocks pipeline")
        elif dep in missing_optional:
            print(f"  MISS [OPT]  {dep.label():15s} (optional)")
        else:
            print(f"  OK   [{('REQ' if dep.required else 'OPT')}]  {dep.label()}")

    # Section: External CLIs (OE MCP + tooling)
    print()
    print("-- External CLIs (OpenEvidence MCP + tooling) --")
    for dep in BIN_DEPS:
        if dep in missing_required:
            print(f"  MISS [REQ]  {dep.label():15s} <-- blocks pipeline")
        elif dep in missing_optional:
            print(f"  MISS [OPT]  {dep.label():15s} (OE audit feature disabled)")
        else:
            v = dep.version()
            print(f"  OK   [OPT]  {dep.label():8s} {v}")

    # Block on required missing
    if missing_required:
        print()
        print("[BLOCK] Required dependencies missing. Install before continuing:")
        for dep in missing_required:
            print(f"    {dep.install_cmd()}")
            print(f"        Purpose: {dep.purpose}")
        print()
        print("Re-run this script after installing.")
        return 2

    # Warn on optional missing
    if missing_optional:
        print()
        print("[WARN] Optional dependencies missing. Impact per-feature:")
        for dep in missing_optional:
            print(f"  - {dep.label()}: {dep.purpose}")
            print(f"      Install: {dep.install_cmd()}")
            if dep.install_hint and isinstance(dep, PyDep) and dep.install_hint not in dep.install_cmd():
                print(f"      Note:    {dep.install_hint}")
        print()
        print("Proceeding with paper-to-deck is safe. Install the missing items")
        print("later if/when you want the corresponding feature.")
    else:
        print()
        print("[OK] All dependencies present. Ready for extract_paper.py")
        print("     (and OpenEvidence citation-audit if MCP server is configured).")

    return 0


if __name__ == "__main__":
    sys.exit(report())
