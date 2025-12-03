"""Test suite package for backend components."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_repo_root_on_path() -> None:
    backend_dir = Path(__file__).resolve().parent.parent
    repo_root = backend_dir.parent
    for path in (repo_root, backend_dir):
        str_path = str(path)
        if str_path not in sys.path:
            sys.path.append(str_path)


_ensure_repo_root_on_path()
