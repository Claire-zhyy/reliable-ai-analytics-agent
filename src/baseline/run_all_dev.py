import argparse
import collections
import csv
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.baseline.agent import run_question, save_log, INFRA_FAILURE_STATUSES


PROJECT_ROOT = Path(__file__).resolve().parents[2]
QUESTIONS_PATH = PROJECT_ROOT / "benchmark" / "questions-dev.csv"
OUTPUT_PATH = PROJECT_ROOT / "results" / "baseline" / "dev_runs.jsonl"


def build_metadata(run_id, row, attempt, rerun_reason=None):
    metadata = {
        "run_id": run_id,
        "version": "A",
        "split": "development",
        "retry_count": 0,  # Version C self-repair count; always 0 for A/B
        "attempt": attempt,
        "question_id": row["question_id"],
        "difficulty": row["difficulty"],
        "question_type": row["question_type"],
        "expected_behavior": row["expected_behavior"],
        "ambiguity_handling": row["ambiguity_handling"]
    }

    if rerun_reason:
        metadata["rerun_reason"] = rerun_reason

    return metadata


def run_item(row, metadata):
    """Run one question; never let a single item stop the batch."""

    try:
        return run_question(
            question=row["question"],
            metadata=metadata,
            log_path=OUTPUT_PATH
        )
    except Exception as exc:
        # Unexpected failure inside the runner itself: infrastructure, eligible for rerun.
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question": row["question"],
            "status": "runner_error",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "final_answer": None
        }
        record.update(metadata)
        save_log(record, OUTPUT_PATH)
        return record


def load_latest_records():
    latest = {}
    with OUTPUT_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            latest[record["question_id"]] = record
    return latest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--retry-infra",
        action="store_true",
        help="Rerun only items whose latest record is an infrastructure failure "
             "(api_error or runner_error), appending new attempts to the same file."
    )
    args = parser.parse_args()

    with QUESTIONS_PATH.open("r", encoding="utf-8") as f:
        questions = list(csv.DictReader(f))

    if args.retry_infra:
        if not OUTPUT_PATH.exists():
            raise FileNotFoundError(f"{OUTPUT_PATH} does not exist; nothing to retry.")

        latest = load_latest_records()
        to_run = []
        for row in questions:
            previous = latest.get(row["question_id"])
            if previous and previous["status"] in INFRA_FAILURE_STATUSES:
                to_run.append((row, previous))

        if not to_run:
            print("No infrastructure failures to retry.")
            return

        for i, (row, previous) in enumerate(to_run, start=1):
            print("\n" + "=" * 80)
            print(f"[retry {i}/{len(to_run)}] {row['question_id']}: {row['question']}")
            print("=" * 80)

            reason = f"{previous['status']}: {previous.get('error', '')}"
            metadata = build_metadata(
                previous["run_id"], row, previous.get("attempt", 1) + 1, reason
            )
            record = run_item(row, metadata)
            print(f"\n--- STATUS: {record['status']} ---")

    else:
        if OUTPUT_PATH.exists():
            raise FileExistsError(
                f"{OUTPUT_PATH} already exists. "
                "Delete it manually only if you intentionally want to rerun the formal baseline, "
                "or use --retry-infra to rerun infrastructure failures."
            )

        total = len(questions)
        run_id = "A-dev-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        print(f"Run ID: {run_id}")
        print(f"Running {total} development questions.")
        print(f"Results will be saved to: {OUTPUT_PATH}")

        for i, row in enumerate(questions, start=1):
            print("\n" + "=" * 80)
            print(f"[{i}/{total}] {row['question_id']}: {row['question']}")
            print("=" * 80)

            record = run_item(row, build_metadata(run_id, row, attempt=1))

            print(f"\n--- STATUS: {record['status']} ---")
            print("\n--- FINAL ANSWER ---")
            print(record["final_answer"])

    latest = load_latest_records()
    counts = collections.Counter(r["status"] for r in latest.values())
    print("\nFinished. Latest status per question:", dict(counts))

    infra = [q for q, r in latest.items() if r["status"] in INFRA_FAILURE_STATUSES]
    if infra:
        print(f"Infrastructure failures to retry with --retry-infra: {', '.join(infra)}")


if __name__ == "__main__":
    main()
