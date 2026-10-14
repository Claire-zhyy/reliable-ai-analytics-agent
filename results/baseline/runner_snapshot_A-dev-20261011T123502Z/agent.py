from pathlib import Path
from datetime import datetime, timezone
import json

from dotenv import load_dotenv
from openai import OpenAI

from src.baseline.db import get_schema, run_sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()

MODEL = "gpt-5.6-terra"

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


def save_log(record, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_question(question, metadata=None, log_path=None):
    schema = get_schema()

    instructions = f"""
You are a data analyst answering questions about an ecommerce database.

You can use the run_sql tool to query the database.

The only database context available to you is the raw schema below.

DATABASE SCHEMA:

{schema}
"""

    input_items = [
        {
            "role": "user",
            "content": question
        }
    ]

    tool_trace = []

    for _ in range(5):
        response = client.responses.create(
            model=MODEL,
            instructions=instructions,
            input=input_items,
            tools=TOOLS,
            reasoning={"effort": "medium"}
        )

        input_items += response.output

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not tool_calls:
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": MODEL,
                "question": question,
                "tool_calls": tool_trace,
                "status": "completed",
                "final_answer": response.output_text
            }

            if metadata:
                record.update(metadata)

            if log_path:
                save_log(record, log_path)

            return record

        for tool_call in tool_calls:
            if tool_call.name != "run_sql":
                raise ValueError(f"Unknown tool: {tool_call.name}")

            arguments = json.loads(tool_call.arguments)
            query = arguments["query"]

            print("\n--- GENERATED SQL ---")
            print(query)

            result = run_sql(query)

            print("\n--- SQL RESULT ---")
            print(result)

            result_obj = json.loads(result)

            tool_trace.append(
                {
                    "tool": "run_sql",
                    "query": query,
                    "result": result_obj
                }
            )

            # Version A/B rule:
            # SQL execution errors end the item immediately.
            # Only Version C is allowed bounded self-repair.
            if "error" in result_obj:
                record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": MODEL,
                    "question": question,
                    "tool_calls": tool_trace,
                    "status": "sql_execution_error",
                    "final_answer": None
                }

                if metadata:
                    record.update(metadata)

                if log_path:
                    save_log(record, log_path)

                return record

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result
                }
            )

    raise RuntimeError("Too many tool-calling rounds.")


if __name__ == "__main__":
    record = run_question(
        "How many orders are in the orders table?"
    )

    print("\n--- FINAL ANSWER ---")
    print(record["final_answer"])
