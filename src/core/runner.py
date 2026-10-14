"""Shared evaluation runner for Versions A, B and C.

Usage (from the project root):
  python -m src.core.runner --version B                 # all development questions
  python -m src.core.runner --version B --retry-infra   # rerun api_error / runner_error items only

Held-out questions can only be run from a clean, frozen commit:
  python -m src.core.runner --version C --split heldout
requires `git status` to be clean and HEAD to carry a tag starting with
`system-frozen` (methodology §8).
"""

import argparse
import collections
import csv
import importlib
import json
import subprocess
import traceback
from datetime import datetime, timezone
from pathlib import Path

from src.core.agent import run_question, save_log, get_git_state, INFRA_FAILURE_STATUSES


PROJECT_ROOT = Path(__file__).resolve().parents[2]

VERSION_MODULES = {
    "A": "src.baseline.version",
    "B": "src.semantic.version",
    "C": "src.improved.version",
}

RESULT_DIRS = {
    "A": "baseline",
    "B": "semantic",
    "C": "improved",
}

QUESTION_FILES = {
    "dev": PROJECT_ROOT / "benchmark" / "questions-dev.csv",
    "heldout": PROJECT_ROOT / "benchmark" / "questions-heldout.csv",
}

SPLIT_LABELS = {"dev": "development", "heldout": "held-out"}

FROZEN_TAG_PREFIX = "system-frozen"


def output_path(version_name, split):
    return PROJECT_ROOT / "results" / RESULT_DIRS[version_name] / f"{split}_runs.jsonl"


def assert_frozen():
    """Refuse a held-out run unless the working tree is clean and HEAD is tagged as frozen."""

    commit, _ = get_git_state()
    if commit is None:
        raise RuntimeError("Held-out run refused: git state unavailable.")

    # Everything except run outputs must match the frozen commit. results/ is
    # excluded so that A, B and C (and infrastructure retries) can run in turn.
    changes = subprocess.run(
        ["git", "status", "--porcelain", "--", ".", ":(exclude)results"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    if changes:
        raise RuntimeError(
            "Held-out run refused: uncommitted changes outside results/. "
            "Commit and tag the frozen system first.\n" + changes
        )

    tags = subprocess.run(
        ["git", "tag", "--points-at", "HEAD"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    if not any(t.startswith(FROZEN_TAG_PREFIX) for t in tags):
        raise RuntimeError(
            f"Held-out run refused: HEAD has no tag starting with '{FROZEN_TAG_PREFIX}'. "
            "Freeze prompts, context, workflow code, runner and grader, then tag the commit."
        )


def build_metadata(run_id, version_name, split, row, attempt, rerun_reason=None):
    metadata = {
        "run_id": run_id,
        "version": version_name,
        "split": SPLIT_LABELS[split],
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


def run_item(row, version, metadata, out_path):
    """Run one question; never let a single item stop the batch."""

    try:
        return run_question(
            question=row["question"],
            version=version,
            metadata=metadata,
            log_path=out_path
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
        save_log(record, out_path)
        return record


def load_latest_records(out_path):
    latest = {}
    with out_path.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            latest[record["question_id"]] = record
    return latest


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, choices=sorted(VERSION_MODULES))
    parser.add_argument("--split", default="dev", choices=sorted(QUESTION_FILES))
    parser.add_argument(
        "--retry-infra",
        action="store_true",
        help="Rerun only items whose latest record is an infrastructure failure "
             "(api_error or runner_error), appending new attempts to the same file."
    )
    args = parser.parse_args(argv)

    if args.split == "heldout":
        assert_frozen()

    version = importlib.import_module(VERSION_MODULES[args.version]).VERSION
    out_path = output_path(version.name, args.split)

    with QUESTION_FILES[args.split].open("r", encoding="utf-8") as f:
        questions = list(csv.DictReader(f))

    if args.retry_infra:
        if not out_path.exists():
            raise FileNotFoundError(f"{out_path} does not exist; nothing to retry.")

        latest = load_latest_records(out_path)
        to_run = [
            (row, latest[row["question_id"]])
            for row in questions
            if row["question_id"] in latest
            and latest[row["question_id"]]["status"] in INFRA_FAILURE_STATUSES
        ]

        if not to_run:
            print("No infrastructure failures to retry.")
            return

        for i, (row, previous) in enumerate(to_run, start=1):
            print("\n" + "=" * 80)
            print(f"[retry {i}/{len(to_run)}] {row['question_id']}: {row['question']}")
            print("=" * 80)

            reason = f"{previous['status']}: {previous.get('error', '')}"
            metadata = build_metadata(
                previous["run_id"], version.name, args.split, row,
                previous.get("attempt", 1) + 1, reason
            )
            record = run_item(row, version, metadata, out_path)
            print(f"\n--- STATUS: {record['status']} ---")

    else:
        if out_path.exists():
            raise FileExistsError(
                f"{out_path} already exists. "
                "Rename or remove it only if you intentionally want a new formal run, "
                "or use --retry-infra to rerun infrastructure failures."
            )

        total = len(questions)
        run_id = f"{version.name}-{args.split}-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        print(f"Run ID: {run_id}")
        print(f"Running {total} {SPLIT_LABELS[args.split]} questions on Version {version.name}.")
        print(f"Results will be saved to: {out_path}")

        for i, row in enumerate(questions, start=1):
            print("\n" + "=" * 80)
            print(f"[{i}/{total}] {row['question_id']}: {row['question']}")
            print("=" * 80)

            record = run_item(row, version, build_metadata(run_id, version.name, args.split, row, attempt=1), out_path)

            print(f"\n--- STATUS: {record['status']} ---")
            print("\n--- FINAL ANSWER ---")
            print(record["final_answer"])

    latest = load_latest_records(out_path)
    counts = collections.Counter(r["status"] for r in latest.values())
    print("\nFinished. Latest status per question:", dict(counts))

    infra = [q for q, r in latest.items() if r["status"] in INFRA_FAILURE_STATUSES]
    if infra:
        print(f"Infrastructure failures to retry with --retry-infra: {', '.join(infra)}")


if __name__ == "__main__":
    main()
