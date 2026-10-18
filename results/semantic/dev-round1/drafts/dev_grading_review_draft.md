# Version B Development Grading — Draft for Review

> Run `B-dev-20261014T093016Z` · 26 development questions · pre-filled 2026-10-18 against the frozen answer key and Evaluation Methodology v1. **Draft: not a final grade.** Every row in `dev_evaluation_draft.csv` needs human confirmation (methodology §3); the five items marked REVIEW are judgement calls. Q18 was checked by re-running the parameterised reference query at the declared threshold (n >= 20). All other numeric checks compare the logged query results with the answer key.

## Draft headline (strict reading)

| | Version A | Version B (draft) |
| --- | ---: | ---: |
| Fully correct | 4/26 | **17/26** |
| Behavior pass | 24/26 | 24/26 |
| Result pass | 4/26 | 19/26 |
| Assumption transparency | 0/7 | 3/7 |
| `execute_sql` fully correct | 3/23 | 16/23 |
| `clarify` fully correct | 0/2 | 0/2 |
| `insufficient_data` fully correct | 1/1 | 1/1 |

Draft primary labels for B: `missed_clarification` 2 (Q37, Q38), `silent_assumption` 2 (Q02, Q05), `metric_definition` 2 (Q01, Q17), `population_filter` 1 (Q27), `wrong_interpretation` 1 (Q23), `other` 1 (Q18). No `sql_execution`, `hallucinated_column`, `join_amplification` or `date_boundary`.

Regressions A → B: none. All four questions A got fully correct (Q08, Q09, Q19, Q30) are also correct in B.

## Items that need your decision

1. **Q18 — ranks 9–10 reversed by rounding.** Ranks 1–8 match the n >= 20 reference exactly. The model rounded averages to 2 dp before sorting, so 3.0274 and 3.0250 both became 3.03 and the tie was broken by review count. Methodology §4 says rows must match "in order"; drafted as a result fail (`other`). If you treat values equal at the displayed precision as tied, it passes and B becomes 18/26.
2. **Q23 — numbers perfect, caveat missing.** All 12 months match exactly; the only gap is the required "not accounting revenue recognition" caveat. Under the answer key that fails `result` (`wrong_interpretation`), which is how A's Q23 secondary label was applied. Keep it strict?
3. **Q02 and Q05 — partial disclosure.** Results are correct. Q02 does not say that the headline total uses valid orders (it only mentions valid orders for the comparison average); Q05 does not state purchase-year attribution. Drafted strictly as `silent_assumption`, matching A's 0/7 standard. If you accept them, transparency goes to 5/7 and fully correct goes up by two.
4. **Q13 — right output, row-level method.** Population is fixed and the Top 10 is identical to Interpretation B, but the query still ranks raw `order_items` rows rather than aggregating to `product_id` (the same mechanism recorded as A's secondary `wrong_grain`). Drafted as a pass because the evaluation rule grades the returned ranking; the method issue is noted. Confirm, or record it as a secondary label.

Leniency range: 17/26 if you keep all strict calls, up to 21/26 if all four go the other way.

## What the draft suggests (for the Day 10 write-up, not final)

The A → B gain is almost entirely the population fix. A had 15 `population_filter` failures; B has one, Q27, where the question does not say "valid" and the model grouped all payment rows (2,961 vs 2,920). B applied the default population correctly on Q24, Q25 and Q26, so its one miss is on the payment table. Q07's date-boundary failure is also fixed by the calendar-date rule in the semantics.

The remaining B failures are mostly not knowledge gaps. Q37 and Q38 show a new pattern: B notices the ambiguity ("needs a criterion", "needs a defined KPI") and then answers anyway. That is the behaviour C1 targets. Q17 (threshold 10) and Q18 (rounding before ranking) are analytical-procedure failures, which is where C7 and C10 apply. Q01 is still the only true metric-definition miss: B defined revenue as price + freight, which is not an accepted interpretation.

For H1: the A → B change is driven by population and date semantics, not by join amplification or wrong grain. That fits the Version A finding that H1's predicted error categories were off even though its mechanism was right.

## Not yet done

- Human confirmation of every row, blind to version where practical (methodology §3).
- Version C grading (`results/improved/dev_runs.jsonl`, run `C-dev-20261014T093341Z`).
- A/B/C question-level comparison table and stage-by-stage label counts.
