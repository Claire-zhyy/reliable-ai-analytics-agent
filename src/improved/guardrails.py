"""Version C code-level checks around the shared run_sql tool.

These checks are enforced by the program, not requested of the model:

1. validate_sql: binds the query against the real DuckDB catalog (EXPLAIN)
   before execution, so non-existent tables or columns are rejected with the
   binder's message instead of being executed.
2. check_result -> join fan-out: for every query block that joins base tables
   and sums, averages or passes on a numeric measure from one of them, the
   program counts joined rows against distinct primary keys of that table. If
   the join repeats the table's rows, a warning says which aggregate is affected.
3. check_result -> duplicate key in a ranking: if a ranked result (ORDER BY +
   LIMIT) returns the same entity id more than once, a warning says so.

Warnings are returned to the model inside the tool output. Check details,
including skipped checks and internal errors, are logged in the trace only.
A check that cannot run never blocks the query.
"""

import sqlglot
from sqlglot import exp
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.scope import traverse_scope

from src.core.db import connect, get_schema_dict


# Primary keys from docs/02-tables-model-context.md. geolocation has no
# reliable key and is not checked.
PRIMARY_KEYS = {
    "orders": ["order_id"],
    "customers": ["customer_id"],
    "order_items": ["order_id", "order_item_id"],
    "order_payments": ["order_id", "payment_sequential"],
    "order_reviews": ["review_id", "order_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "product_category_translation": ["product_category_name"],
}

NUMERIC_TYPES = ("DOUBLE", "BIGINT", "INTEGER", "DECIMAL", "FLOAT", "HUGEINT", "SMALLINT", "REAL")

SCHEMA = get_schema_dict()


def is_measure(table, column):
    """Numeric, non-key columns (price, freight_value, payment_value, review_score...)."""

    col_type = SCHEMA.get(table, {}).get(column, "")
    keyish = column.endswith("_id") or column in PRIMARY_KEYS.get(table, []) or column.endswith("_prefix")
    return col_type.upper().startswith(NUMERIC_TYPES) and not keyish


# ---------------------------------------------------------------------------
# 1. Pre-execution schema validation
# ---------------------------------------------------------------------------

def validate_sql(query):
    """Return a rejection message, or None if the query binds against the catalog."""

    conn = connect()
    try:
        # Parse first so syntax errors are reported against the model's own text.
        try:
            conn.extract_statements(query)
        except Exception as exc:
            return "Rejected before execution: the query could not be parsed. " + str(exc)

        # Then bind against the real catalog without running the query.
        conn.execute("EXPLAIN " + query)
        return None
    except Exception as exc:
        message = str(exc)
        if "Catalog Error" in message or "Binder Error" in message:
            return (
                "Rejected before execution by the schema check: the query references "
                "a table or column that does not exist or cannot be resolved. "
                + message
            )
        return "Rejected before execution: " + message
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 2. Join fan-out check
# ---------------------------------------------------------------------------

def _scope_aggregates(select):
    """SUM/AVG expressions that belong to this SELECT (not to nested subqueries)."""

    return [
        node for node in select.find_all(exp.Sum, exp.Avg)
        if node.find_ancestor(exp.Select) is select
    ]


def _fanout_candidates(scope, is_root):
    """Return {alias: (table, [reasons])} for measure columns that could be over-counted."""

    select = scope.expression
    tables = {alias: src.name for alias, src in scope.sources.items() if isinstance(src, exp.Table)}
    candidates = {}

    for agg in _scope_aggregates(select):
        for column in agg.find_all(exp.Column):
            alias = column.table
            if alias in tables and is_measure(tables[alias], column.name):
                label = f"{agg.key.upper()}({tables[alias]}.{column.name})"
                candidates.setdefault(alias, (tables[alias], []))[1].append(label)

    # A non-root block (CTE or subquery) that passes a raw measure through a
    # join feeds later aggregation, so repeated rows there matter too.
    if not is_root and not select.args.get("group"):
        for projection in select.expressions:
            for column in projection.find_all(exp.Column):
                if column.find_ancestor(exp.AggFunc):
                    continue
                alias = column.table
                if alias in tables and is_measure(tables[alias], column.name):
                    label = f"{tables[alias]}.{column.name} (passed to a later aggregation)"
                    candidates.setdefault(alias, (tables[alias], []))[1].append(label)

    return candidates


def _diagnostic_sql(select, alias, table):
    """COUNT(*) vs COUNT(DISTINCT pk) over the same FROM/JOIN/WHERE as the query block."""

    keys = [exp.column(k, table=alias) for k in PRIMARY_KEYS[table]]
    if len(keys) == 1:
        distinct_key = keys[0]
    else:
        distinct_key = exp.func("CONCAT_WS", exp.Literal.string("|"), *keys)

    diag = select.copy()
    for arg in ("with", "group", "having", "order", "limit", "offset", "qualify", "distinct", "windows"):
        diag.set(arg, None)
    diag.set("expressions", [
        exp.alias_(exp.Count(this=exp.Star()), "n_rows"),
        exp.alias_(exp.Count(this=exp.Distinct(expressions=[distinct_key])), "n_keys"),
    ])
    return diag.sql(dialect="duckdb")


def check_fanout(query):
    warnings, log = [], []

    try:
        tree = sqlglot.parse_one(query, read="duckdb")
        tree = qualify(tree, schema=SCHEMA, dialect="duckdb", validate_qualify_columns=False)
    except Exception as exc:
        return warnings, [{"check": "fanout", "status": "skipped", "reason": f"parse/qualify failed: {exc}"[:300]}]

    root = tree
    conn = connect()
    try:
        for scope in traverse_scope(tree):
            select = scope.expression
            if not isinstance(select, exp.Select):
                continue
            # Only self-contained blocks over base tables: a diagnostic can then
            # be run on exactly the same FROM / JOIN / WHERE.
            if len(scope.sources) < 2 or not all(isinstance(s, exp.Table) for s in scope.sources.values()):
                continue
            if select.args.get("distinct"):
                log.append({"check": "fanout", "status": "skipped", "reason": "SELECT DISTINCT block"})
                continue

            candidates = _fanout_candidates(scope, is_root=select is root)
            for alias, (table, labels) in candidates.items():
                if table not in PRIMARY_KEYS:
                    continue
                diag_sql = _diagnostic_sql(select, alias, table)
                try:
                    n_rows, n_keys = conn.execute(diag_sql).fetchone()
                except Exception as exc:
                    log.append({"check": "fanout", "table": table, "status": "error", "reason": str(exc)[:300]})
                    continue

                entry = {"check": "fanout", "table": table, "n_rows": n_rows, "n_keys": n_keys,
                         "affected": sorted(set(labels)), "diagnostic_sql": diag_sql}
                if n_keys and n_rows > n_keys:
                    entry["status"] = "warning"
                    warnings.append(
                        f"Join fan-out: in this query the joins repeat rows of {table} "
                        f"({n_rows:,} joined rows for {n_keys:,} distinct {table} records), so "
                        f"{', '.join(sorted(set(labels)))} counts some {table} values more than once. "
                        f"Aggregate {table} to the join key before joining, or explain why this weighting is intended."
                    )
                else:
                    entry["status"] = "ok"
                log.append(entry)
    finally:
        conn.close()

    return warnings, log


# ---------------------------------------------------------------------------
# 3. Duplicate entity in a ranked result
# ---------------------------------------------------------------------------

def check_ranking_duplicates(query, result_obj):
    try:
        tree = sqlglot.parse_one(query, read="duckdb")
    except Exception:
        return [], [{"check": "ranking_duplicates", "status": "skipped", "reason": "parse failed"}]

    if not (tree.args.get("order") and tree.args.get("limit")):
        return [], []

    columns = result_obj.get("columns", [])
    id_columns = [i for i, c in enumerate(columns) if c.endswith("_id")]
    if not id_columns:
        return [], []

    index = id_columns[0]
    name = columns[index]
    seen, repeated = set(), []
    for row in result_obj.get("rows", []):
        value = row[index]
        if value in seen and value not in repeated:
            repeated.append(value)
        seen.add(value)

    if not repeated:
        return [], [{"check": "ranking_duplicates", "column": name, "status": "ok"}]

    shown = ", ".join(str(v) for v in repeated[:3])
    return (
        [f"Duplicate entity in ranking: {name} {shown} appears more than once in this ranked result. "
         f"If the ranking is meant to be one row per {name}, aggregate to that grain first."],
        [{"check": "ranking_duplicates", "column": name, "status": "warning", "repeated": repeated[:10]}],
    )


def check_result(query, result_obj):
    """Run all post-execution checks. Returns (warnings for the model, log entries for the trace)."""

    warnings, log = [], []
    for check in (lambda: check_fanout(query), lambda: check_ranking_duplicates(query, result_obj)):
        try:
            w, l = check()
        except Exception as exc:  # a check must never break the run
            w, l = [], [{"check": "internal", "status": "error", "reason": str(exc)[:300]}]
        warnings += w
        log += l
    return warnings, log
