# System Freeze Record

> Frozen on 2026-10-18 for the Day 11 held-out run (methodology §8). The tag `system-frozen-v1` is placed on the commit that adds this file.

## What is frozen

| Layer | Identifier |
| --- | --- |
| Model and settings | `gpt-5.6-terra`, reasoning effort `medium`, API-default temperature, max 5 tool rounds, 200 result rows; C repairs ≤ 2 |
| Version A instructions | `prompt_hash 7192e95c00b0…` (unchanged since the first A run) |
| Version B context | `docs/02-tables-model-context.md` + `docs/03-olist-business-semantics.md` incl. the review-attribution definition; `context_hash e9099d59b78d…`, `prompt_hash 3342ab2401cd…` |
| Version C | B context + `src/improved/rules.py` (C1–C12) + code checks in `src/improved/guardrails.py`; `prompt_hash aa536654e1c9…` |
| Runner, grader and benchmark | `src/core/`, `docs/05-evaluation-methodology.md`, answer key, reference SQL, split |
| Grading standard | `results/evaluation-change-log.md`, entries dated 2026-10-18 |

Full prompt and context hashes are recorded in every pre-freeze run log (`results/*/dev_runs.jsonl`). SHA-256 of every frozen file: `results/system-freeze-sha256.txt`.

**About `benchmark/FREEZE-SHA256.txt`:** that file is the historical snapshot from the benchmark freeze on 2026-10-02. All benchmark files still match it. `docs/03-olist-business-semantics.md` no longer matches, because the review-attribution definition was added on 2026-10-18 (logged as a pre-freeze revision). The current system is verified against `results/system-freeze-sha256.txt`, not the 2026-10-02 snapshot.

## Pre-freeze development result

A 4/26 · B 16/26 · C 19/26 fully correct (see `results/dev-comparison-abc.md`).

## Repeatability questions (methodology §8.2)

Selected before any held-out run. Each is run three times on final Version C after the held-out run, recording whether SQL, behaviour and final answer stay consistent. Development questions are used so that the repeatability test adds no held-out exposure.

| Q | Expected | Why it is included |
| --- | --- | --- |
| Q01 | execute_sql · disclosed_assumption | Revenue basis, coverage and growth window varied across runs |
| Q18 | execute_sql · disclosed_assumption | Review attribution grain, threshold choice and ranking order |
| Q23 | execute_sql · defined | Exact monthly values with a required caveat; tests caveat stability |
| Q31 | execute_sql · defined | Multi-step population, item grain and payment pre-aggregation |
| Q37 | clarify | Whether the clarification behaviour is stable |

## Held-out protocol (unchanged, methodology §8)

Run A, B and C once each on the 13 held-out questions from a clean commit carrying a `system-frozen*` tag (the runner refuses otherwise). Re-run an item only for an infrastructure failure. Grade with the frozen standard; after grading nothing is changed, and any problem found becomes a stated limitation.
