"""DuckDB connection helper."""

from __future__ import annotations

from pathlib import Path

import duckdb

from src.config import settings


def connect(db_path: Path | None = None) -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection, creating the parent data directory if needed."""

    path = db_path or settings.db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))
