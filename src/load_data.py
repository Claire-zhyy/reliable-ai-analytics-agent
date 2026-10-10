from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "olist.duckdb"

TABLE_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}

conn = duckdb.connect(str(DB_PATH))

for table_name, filename in TABLE_FILES.items():
    csv_path = DATA_DIR / filename

    conn.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT *
        FROM read_csv_auto(?)
        """,
        [str(csv_path)],
    )

    row_count = conn.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).fetchone()[0]

    print(f"{table_name}: {row_count:,} rows")

conn.close()

print(f"\nDatabase created at: {DB_PATH}")
