import csv
from pathlib import Path

from src.baseline.agent import run_question


PROJECT_ROOT = Path(__file__).resolve().parents[2]
QUESTIONS_PATH = PROJECT_ROOT / "benchmark" / "questions-dev.csv"

QUESTION_IDS = {"Q01", "Q02", "Q04", "Q05", "Q07"}


def main():
    with QUESTIONS_PATH.open("r", encoding="utf-8") as f:
        questions = list(csv.DictReader(f))

    selected = [
        row for row in questions
        if row["question_id"] in QUESTION_IDS
    ]

    for row in selected:
        question_id = row["question_id"]
        question = row["question"]

        print("\n" + "=" * 80)
        print(f"{question_id}: {question}")
        print("=" * 80)

        answer = run_question(question)

        print("\n--- FINAL ANSWER ---")
        print(answer)


if __name__ == "__main__":
    main()
