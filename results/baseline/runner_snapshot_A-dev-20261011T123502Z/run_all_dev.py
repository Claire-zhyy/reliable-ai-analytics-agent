import csv
from datetime import datetime, timezone
from pathlib import Path

from src.baseline.agent import run_question


PROJECT_ROOT = Path(__file__).resolve().parents[2]
QUESTIONS_PATH = PROJECT_ROOT / "benchmark" / "questions-dev.csv"
OUTPUT_PATH = PROJECT_ROOT / "results" / "baseline" / "dev_runs.jsonl"


def main():
    with QUESTIONS_PATH.open("r", encoding="utf-8") as f:
        questions = list(csv.DictReader(f))

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            f"{OUTPUT_PATH} already exists. "
            "Delete it manually only if you intentionally want to rerun the formal baseline."
        )

    total = len(questions)

    run_id = "A-dev-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"Run ID: {run_id}")
    print(f"Running {total} development questions.")
    print(f"Results will be saved to: {OUTPUT_PATH}")

    for i, row in enumerate(questions, start=1):
        question_id = row["question_id"]
        question = row["question"]

        print("\n" + "=" * 80)
        print(f"[{i}/{total}] {question_id}: {question}")
        print("=" * 80)

        metadata = {
            "run_id": run_id,
            "version": "A",
            "split": "development",
            "temperature": "api_default",
            "retry_count": 0,
            "question_id": question_id,
            "difficulty": row["difficulty"],
            "question_type": row["question_type"],
            "expected_behavior": row["expected_behavior"],
            "ambiguity_handling": row["ambiguity_handling"]
        }

        record = run_question(
            question=question,
            metadata=metadata,
            log_path=OUTPUT_PATH
        )

        print("\n--- FINAL ANSWER ---")
        print(record["final_answer"])

    print("\nFinished.")
    print(f"Saved {total} baseline runs to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
