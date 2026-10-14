## 2026-10-11 — Runner correction

- Layer: runner
- Trigger: Q37 in the first Version A development dry run produced an SQL execution error, but the runner returned the error to the model and allowed it to repair the SQL.
- Change: Version A now terminates the item immediately on the first SQL execution error. The error is logged but is not returned to the model for repair.
- Reason: This restores the pre-registered Evaluation Methodology v1. Version A and B do not use self-repair; bounded self-repair is reserved for Version C.
- Scope: General runner behavior, not a question-specific rule.
- Previous run: retained as `dev_runs_invalid_repair.jsonl` and excluded from formal evaluation.

## 2026-10-14 — Grader corrections (Version A development)

- Layer: grader (application of the frozen answer key; no question, split, answer-key entry or methodology rule changed)
- Run: `A-dev-20261011T123502Z`
- Q13: `result_pass` True → False; primary `silent_assumption` → `population_filter`; secondary none → `wrong_grain`. Reason: the response used all order statuses and ranked raw `order_items` rows without aggregating to `product_id`. Its Top 10 is identical to Interpretation B, but Q05, Q11 and Q25 were failed for the same population issue even where their rankings matched, so Q13 is graded on the same principle. Primary is `population_filter` because the row-level ordering did not change the output in this response (it is equivalent to a MAX-price ranking until a product repeats, first at row 17); the grain issue is recorded as secondary.
- Q31: secondary `wrong_interpretation` removed. The missing caveat concerns reconstructing payment as price + freight, which the response did not do; the result already fails on population.
- Q24, Q25, Q32: grader notes clarified only (Q24 ranks 7–8 reversed; Q25 Top 10 order identical to reference; Q32 near miss within tolerance).
- Effect: result pass 5/26 → 4/26; fully correct unchanged at 4/26; primary `population_filter` 14 → 15; `silent_assumption` 1 → 0. Summary updated accordingly.

## 2026-10-14 — Runner configuration record (documentation only)

- Layer: runner
- The formal Version A development run used: model `gpt-5.6-terra`, reasoning effort `medium`, temperature API default, a maximum of **5 tool-calling rounds** per question, and at most 200 result rows returned to the model per query.
- The limit is on model rounds, not on SQL queries: one round can contain several `run_sql` calls (Q38 issued 8 queries). Methodology §1 refers to a shared "query limit"; the implemented and recorded limit is 5 rounds, and the same limit applies to Versions B and C.
- Version A context fingerprints (same algorithm as the new `prompt_hash` / `schema_hash` log fields): prompt `7192e95c00b0ea41e65ce861539f7c1269009f0ce7442a6cadd4b718e451a91e`, schema `c2e24fc13a727456485d866f34378076edf0d3b69e55478b5b948322215ed13d`.
- The exact runner code used for that run is retained in `results/baseline/runner_snapshot_A-dev-20261011T123502Z/` with SHA-256 hashes.

## 2026-10-14 — Runner robustness and logging (no model-visible change)

- Layer: runner
- Trigger: code review before Version B/C. Not triggered by any question result.
- Change: each item now ends with a logged status instead of an exception: `completed`, `sql_execution_error`, `max_rounds_exceeded`, `unknown_tool_call`, `api_error`, `runner_error`. The batch continues to the next question. `max_rounds_exceeded` and `unknown_tool_call` are model failures and are graded normally; `api_error` and `runner_error` are infrastructure failures, eligible for one logged rerun under methodology §8.4 (`run_all_dev.py --retry-infra`).
- Change: new log fields: `git_commit`, `git_dirty`, `model`, `temperature`, `reasoning_effort`, `max_tool_rounds`, `tool_rounds_used`, `query_count`, `max_result_rows`, `result_truncated` (overall and per query), `prompt_hash`, `schema_hash`, `context_hash` (null for Version A, which has no context files), and `response_ids`.
- Model-visible behavior is unchanged: same instructions text, tool schema, model, reasoning effort, 5-round limit, 200-row cap and SQL-error termination for A/B. Truncation is recorded in the trace only and is not added to the tool output. The tool output string was checked to be identical to the previous implementation on test queries, including error and truncated cases.
- Version A is not re-run.
