"""Version B: Version A + business context (data dictionary and business semantics).

Version B adds knowledge only. It adds no workflow steps: SQL errors still end the
item, and no code-level checks run. The two context files are inserted verbatim
(YAML frontmatter removed), so any change to them changes context_hash.
"""

from pathlib import Path

from src.core.agent import VersionConfig, sha256_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONTEXT_FILES = [
    "docs/02-tables-model-context.md",
    "docs/03-olist-business-semantics.md",
]


def strip_frontmatter(text):
    """Remove a leading Obsidian/YAML frontmatter block, if present."""

    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + len("\n---\n"):].lstrip("\n")
    return text


def load_context():
    data_dictionary, semantics = [
        strip_frontmatter((PROJECT_ROOT / path).read_text(encoding="utf-8")).strip()
        for path in CONTEXT_FILES
    ]
    return data_dictionary, semantics


DATA_DICTIONARY, BUSINESS_SEMANTICS = load_context()

CONTEXT_HASH = sha256_text(DATA_DICTIONARY + "\n\n" + BUSINESS_SEMANTICS)


def build_context_block(schema):
    # Same base structure as Version A: role, tool, context statement, schema.
    return f"""
You are a data analyst answering questions about an ecommerce database.

You can use the run_sql tool to query the database.

The database context available to you is the raw schema below, followed by the data dictionary and business semantics written by the analytics team.

DATABASE SCHEMA:

{schema}

DATA DICTIONARY:

{DATA_DICTIONARY}

BUSINESS SEMANTICS:

{BUSINESS_SEMANTICS}
"""


def build_instructions(schema):
    return build_context_block(schema)


VERSION = VersionConfig(
    name="B",
    build_instructions=build_instructions,
    context_hash=CONTEXT_HASH,
    context_files=CONTEXT_FILES,
)
