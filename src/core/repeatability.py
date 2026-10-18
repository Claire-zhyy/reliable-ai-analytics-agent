"""Repeatability test (methodology §8.6): run the pre-registered questions
three times each on final Version C, using the frozen system unchanged.

The questions were recorded in results/system-freeze-record.md before the
held-out run. This script only selects questions and repeats them; it reuses
the frozen runner, agent and Version C definition without modification.

Usage (from the project root):
  python -m src.core.repeatability
"""

import csv
import importlib
from datetime import datetime, timezone

from src.core.runner import (
    PROJECT_ROOT, QUESTION_FILES, VERSION_MODULES,
    build_metadata, preflight_database, run_item,
)

QUESTION_IDS = ["Q01", "Q18", "Q23", "Q31", "Q37"]
REPETITIONS = 3
VERSION = "C"
OUT_PATH = PROJECT_ROOT / "results" / "improved" / "repeatability_runs.jsonl"


def main():
    if OUT_PATH.exists():
        raise FileExistsError(f"{OUT_PATH} already exists; the repeatability test is run once.")

    preflight_database()
    version = importlib.import_module(VERSION_MODULES[VERSION]).VERSION

    with QUESTION_FILES["dev"].open("r", encoding="utf-8") as f:
        rows = {r["question_id"]: r for r in csv.DictReader(f)}
    missing = [q for q in QUESTION_IDS if q not in rows]
    if missing:
        raise ValueError(f"Not development questions: {missing}")

    run_id = "C-repeat-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"Run ID: {run_id}\nResults: {OUT_PATH}")

    for rep in range(1, REPETITIONS + 1):
        for qid in QUESTION_IDS:
            metadata = build_metadata(run_id, version.name, "dev", rows[qid], attempt=1)
            metadata["repetition"] = rep
            print(f"\n[rep {rep}/{REPETITIONS}] {qid}")
            record = run_item(rows[qid], version, metadata, OUT_PATH)
            print(f"--- STATUS: {record['status']} ---")

    print("\nFinished.")


if __name__ == "__main__":
    main()
