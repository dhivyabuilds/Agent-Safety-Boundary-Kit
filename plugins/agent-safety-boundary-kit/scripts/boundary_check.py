#!/usr/bin/env python3
"""Launch the Agent Safety Boundary Kit checker from an installed Codex plugin."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _find_repo_checker() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "scripts" / "boundary_check.py"
        if candidate.exists() and candidate != here:
            return candidate
    raise SystemExit(
        "Could not find the Agent Safety Boundary Kit checker. "
        "Run this from a full Agent-Safety-Boundary-Kit checkout or use the root scripts/boundary_check.py."
    )


if __name__ == "__main__":
    checker = _find_repo_checker()
    sys.argv[0] = str(checker)
    runpy.run_path(str(checker), run_name="__main__")
