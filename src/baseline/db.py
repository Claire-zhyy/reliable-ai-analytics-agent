from pathlib import Path
import json

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "olist.duckdb"

# Maximum number of result rows returned to the model per query.
# Fixed for Versions A, B and C (see results/evaluation-change-log.md).
MAX_RESULT_ROWS = 200


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


def execute_sql(query):
    """Execute SQL and return the model-visible output plus trace-only metadata.

    Returns a dict:
      - output: the JSON string sent back to the model. Its format is identical
        to the original run_sql output (columns + at most MAX_RESULT_ROWS rows,
        or an error message). Truncation is NOT signalled to the model.
      - truncated: True if the query returned more than MAX_RESULT_ROWS rows.
        Recorded in the trace only.
    """

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        result = conn.execute(query)

        columns = (
            [description[0] for description in result.description]
            if result.description
            else []
        )

        # Fetch one extra row only to detect truncation; it is never returned.
        rows = result.fetchmany(MAX_RESULT_ROWS + 1)
        truncated = len(rows) > MAX_RESULT_ROWS
        rows = rows[:MAX_RESULT_ROWS]

        output = json.dumps(
            {
                "columns": columns,
                "rows": rows,
            },
            default=str,
        )

        return {"output": output, "truncated": truncated}

    except Exception as exc:
        output = json.dumps(
            {
                "error": str(exc),
            }
        )

        return {"output": output, "truncated": False}

    finally:
        conn.close()


def run_sql(query):
    """Execute SQL against the Olist DuckDB database (model-visible output only)."""

    return execute_sql(query)["output"]
