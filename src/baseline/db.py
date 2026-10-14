"""Kept for backward compatibility. The shared implementation lives in src/core/db.py."""

from src.core.db import *  # noqa: F401,F403
from src.core.db import execute_sql, get_schema, run_sql, MAX_RESULT_ROWS  # noqa: F401
