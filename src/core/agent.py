"""Shared tool-calling loop for Versions A, B and C.

The model, reasoning effort, tool schema, round limit, row cap and database are
identical for every version. A version only changes:
  - the instructions text (A: schema; B: + business context; C: + workflow rules)
  - whether SQL errors are returned for bounded self-repair (C only)
  - whether code-level checks run around run_sql (C only)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional
import hashlib
import json
import subprocess

from dotenv import load_dotenv
from openai import OpenAI, APIError

from src.core.db import get_schema, execute_sql, MAX_RESULT_ROWS


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()

# Run configuration. Fixed for Versions A, B and C; recorded in every log record.
MODEL = "gpt-5.6-terra"
REASONING_EFFORT = "medium"
TEMPERATURE = "api_default"  # reasoning model; temperature is not set explicitly
MAX_TOOL_ROUNDS = 5  # limit on model rounds, not on SQL queries (one round can hold several calls)

TOOLS = [
    {
        "type": "function",
        "name": "run_sql",
        "description": "Execute a read-only SQL query against the Olist DuckDB database.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL query to execute."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    }
]

# Item statuses.
# Model failures (graded normally): sql_execution_error, max_rounds_exceeded, unknown_tool_call
# Infrastructure failures (eligible for one logged rerun, methodology §8.4): api_error, runner_error
INFRA_FAILURE_STATUSES = {"api_error", "runner_error"}


@dataclass
class VersionConfig:
    name: str                                   # "A", "B" or "C"
    build_instructions: Callable[[str], str]    # schema text -> instructions
    context_hash: Optional[str] = None          # hash of business context files (B/C)
    context_files: List[str] = field(default_factory=list)
    max_repairs: int = 0                        # SQL errors returned to the model for repair (C only)
    validate_sql: Optional[Callable] = None     # query -> error message or None (C only)
    check_result: Optional[Callable] = None     # (query, result_obj) -> (warnings, check_log) (C only)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_git_state():
    """Return (commit, dirty) for the project repo, or (None, None) if unavailable."""

    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
        return commit, bool(status)
    except Exception:
        return None, None


def save_log(record, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_question(question, version, metadata=None, log_path=None):
    schema = get_schema()
    instructions = version.build_instructions(schema)
    git_commit, git_dirty = get_git_state()

    input_items = [
        {
            "role": "user",
            "content": question
        }
    ]

    tool_trace = []
    response_ids = []
    normal_rounds = 0
    repair_rounds = 0
    repairs_used = 0

    def finish(status, final_answer=None, error=None):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": version.name,
            "model": MODEL,
            "temperature": TEMPERATURE,
            "reasoning_effort": REASONING_EFFORT,
            "max_tool_rounds": MAX_TOOL_ROUNDS,
            "max_result_rows": MAX_RESULT_ROWS,
            "max_repairs": version.max_repairs,
            "git_commit": git_commit,
            "git_dirty": git_dirty,
            "prompt_hash": sha256_text(instructions),
            "schema_hash": sha256_text(schema),
            "context_hash": version.context_hash,
            "context_files": version.context_files,
            "question": question,
            "tool_calls": tool_trace,
            "tool_rounds_used": normal_rounds + repair_rounds,
            "repair_rounds_used": repair_rounds,
            "retry_count": repairs_used,
            "query_count": len(tool_trace),
            "result_truncated": any(t["truncated"] for t in tool_trace),
            "guardrail_warning_count": sum(len(t.get("warnings", [])) for t in tool_trace),
            "response_ids": response_ids,
            "status": status,
            "final_answer": final_answer,
        }

        if error is not None:
            record["error"] = error

        if metadata:
            record.update(metadata)

        if log_path:
            save_log(record, log_path)

        return record

    pending_repair = False

    while True:
        # Repair rounds (C only) do not count against the shared round limit
        # (methodology §1: repairs count against the retry limit instead).
        if not pending_repair and normal_rounds >= MAX_TOOL_ROUNDS:
            # The model was still calling tools after MAX_TOOL_ROUNDS responses.
            return finish("max_rounds_exceeded")

        try:
            response = client.responses.create(
                model=MODEL,
                instructions=instructions,
                input=input_items,
                tools=TOOLS,
                reasoning={"effort": REASONING_EFFORT}
            )
        except APIError as exc:
            return finish("api_error", error=f"{type(exc).__name__}: {exc}")

        if pending_repair:
            repair_rounds += 1
        else:
            normal_rounds += 1
        pending_repair = False

        response_ids.append(getattr(response, "id", None))

        input_items += response.output

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not tool_calls:
            return finish("completed", final_answer=response.output_text)

        for tool_call in tool_calls:
            if tool_call.name != "run_sql":
                return finish(
                    "unknown_tool_call",
                    error=f"Unknown tool: {tool_call.name}"
                )

            arguments = json.loads(tool_call.arguments)
            query = arguments["query"]

            print("\n--- GENERATED SQL ---")
            print(query)

            trace_entry = {"tool": "run_sql", "query": query}

            # C only: check the query against the real catalog before execution.
            rejection = version.validate_sql(query) if version.validate_sql else None

            if rejection:
                result = json.dumps({"error": rejection})
                trace_entry["validation"] = "rejected"
                truncated = False
            else:
                if version.validate_sql:
                    trace_entry["validation"] = "passed"
                executed = execute_sql(query)
                result = executed["output"]
                truncated = executed["truncated"]

            result_obj = json.loads(result)
            trace_entry["truncated"] = truncated

            # C only: code-level checks on successful results. Warnings are
            # appended to the tool output the model sees; check details are
            # logged in the trace only.
            if version.check_result and "error" not in result_obj:
                warnings, check_log = version.check_result(query, result_obj)
                trace_entry["checks"] = check_log
                if warnings:
                    trace_entry["warnings"] = warnings
                    result_obj["warnings"] = warnings
                    result = json.dumps(result_obj, default=str)

            print("\n--- SQL RESULT ---")
            print(result)

            trace_entry["result"] = json.loads(result)
            tool_trace.append(trace_entry)

            if "error" in result_obj:
                # Version A/B rule: SQL errors end the item immediately.
                # Version C: the error is returned to the model for bounded self-repair.
                if repairs_used >= version.max_repairs:
                    return finish("sql_execution_error")

                repairs_used += 1
                trace_entry["returned_for_repair"] = True
                pending_repair = True

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result
                }
            )
