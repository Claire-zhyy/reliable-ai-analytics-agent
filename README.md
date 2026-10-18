# Reliable AI Analytics Agent

An evaluation case study: how reliably can an LLM answer business questions over a multi-table database, which analytical errors does it make, and how much do business context and workflow controls each improve reliability?

Three versions are compared on the same benchmark, model, tool and database:

| Version | What it adds | Code |
| --- | --- | --- |
| A — Raw schema | Database schema and a `run_sql` tool only | `src/baseline/` |
| B — Business semantics | A + data dictionary and business-semantics documents | `src/semantic/` |
| C — Workflow controls | B + prompt-level workflow rules and code-level checks (schema validation, bounded self-repair, join fan-out and duplicate-entity checks) | `src/improved/` |

All three run through one shared loop and runner (`src/core/`), so the only difference between versions is the layer under test.

> Held-out set locked on 2026-10-02 (benchmark v4, tag `benchmark-v4-frozen`). The 13 held-out questions were not used for tuning and are run once on all three versions after the system freeze.

## Results

| Held-out, fully correct (`execute_sql`, 10 questions) | A — raw schema | B — + business semantics | C — + workflow controls |
| --- | ---: | ---: | ---: |
| | 2/10 | 6/10 | 4/10 |

Business definitions, not SQL ability, were the bottleneck. Workflow controls improved clarification, disclosure and error recovery but did not raise result accuracy on unseen questions. See [`results/final-report.md`](results/final-report.md).

## Repository layout

- `benchmark/`: 39 questions (26 development / 13 held-out), answer key, reference SQL, split and freeze hashes
- `docs/`: model context (`02`, `03`), evaluation methodology (`05`), human-in-the-loop points (`06`)
- `src/core/`: shared database access, tool-calling loop, runner
- `src/baseline/`, `src/semantic/`, `src/improved/`: Version A, B and C definitions
- `results/`: run logs, grading, error analysis and the evaluation change log

### What is in `results/`

| Path | Status |
| --- | --- |
| `final-report.md`, `heldout-results.md`, `dev-comparison-abc.md`, `repeatability-results.md` | Final write-ups |
| `{baseline,semantic,improved}/heldout_*` | Official held-out runs and grades (frozen system, one run per version) |
| `{baseline,semantic,improved}/dev_*` | Pre-freeze development re-run and grades |
| `improved/repeatability_runs.jsonl` | Repeatability test (5 questions × 3 runs on Version C) |
| `*/dev-round1/`, `dev-comparison-abc-round1.md` | Development round 1, kept for comparison (superseded by the re-run) |
| `semantic/dev-round1/drafts/` | Grading drafts before independent verification |
| `baseline/dev_runs_invalid_repair.jsonl`, `semantic/dev_runs_aborted_db_lock_*.jsonl` | Invalid or aborted runs, excluded from scoring and kept as evidence (see change log) |
| `baseline/runner_snapshot_*/` | Exact runner code used for the first Version A run |
| `evaluation-change-log.md` | Every change to runner, context, rules and grading, with reasons |
| `system-freeze-record.md`, `system-freeze-sha256.txt` | What was frozen for the held-out run |

## Running

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# .env must contain OPENAI_API_KEY; data/olist.duckdb is built by src/load_data.py

python -m src.core.runner --version B                # development questions
python -m src.core.runner --version B --retry-infra  # rerun API/runner failures only
python -m src.core.show_prompt --version C           # print the exact instructions a version uses
```

Held-out questions run only from a clean commit tagged `system-frozen*`; the runner refuses otherwise.
