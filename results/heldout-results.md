# Held-out Results (Day 11)

> Runs `A-heldout-20261018T091126Z`, `B-heldout-20261018T091335Z`, `C-heldout-20261018T091457Z` on the frozen commit `4260d21` (tag `system-frozen-v1`); each version ran once on the 13 held-out questions, with no re-runs. Graded on 2026-10-18 against the frozen answer key and grading standard, independently re-verified (round 4: all 39 grades checked, held-out reference SQL re-run read-only, freeze manifest 34/34 files verified), and confirmed by Claire. Grades: `results/{baseline,semantic,improved}/heldout_evaluation.csv`. After this grading nothing in the system or grading is changed; problems found become stated limitations.

## Headline: held-out `execute_sql` (10 questions)

| | A | B | C |
| --- | ---: | ---: | ---: |
| **Fully correct, execute_sql** | **2/10** | **5/10** | **4/10** |
| Fully correct, all 13 | 2/13 | 7/13 | 7/13 |
| `clarify` (Q06, Q39) | 0/2 | 1/2 | 2/2 |
| `insufficient_data` (Q15) | 0/1 | 1/1 | 1/1 |
| Assumption transparency (Q03, Q12, Q16) | 2/3 | 1/3 | 3/3 |
| Behavior pass | 10/13 | 12/13 | 13/13 |
| SQL errors ending the item | 0 | 2 (Q03, Q12) | 0 (Q03 repaired) |

**Pooled descriptive counts (development re-run + held-out):** `clarify` A 0/4, B 1/4, C 3/4; `insufficient_data` A 1/2, B 2/2, C 2/2.

## Question-level table

| Q | Expected | A | B | C |
| --- | --- | --- | --- | --- |
| Q03 | execute_sql | ✗ metric_definition | ✗ sql_execution | ✗ metric_definition |
| Q06 | clarify | ✗ missed_clarification | ✓ | ✓ |
| Q10 | execute_sql | ✗ population_filter | ✓ | ✓ |
| Q12 | execute_sql | ✗ wrong_interpretation | ✗ sql_execution | ✗ wrong_interpretation |
| Q15 | insufficient_data | ✗ unsupported_proxy | ✓ | ✓ |
| Q16 | execute_sql | ✗ wrong_interpretation | ✗ wrong_interpretation | ✗ wrong_interpretation |
| Q21 | execute_sql | ✗ population_filter | ✓ | ✓ |
| Q28 | execute_sql | ✗ population_filter | ✗ other | ✗ date_boundary |
| Q29 | execute_sql | ✗ population_filter | ✓ | ✓ |
| Q34 | execute_sql | ✓ | ✓ | ✗ metric_definition |
| Q35 | execute_sql | ✓ | ✓ | ✓ |
| Q36 | execute_sql | ✗ date_boundary / wrong_grain | ✗ wrong_grain / wrong_interpretation | ✗ population_filter |
| Q39 | clarify | ✗ missed_clarification | ✗ missed_clarification | ✓ |

## What the held-out set shows

**A → B generalises.** B gets 5/10 `execute_sql` questions fully correct against A's 2/10. Four of A's eight `execute_sql` failures are the valid-order population again (Q10, Q21, Q28, Q29). B gets the population right on all four; three pass fully, and Q28 fails only because the percentage is reported as 20.6% instead of 20.63%. This is the same mechanism as on development: business definitions, not SQL ability, were the bottleneck.

**B → C does not add `execute_sql` accuracy.** C scores 4/10 against B's 5/10. It fixes none of the `execute_sql` questions B failed (Q03, Q12, Q16, Q28, Q36), and Q34 moves from pass to fail. Q28 fails in both, for different reasons. C's gains are elsewhere: both held-out `clarify` questions (Q06, Q39; B 1/2), full assumption transparency (3/3; B 1/3), and no item lost to an SQL error. Three C failures are consistent with rules being applied outside the situations they were written for:

- **Q34:** C imposed a 100-order minimum on a state ranking, removing the two slowest states. This matches C7 (minimum sample for average-based rankings), applied where the answer key says no threshold is needed.
- **Q28:** C built a "like-for-like" Jan–Sep comparison (+99.8%) instead of reporting the verified change (+9,156, +20.63%) with a caveat, and its window includes a full September 2017 but only residual September 2018 records. This is consistent with C8 (coverage check) and repeats the development Q01 cutoff error.
- **Q36:** C excluded review IDs linked to several orders from a review-year average, where the key says they must be kept. This matches applying the review-attribution definition added before freeze outside its product/seller scope. B did not exclude them but failed on a different grain error.

These are interpretations of single runs, not tested causes.

**A held-out repair case.** B and C hit the same DuckDB `generate_series` cast error on Q03. B stopped with no answer; C repaired the query in one round and completed. C still fails Q03, on its spike rule, so the repair saved the answer but not the grade. (Development had one earlier repair, C Q01.)

**Failures shared across versions:** Q16's required caveat (the data does not record who initiated a cancellation) in all three, and spike detection on raw counts rather than rates (Q03, A and C).

## Hypotheses (held-out)

- **H1** (A → B mainly from fewer metric-definition, wrong-grain and join-amplification errors): the A → B gain holds on held-out and again comes from population definition, not from the predicted categories. Join amplification did not occur.
- **H2** (B → C mainly from ambiguous questions and execution errors): partly supported. Clarification improved (`clarify` 2/2 vs 1/2) and every item produced an answer (the Q03 repair), but `execute_sql` accuracy did not improve: C 4/10 vs B 5/10.

## Grading notes

- **C Q12** fails only on the rubric's "reports sample sizes for compared groups": n is given for states and the distance-eligible total, not per distance, weight, volume, period or weekday band.
- **C Q06** passes: merchandise sales is offered as a default option inside the clarification, not presented as the measure of competitiveness.
- **B Q28** fails on reporting precision (20.6% vs 20.63%); methodology §4 has no exception for lower displayed precision.

## Small-sample warning

Ten `execute_sql` questions: one question is 10 percentage points. B's 5/10 versus C's 4/10 is a one-question difference in a single run per version, and development re-runs moved individual items by one or two. The observation from this run is that C did not improve result accuracy over B, while it did improve clarification, disclosure and answer completion. The size of the gap is not a stable estimate.

## Next

Repeatability test (Q01, Q18, Q23, Q31, Q37 on Version C, three runs each), then the final report.
