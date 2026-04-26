"""Reproducible demo entrypoint for video recording."""

from __future__ import annotations

import runpy
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    runpy.run_path(str(PROJECT_ROOT / "scripts/03_run_loop.py"), run_name="__main__")


if __name__ == "__main__":
    main()
