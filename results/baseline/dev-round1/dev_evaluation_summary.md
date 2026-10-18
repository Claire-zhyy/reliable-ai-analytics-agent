# Version A Development Evaluation

> Run `A-dev-20261011T123502Z` · 26 development questions · graded against the frozen answer key and Evaluation Methodology v1. Grader corrections of 2026-10-14 (Q13, Q31 labels; Q24, Q25, Q32 notes) are logged in `results/evaluation-change-log.md`.

## Headline results

- Fully correct: **4/26 (15.4%)**
- Behavior pass: **24/26 (92.3%)**
- Result pass: **4/26 (15.4%)**
- Assumption transparency: **0/7 (0.0%)**

## By expected behavior

- `execute_sql`: fully correct **3/23**
- `clarify`: fully correct **0/2**
- `insufficient_data`: fully correct **1/1**

## Primary error breakdown

- `population_filter`: **15**
- `metric_definition`: **2**
- `missed_clarification`: **2**
- `date_boundary`: **1**
- `wrong_grain`: **1**
- `wrong_interpretation`: **1**
- `join_amplification`, `hallucinated_column`, `silent_assumption`: **0**

Secondary labels: `wrong_interpretation` 3, `wrong_grain` 2 (Q13, Q18), `population_filter` 1, `sql_execution` 1 (Q37).

## Fully correct questions

- **Q08**: For orders that were handed over to the carrier, on average, how long did it take from order placement to carrier handoff?
- **Q09**: On average, how long does it take from order placement until the customer receives the order?
- **Q19**: How many order records are in the dataset?
- **Q30**: Which marketing channels generated the most valid orders?

## Key findings

Version A can usually generate executable SQL and often uses the correct analytical structure, but it is unreliable when business semantics are not explicitly available. The dominant failure mode is population definition, not SQL syntax or join mechanics. Only one response failed on SQL execution (Q37, an alias/Binder error); no response used a hallucinated column or produced join amplification; and Q31 correctly pre-aggregated payments to order level before averaging.

The 15 `population_filter` failures fall into three groups that call for different fixes. In five questions (Q04, Q20, Q22, Q31, Q32) the question explicitly said "valid", but Version A had no business definition and invented one, either delivered-only or "not canceled/unavailable" (which wrongly keeps `created`). In eight questions (Q01, Q13, Q14, Q23, Q24, Q25, Q26, Q27) the question did not say "valid" and the model applied no population filter at all. In two questions (Q05, Q11) the question did not say "valid" and the model substituted a plausible but narrower delivered-only population. The first group tests whether Version B learns what a valid order is; the second and third test whether it learns to apply the valid-order population by default when the question does not ask for it. That second question is the main thing to watch in Version B.

Several population failures have little or no effect on the business answer. In Q25 the returned Top 10 order matches the reference exactly; in Q13 the Top 10 is identical to Interpretation B; Q32 returns 80.84 days against 80.79, inside tolerance, and fails only because including `created` orders adds one repeat customer (2,888 vs 2,887). These are graded as failures because the frozen answer key requires the valid-order population, and they should be presented as method failures with limited material impact rather than as wrong business conclusions. Q24 is different: the #1 category matches, but ranks 7 and 8 are reversed.

Both development `clarify` questions failed because the model proceeded to analysis instead of asking a focused clarification. In Q37 the item ended on an SQL error before any answer was produced, but the attempted query was already a final ranking by merchandise revenue.

## Interpretation notes

**Assumption transparency.** `0/7` means no disclosed-assumption question satisfied all required disclosures under the strict rubric. It does not mean the model never states assumptions: Q01 and Q11, for example, explicitly stated the population they used, but that population was not the benchmark's valid-order population. After the Q13 correction, Version A has no case in which the result is correct and the only failure is a silent assumption.

**Run-to-run instability (descriptive only).** An earlier development run (`dev_runs_invalid_repair.jsonl`) is excluded from the formal score because the runner allowed SQL self-repair. Repair was only triggered on Q37, however, so the other 25 items are comparable responses to the same questions. Across the two runs, the inferred order population changed on seven questions (Q04, Q05, Q11, Q20, Q23, Q31, Q32). For example, Q20 answered 96,478 (valid = delivered) in the earlier run and 98,207 (valid = not canceled/unavailable) in the formal run, and in Q11, Q23 and Q31 the earlier run's guess happened to reproduce the reference values. The baseline therefore did not converge on one stable but incorrect definition of valid orders; it was guessing business semantics rather than applying a fixed rule. This is descriptive evidence from a non-scored duplicate run, not a formal repeatability experiment, and it means the 4/26 figure carries some run-to-run noise.

**Hypothesis 1.** The development results are directionally consistent with H1's underlying mechanism: business semantics, rather than basic SQL generation, were the main bottleneck. The predicted error categories were not accurate, however. H1 expected metric-definition, wrong-grain and join-amplification errors to dominate; population-definition failures dominated instead, and join amplification did not appear. H1 is not revised; this will be reported as stated.

**Model-side arithmetic.** In Q20 the SQL returned only status counts, and the final figure of 98,207 was computed by the model while writing the answer. The system should therefore not be described as "the LLM only writes SQL and the database does all calculations". The database is the source of truth for queried data, but the model can still perform arithmetic and interpretation during answer synthesis, which is an additional reliability surface.
