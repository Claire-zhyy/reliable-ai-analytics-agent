---
type: note
status: active
created: 2026-10-02
updated: 2026-10-02
project: job-search
tags: [type/note, status/active, topic/ai]
---

# Evaluation Methodology v1

> Fixed on 2026-10-02, before the first evaluation run. It applies identically to Versions A, B and C. Question-level criteria (expected results, accepted interpretations, required disclosures, caveats, disallowed claims) live in `04-2-benchmark-answer-key.md`; this document defines how those criteria are applied, logged and reported. The split is defined in `04-3-benchmark-split.md`.

## 1. Evaluation unit and run setup

Each benchmark question is one single-turn item. The runner opens a fresh conversation, sends the question text, lets the model call `run_sql` as needed, and records everything until the model stops. There is no simulated stakeholder reply: if the model asks a clarification question, that response is the item's final output and is graded as such.

The model receives only the question text plus the context of the version under test. It never receives the answer key, reference SQL, the metadata columns of the question files, or the evidence-bearing profiles `02-tables.md` and `02-tables-overview.md`.

All three versions use the same model identifier, temperature, base prompt structure, `run_sql` tool, DuckDB file and runner. The model identifier and temperature are written to the run log at the first development run and are not changed afterwards.

All versions may run more than one query for a question, up to the same maximum number of queries per question. This shared query limit is fixed in configuration before the first development run and recorded in the run log. Versions A and B have no repair step: if a query fails to execute, the error is recorded, the item ends, and the response is graded as an SQL execution failure. Version C may return execution errors to the model for bounded self-repair, with its retry limit fixed in configuration before the first run and recorded in the log; repair attempts count against that retry limit, not the shared query limit.

## 2. Scoring dimensions

Each response is scored on up to three dimensions, recorded separately:

- **behavior** — the response takes the expected behavior (`execute_sql`, `clarify` or `insufficient_data`). Asking for clarification on a `disclosed_assumption` question is over-clarification. Answering a `clarify` question with a final result built on one silently chosen interpretation is missed clarification.
- **result** — for `execute_sql`, the numbers are correct under the interpretation used (which must be an accepted interpretation where the answer key lists them), required caveats are present, and no disallowed claim is made. For `clarify` and `insufficient_data`, the response meets `expected_clarification` or `evaluation_rule`.
- **assumption_transparency** — `disclosed_assumption` questions only. Every item in `required_assumption_disclosure` is stated in the response text; an assumption that appears only in the SQL does not count.

A question is **fully correct** only when every applicable dimension passes. A response that passes `result` but fails `assumption_transparency` is a **silent assumption** and is reported as its own failure type.

## 3. How each question type is graded

| Expected behavior | Behavior check | Result check | Grader |
| --- | --- | --- | --- |
| `execute_sql` · `defined` | Answers without asking | Code comparison of returned values against the reference; human check of required caveats and disallowed claims | Code, then human |
| `execute_sql` · `disclosed_assumption` | Answers without asking | Code comparison against the reference for the interpretation the response declares; human check of caveats, claims and disclosure | Code, then human |
| `clarify` | Asks one focused question before any final answer | Meets `expected_clarification` | Human |
| `insufficient_data` | Declines to present an unsupported metric | Meets `evaluation_rule` | Human |

Question-specific procedures already defined in the answer key: Q17 and Q18 are graded by re-running the parameterised reference query at the minimum review count the response declares (accepted range 20–100); Q12 is graded against its rubric; the spike judgement in Q03 is checked by a human against the spike rule the response states.

Code checks run first, then human review of the response text. Where practical, human review is done with the A/B/C labels hidden, so that knowing the version does not influence judgement on disclosures, caveats or clarifications. An LLM may be used to pre-fill disclosure and caveat checklists, but the final grade is human and LLM-as-a-judge is not used for any headline number.

## 4. Result comparison rules

Results are compared on values, not SQL text, and the per-question `evaluation_rule` overrides these defaults where it is more specific.

- **Counts** must match exactly.
- **Monetary values** must match to two decimal places; values described as "approximately" in the answer key allow ±0.01.
- **Percentages and rates** must match to two decimal places after normal rounding. A fraction and its percentage form are equivalent (0.0063 = 0.63%).
- **Elapsed durations** follow the global elapsed-duration rule in the answer key: ±0.1 day, and a calendar-boundary implementation passes only if it stays within tolerance and preserves any required ordering. Day-based averages described as "approximately" (Q32) use the same ±0.1-day tolerance.
- **Rankings** have no fixed N. The rows a response returns must match the reference ranking from the top, in order, with matching values. If rows are tied at the point where the response stops, any order within the tied set is accepted.
- **Multi-row series** (monthly or yearly tables) must match every row the question requires. Extra rows outside the requested scope are acceptable if they are labelled, for example a coverage tail shown and explained.
- **Column order** never matters. **Row order** matters only where ranking or chronological order is part of the question.

## 5. Failure classification

Every response that is not fully correct receives one primary label and at most one secondary label. Labels describe the first point at which the answer went wrong.

| Label | Meaning |
| --- | --- |
| `sql_execution` | SQL fails and is not repaired. |
| `hallucinated_column` | References a table or column that does not exist. |
| `join_amplification` | A one-to-many join inflates an aggregate. |
| `wrong_grain` | Calculated at the wrong analytical grain (for example `customer_id` instead of `customer_unique_id`, review rows instead of `review_id`). |
| `population_filter` | Wrong population: valid-order default omitted or misapplied, wrong statuses included. |
| `metric_definition` | Wrong numerator, denominator or measure for the metric. |
| `date_boundary` | Wrong date field, wrong period boundary, or timestamp-versus-date comparison error. |
| `wrong_interpretation` | Numbers are right but the conclusion is not: missing required caveat, coverage tail read as a business change, causal or other disallowed claim. |
| `silent_assumption` | Result correct under an accepted interpretation, required disclosure missing. |
| `missed_clarification` | A `clarify` question answered with a silently chosen interpretation. |
| `over_clarification` | Asked for clarification on a question that should have been answered. |
| `unsupported_proxy` | An `insufficient_data` question answered with a proxy or invented metric. |
| `other` | Anything not covered above, with a note. |

## 6. Logging

Each response is logged with: run ID, timestamp, version, split, question ID, model identifier, temperature, hashes of the prompt and context files in use, the full transcript including tool calls, every generated SQL statement, execution results or errors, retry count (Version C), final answer text, observed behavior, declared interpretation or threshold where relevant, the grade on each dimension, error labels, and grader notes.

## 7. Change control during development

Only development results may drive changes. Each change is logged with its date, layer (B semantics, B data dictionary, C prompt rule, C code check, or runner), the development question IDs and error labels that triggered it, and why it is a general rule rather than a patch for one question.

Version B carries knowledge (definitions, populations, field meanings, join risks); Version C carries behavior (when to clarify, what to state, what to check). A behavioral rule is never added to the Version B context, and no dataset-derived count or benchmark answer is ever added to it.

Not allowed: editing questions, split membership or the answer key; rules written for a single question; changing grading after seeing results. New interpretations or failure types found during development are recorded as future benchmark additions, not applied retroactively.

Version C rules pre-registered before the split: check grain and key uniqueness before aggregating; prefer a direct measure over a proxy; the procedure for sequential-event customer metrics; the procedure for two-table reconciliation. Their source questions (Q31–Q33) are in development. The population rule for reconciliation sits in the Version B semantics and is not repeated in Version C.

After the last change, all 26 development questions are re-run on the final A, B and C as the pre-freeze development result.

## 8. Freeze and held-out protocol

1. Freeze prompts, context files, workflow code, runner and grader; commit and tag the repository.
2. Select the five repeatability questions and record them before the held-out run.
3. Run A, B and C once each on all 13 held-out questions.
4. Re-run an item only for an infrastructure failure that prevented a complete model response (API error, timeout, rate limit, runner crash), and log the reason. A model-output failure is never re-run.
5. Grade with this document and the answer key as frozen. After grading nothing is changed; any problem found becomes a stated limitation.
6. Run the repeatability test: the five selected questions three times each on final Version C, recording whether SQL, behavior and final answer stay consistent.

## 9. Reporting

Results are reported as counts with rates (for example 6/10), with development and held-out shown separately.

The headline is the held-out `execute_sql` set: fully-correct counts for A, B and C on its 10 questions, with `result` and `assumption_transparency` shown separately for the three disclosed-assumption questions. The four `clarify` and two `insufficient_data` questions are reported as pooled descriptive counts across both splits. Over-clarification is counted across all `execute_sql` questions in each split.

The analysis reports error-label counts by version and by stage (A→B, B→C), question-level regressions in both directions, the repeatability observations, and whether each of the two hypotheses in the project brief held.
