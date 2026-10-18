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

## 2026-10-14 — Day 9: Version B and Version C built (before any B or C run)

- Layers: runner, B context, C prompt rules, C code checks. No question, split, answer-key entry or grading rule changed.
- **Runner refactor.** One shared loop (`src/core/agent.py`) and one shared runner (`python -m src.core.runner --version A|B|C`) for all versions. Outputs go to `results/{baseline,semantic,improved}/{dev,heldout}_runs.jsonl`. Version A's model-visible requests were checked to be identical to the A snapshot in six scenarios (normal, truncated result, SQL error, round limit, unknown tool, API error), and A's `prompt_hash` is unchanged (`7192e95c…`). `src/baseline/agent.py`, `db.py` and `run_all_dev.py` remain as thin wrappers.
- **Version B** (`src/semantic/`). Version A plus `docs/02-tables-model-context.md` and `docs/03-olist-business-semantics.md`, inserted verbatim with YAML frontmatter removed. The context statement line changes from "The only database context available to you is the raw schema below" to "…the raw schema below, followed by the data dictionary and business semantics written by the analytics team"; the rest of the base prompt is unchanged. No workflow change: SQL errors still end the item and no code checks run. `context_hash` `709a2e6c76ba00dc53b59d14f4bc8accd027016f60922f3acdc899a88dbc9525`; `prompt_hash` `c8c5565d0c7b6a49a8de7d3c31b60a22d9bce7879d4a5772da2ddc4df9ae7400`. The context files are the versions locked on 2026-10-02 and are not edited before the first B run (see `results/error-analysis.md`). Note: `03` §7 mentions "the existing benchmark questions"; it is left as frozen text.
- **Version C** (`src/improved/`). Version B plus 12 prompt-level rules (`src/improved/rules.py`) and code-level checks. `prompt_hash` `58c5287ad3894d6dad9bd26a686a60da8082054f97ae8d93ce388aa181d761aa`.
  - From the project brief §4: C1 clarify only when genuinely ambiguous, C2 state analytical choices in the answer text, C11 name missing data instead of using a proxy, C12 act on tool errors and warnings.
  - Pre-registered in methodology §7: C3 grain and key uniqueness before aggregating, C4 direct measure over proxy, C5 sequential-event procedure, C6 two-table reconciliation procedure.
  - Development-driven, from Version A failures: C7 minimum sample for average-based rankings (Q18, `metric_definition`); C8 coverage check before period comparison (Q01, `wrong_interpretation`); C9 associations, not causes (Q02, Q18 caveats); C10 compute reported numbers in SQL (Q20, model-side arithmetic). Each is a general analytical behaviour, contains no benchmark wording and no dataset-derived number.
  - C1's wording and examples come only from the development clarify failures (Q37, composite evaluative term; Q38, missing comparison baseline). The held-out ambiguity types described in `04-3-benchmark-split.md` §3 were deliberately not used as examples.
  - Not included in C: the population rule for reconciliation, which methodology §7 places in the Version B semantics, although the sprint plan's Day 9 list includes it; and a control-total check from the sprint plan, which would need dataset-derived totals in the model context or question-specific logic. The join fan-out check below targets the same failure mechanism directly.
  - Code checks: (1) pre-execution schema validation (parse, then bind with `EXPLAIN` against the real catalog); a rejected query is returned to the model as an error. (2) Bounded self-repair: **MAX_REPAIRS = 2** SQL errors per question are returned to the model; a third error ends the item as `sql_execution_error`; repair rounds do not count against the 5-round limit (methodology §1). (3) Join fan-out: for query blocks over base tables that sum, average or pass on a numeric measure, the program compares `COUNT(*)` with `COUNT(DISTINCT primary key)` of that table over the same FROM / JOIN / WHERE. (4) Duplicate entity in a ranked result (ORDER BY + LIMIT, first `*_id` column). Warnings are appended to the tool output; all check details are logged in the trace.
  - Checks validated on Version A's 94 logged queries (both runs): they flagged the review-score weighting in Q17 and Q38 (true positives), rejected Q37's alias error before execution, and raised no warning on any other query. Known limits: blocks that read from CTEs or subqueries are not checked, `SELECT DISTINCT` blocks are skipped, and `COUNT(*)` is not checked.
- **Held-out guard.** `--split heldout` is refused unless there are no uncommitted changes outside `results/` and HEAD carries a tag starting with `system-frozen`.
- Also added: `requirements.txt` (adds `sqlglot==30.22.0`), `docs/06-human-in-the-loop.md`, `README.md`, `src/core/show_prompt.py` (prints a version's exact instructions and hashes).
- Testing: simulated-API tests for every item status, repair accounting and warning delivery, the batch runner and the held-out guard, on Python 3.9 with the pinned packages. No real API call was made in testing.

## 2026-10-14 — Aborted Version B start (database lock) and runner preflight

- Layer: runner (infrastructure; no model-visible change)
- Event: the first Version B development run (`B-dev-20261014T091438Z`, commit `e702519`) failed on all 26 items with `runner_error` before any model call. DBeaver held a lock on `data/olist.duckdb`, so the runner could not open the database. No response ID was recorded for any item. The Version C run did not start (same lock at import).
- Handling: no model output exists, so this is not treated as a Version B run, and `--retry-infra` was not used. The file is retained as `results/semantic/dev_runs_aborted_db_lock_20261014T091438Z.jsonl` and excluded from evaluation. The formal Version B run starts fresh with a new run ID.
- Change: the runner now opens the database once before loading a version or writing any result (`preflight_database`). If it cannot, it stops with a message and writes nothing.

## 2026-10-18 — Grading decisions applied from Version B onward

- Layer: grader (application of the frozen answer key and methodology; no question, split, answer-key entry or methodology rule changed). Decided while grading Version B development, before any Version C grade was assigned, and applied identically to C.
- **Ranking order is strict.** Rows must match "in order, with matching values" (§4). Values that are equal only after the response's own rounding are not a tie (Q18: 3.0250 vs 3.0274 reversed → fail).
- **A missing required caveat fails `result`**, even when every number matches, and is labelled `wrong_interpretation` (Q23, consistent with A's Q23 secondary label).
- **Disclosure is read from the answer text only.** A population or attribution applied correctly in the SQL but not stated in the response fails `assumption_transparency` (Q02, Q05 → `silent_assumption`).
- **Rankings are graded on returned values.** A query that reaches the reference output through a different but equivalent-for-this-output mechanism passes, with the method risk in the notes (Q13). This does not apply where the answer key prescribes the computation explicitly.
- **Review questions (Q17, Q18): each retained `review_id` must contribute once.** Collapsing distinct reviews on one order (via `DISTINCT … review_score` or an order-level average) is `wrong_grain`, even if the displayed Top N is unchanged.
- Version B grading: draft pre-filled, independently re-verified (all 23 `execute_sql` reference queries re-run read-only), corrections adopted (Q17/Q18 primary `wrong_grain`; Q01 secondary `wrong_interpretation`). Result: fully correct 17/26. Drafts retained in `results/semantic/drafts/`.

## 2026-10-18 — Version C development graded

- Run `C-dev-20261014T093341Z`, graded with the 2026-10-18 standard above. Fully correct 20/26 (strict; Q38 marked REVIEW). No code check fired on any item (0 warnings, 0 SQL errors, 0 repairs). Over-clarification on Q17 and Q18.
- A/B/C development comparison written to `results/dev-comparison-abc.md`. No context, rule, code or answer-key change has been made since the runs.

## 2026-10-18 — Round-2 verification applied; Q38 decided

- Q38 (Version C): graded strictly, behavior pass, result fail (`other`); C fully correct 20/26. Rule: "asks one focused clarification about the comparison baseline"; the response asks which measure to use.
- Transparency standard clarified (no grade changed): `assumption_transparency` checks only whether each required disclosure is stated in the answer text; whether the stated basis is acceptable is judged under `result`. C Q01 = True (basis, population and purchase date stated); B Q01 = False (purchase-date attribution not clearly stated).
- Summaries and the A/B/C comparison revised after independent round-2 verification: causal language softened to "consistent with" (single runs, no rule-level ablation); code checks described as run without warnings rather than not run; Q27 and Q17/Q18 mechanisms presented as possible explanations; Q01 corrected (A used an accepted basis); transparency changes listed in full (Q01, Q02, Q05 up; Q18 down; net +2); H2 restated as partly supported on clarification, execution repair untested.
- No context, prompt, code, answer-key or split change.

## 2026-10-18 — B semantics: review attribution rule (pre-freeze revision)

- Layer: **B semantics** (`docs/03-olist-business-semantics.md` §5, new subsection "Review attribution to products and sellers"). Inherited by Version C. Version A is unchanged.
- Trigger (development only): Q17 and Q18. In B both failed as `wrong_grain` (distinct reviews on one order merged, by `DISTINCT … review_score` in Q17 and by an order-level average in Q18). In C both failed as `over_clarification`: the model asked how order-level reviews should be attributed. `02-tables-model-context.md` says product- or seller-level review analysis needs a defined attribution grain, but neither context file stated one.
- Change: defines the attribution as knowledge, not behaviour: use `review_id`s linked to exactly one order; treat each retained `review_id` as one review (no merging by order or score); attribute each review once to each distinct product or seller in its order; review attribution is an association.
- Why it is general and allowed under methodology §7: it is a definition of attribution grain for any product- or seller-level review analysis, which §7 places in Version B ("definitions, populations, field meanings, join risks"). It contains no dataset-derived count, no threshold, no benchmark answer and no question wording. The minimum-review threshold is deliberately not added (C7 already asks for a stated minimum; the accepted range is an answer-key rule).
- Held-out risk: the split file shows Q17 and Q18 are in development; held-out also contains review-grain questions, so the rule may generalise to them. It was derived only from the observed development failures; held-out answer-key entries were not consulted.
- Not changed, reported as limitations: Q01 (revenue basis; the accepted-interpretation list is not written into the context), Q23 (commercial-vs-accounting caveat), Q27 (scope boundary of the raw-table rule).
- The Obsidian design copy (`10_Projects/job-search/ai-preparation/03-olist-business-semantics.md`) is updated to the same text.
- Context hashes change for B and C; the new `context_hash` and `prompt_hash` values are recorded in the re-run logs.
- **Re-run.** Per methodology §7, all 26 development questions are re-run on A, B and C. The first-round runs, grades and summaries move to `results/{baseline,semantic,improved}/dev-round1/` and `results/dev-comparison-abc-round1.md` (B drafts in `results/semantic/dev-round1/drafts/`) so the runner can write fresh `dev_runs.jsonl` files. Earlier change-log entries that cite `results/<dir>/dev_runs.jsonl` or `dev_evaluation.csv` refer to the files now under `dev-round1/`. Version A's re-run has an unchanged prompt and also serves as a descriptive repeatability observation.

## 2026-10-18 — Pre-freeze development re-run graded

- Runs on commit `7307052`: `A-dev-20261018T083037Z` (25 completed, 1 `sql_execution_error`), `B-dev-20261018T083414Z` and `C-dev-20261018T083658Z` (26 completed each). A's `prompt_hash` is unchanged (`7192e95c…`); B and C carry the new `context_hash` (`e9099d59…`). `git_dirty` is True only because the new run files were untracked while running.
- Graded with the 2026-10-18 standard; no new grading decision was needed. Fully correct: A 4/26, B 17/26, C 20/26 (same totals as round 1). Over-clarification 0. One C repair (Q01, schema-check rejection repaired).
- Effect of the review-attribution definition: Q17/Q18 grain errors (B) and over-clarifications (C) no longer occur; both still fail on threshold choice (B) or caveats and rounding before ranking (C). No further system change is made before freeze.
- These are the pre-freeze development results required by methodology §7.

## 2026-10-18 — Round-3 verification applied; system frozen

- Two grades corrected after independent round-3 verification (no system change, no re-run):
  - **B Q08** → result fail, `population_filter`: B restricted the observed carrier-handoff population to valid orders (97,583 vs 97,658). An average within tolerance does not excuse a narrowed population.
  - **C Q24** → result fail, `other`: the answer table reports 4,325 orders for Garden Tools where the SQL returned 3,505. Methodology §4, counts must match exactly; supplementary figures in the answer are not exempt.
- Label and note fixes: B Q02 secondary `silent_assumption` removed (that label requires a result pass); B Q18 secondary `wrong_interpretation` added (caveat omits delivery/platform experience); B Q17 note corrected (no minimum review count is applied at all).
- Re-run totals: A 4/26, B 16/26, C 19/26. A → B: 13 fixes, 1 regression (Q08). B → C: 4 fixes (Q02, Q08, Q33, Q37), 1 regression (Q24).
- Wording: Q17/Q18 changes are described as consistent with the review-attribution definition, not proven by it; the C Q01 code-check event is described as a schema-check rejection repaired by C's repair path, not as preventing termination.
- Repeatability questions selected before the held-out run: Q01, Q18, Q23, Q31, Q37 (Version C, three runs each, after held-out).
- `benchmark/FREEZE-SHA256.txt` is the 2026-10-02 benchmark snapshot; all benchmark files still match it, and only `docs/03` differs, by the logged revision. The system freeze manifest is `results/system-freeze-sha256.txt`; freeze summary in `results/system-freeze-record.md`. Tag: `system-frozen-v1`.
