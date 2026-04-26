"""Initialize the local DuckDB schema."""

from __future__ import annotations

from _bootstrap import add_project_root_to_path

PROJECT_ROOT = add_project_root_to_path()

from src.db.conn import connect


def main() -> None:
    schema_path = PROJECT_ROOT / "src/db/schema.sql"
    con = connect()
    try:
        con.execute(schema_path.read_text(encoding="utf-8"))
    finally:
        con.close()
    print(f"Initialized DuckDB schema from {schema_path}")


if __name__ == "__main__":
    main()
