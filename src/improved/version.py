"""Version C: Version B + workflow controls.

Prompt level: the rules in src/improved/rules.py, appended after the Version B
context. Code level: pre-execution schema validation, bounded self-repair of SQL
errors, and post-execution structural checks (src/improved/guardrails.py).
"""

from src.core.agent import VersionConfig
from src.improved.guardrails import validate_sql, check_result
from src.improved.rules import rules_text
from src.semantic.version import build_context_block, CONTEXT_FILES, CONTEXT_HASH


# Maximum number of SQL errors (schema rejections or execution errors) returned
# to the model for repair per question. Fixed before the first Version C run.
MAX_REPAIRS = 2

RULES_TEXT = rules_text()


def build_instructions(schema):
    return build_context_block(schema) + f"""
ANALYSIS WORKFLOW RULES:

{RULES_TEXT}
"""


VERSION = VersionConfig(
    name="C",
    build_instructions=build_instructions,
    context_hash=CONTEXT_HASH,
    context_files=CONTEXT_FILES,
    max_repairs=MAX_REPAIRS,
    validate_sql=validate_sql,
    check_result=check_result,
)
