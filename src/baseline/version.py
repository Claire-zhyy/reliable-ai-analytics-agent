"""Version A: raw schema only."""

from src.core.agent import VersionConfig


def build_instructions(schema):
    # Text must stay identical to the Version A development run
    # (prompt_hash 7192e95c..., see results/evaluation-change-log.md).
    return f"""
You are a data analyst answering questions about an ecommerce database.

You can use the run_sql tool to query the database.

The only database context available to you is the raw schema below.

DATABASE SCHEMA:

{schema}
"""


VERSION = VersionConfig(
    name="A",
    build_instructions=build_instructions,
)
