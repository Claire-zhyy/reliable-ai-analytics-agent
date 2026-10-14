from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

from dotenv import load_dotenv
from openai import OpenAI, APIError

from src.baseline.db import get_schema, execute_sql, MAX_RESULT_ROWS


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


def build_instructions(schema):
    # Text must stay identical to the Version A development run.
    return f"""
You are a data analyst answering questions about an ecommerce database.

You can use the run_sql tool to query the database.

The only database context available to you is the raw schema below.

DATABASE SCHEMA:

{schema}
"""


def save_log(record, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_question(question, metadata=None, log_path=None):
    schema = get_schema()
    instructions = build_instructions(schema)
    git_commit, git_dirty = get_git_state()

    input_items = [
        {
            "role": "user",
            "content": question
        }
    ]

    tool_trace = []
    response_ids = []
    rounds_used = 0

    def finish(status, final_answer=None, error=None):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "temperature": TEMPERATURE,
            "reasoning_effort": REASONING_EFFORT,
            "max_tool_rounds": MAX_TOOL_ROUNDS,
            "max_result_rows": MAX_RESULT_ROWS,
            "git_commit": git_commit,
            "git_dirty": git_dirty,
            "prompt_hash": sha256_text(instructions),
            "schema_hash": sha256_text(schema),
            "context_hash": None,  # Version A has no context files; B/C set this
            "question": question,
            "tool_calls": tool_trace,
            "tool_rounds_used": rounds_used,
            "query_count": len(tool_trace),
            "result_truncated": any(t["truncated"] for t in tool_trace),
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

    for _ in range(MAX_TOOL_ROUNDS):
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

        rounds_used += 1
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

            executed = execute_sql(query)
            result = executed["output"]

            print("\n--- SQL RESULT ---")
            print(result)

            result_obj = json.loads(result)

            tool_trace.append(
                {
                    "tool": "run_sql",
                    "query": query,
                    "result": result_obj,
                    "truncated": executed["truncated"]
                }
            )

            # Version A/B rule:
            # SQL execution errors end the item immediately.
            # Only Version C is allowed bounded self-repair.
            if "error" in result_obj:
                return finish("sql_execution_error")

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result
                }
            )

    # The model was still calling tools after MAX_TOOL_ROUNDS responses.
    return finish("max_rounds_exceeded")


if __name__ == "__main__":
    record = run_question(
        "How many orders are in the orders table?"
    )

    print("\n--- FINAL ANSWER ---")
    print(record["final_answer"])
