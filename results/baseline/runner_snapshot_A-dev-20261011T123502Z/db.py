from pathlib import Path
import json

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "olist.duckdb"


def get_schema():
    """Return the raw DuckDB schema visible to Version A."""

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        tables = conn.execute("SHOW TABLES").fetchall()

        schema_parts = []

        for (table_name,) in tables:
            columns = conn.execute(f"DESCRIBE {table_name}").fetchall()

            column_lines = [
                f"  - {column[0]} {column[1]}"
                for column in columns
            ]

            schema_parts.append(
                f"Table: {table_name}\n" + "\n".join(column_lines)
            )

        return "\n\n".join(schema_parts)

    finally:
        conn.close()


def run_sql(query):
    """Execute SQL against the Olist DuckDB database."""

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        result = conn.execute(query)

        columns = (
            [description[0] for description in result.description]
            if result.description
            else []
        )

        rows = result.fetchmany(200)

        return json.dumps(
            {
                "columns": columns,
                "rows": rows,
            },
            default=str,
        )

    except Exception as exc:
        return json.dumps(
            {
                "error": str(exc),
            }
        )

    finally:
        conn.close()
