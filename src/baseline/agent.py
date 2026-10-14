"""Kept for backward compatibility. The shared loop lives in src/core/agent.py.

The exact runner used for the formal Version A development run is preserved in
results/baseline/runner_snapshot_A-dev-20261011T123502Z/.
"""

from src.core import agent as _core
from src.baseline.version import VERSION


def run_question(question, metadata=None, log_path=None):
    return _core.run_question(question, VERSION, metadata=metadata, log_path=log_path)


if __name__ == "__main__":
    record = run_question("How many orders are in the orders table?")
    print("\n--- FINAL ANSWER ---")
    print(record["final_answer"])
