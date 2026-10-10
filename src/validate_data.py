from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "olist.duckdb"

conn = duckdb.connect(str(DB_PATH))

tables = conn.execute(
    "SHOW TABLES"
).fetchall()

print("Tables in database:")
for table in tables:
    print(f"- {table[0]}")

print("\n" + "=" * 60)

for (table_name,) in tables:
    row_count = conn.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).fetchone()[0]

    print(f"\nTABLE: {table_name}")
    print(f"ROW COUNT: {row_count:,}")
    print("FIRST 5 ROWS:")

    rows = conn.execute(
        f"SELECT * FROM {table_name} LIMIT 5"
    ).fetchall()

    for row in rows:
        print(row)

conn.close()
