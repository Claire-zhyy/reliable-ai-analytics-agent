# Version C Development Evaluation — Pre-freeze Re-run

> Run `C-dev-20261018T083658Z` (commit `7307052`) · 26 development questions · graded on 2026-10-18 with the standard in `results/evaluation-change-log.md`. Context includes the new review-attribution definition (`context_hash e9099d59…`); prompt rules and code checks are unchanged. Round 1 (`C-dev-20261014T093341Z`) is in `dev-round1/`.

| | Round 1 | Re-run |
| --- | ---: | ---: |
| Fully correct | 20/26 | 19/26 |
| Behavior pass | 24/26 | **26/26** |
| Result pass | 20/26 | 19/26 |
| Assumption transparency | 5/7 | **7/7** |
| Over-clarification | 2 | **0** |

Fully correct: Q02, Q04, Q05, Q07, Q08, Q09, Q11, Q13, Q14, Q19, Q20, Q22, Q25, Q26, Q30, Q31, Q32, Q33, Q37.

## Effect of the review-attribution definition (Q17, Q18)

No over-clarification occurred in this run. Both questions run SQL at the right grain, declare a 30-review minimum (inside the accepted range) and state the attribution. This is consistent with the round-1 reading that a missing attribution definition, not C1 alone, made the questions look ambiguous; a single run cannot prove it. Neither passes:

- **Q17:** the Top 10, review counts and averages match the canonical n ≥ 30 reference exactly. It fails only on the required caveat that a minimum review count does not establish statistical significance.
- **Q18:** counts are right, but averages are rounded to 2 dp before sorting, which reverses ranks 5–6 and 7–8, the same rounding-before-ranking failure as B in round 1. The causation caveat is also missing.

## Code checks

For the first time, a code-level check fired. In Q01, the pre-execution schema check rejected a query that referenced a column alias not available in scope, and C's bounded repair fixed it in one round (1 repair; 0 warnings across all items). The item still fails on the growth window. Without the pre-check, the error would have surfaced at execution and also been returned for repair, so this shows the check and repair path working, not a grade it changed. Across both C runs, this is the only corrective event from the code-level checks.

## Other changes from round 1

- **Q01** now uses an accepted basis (merchandise value; full-year 2017 6,108,492.27 matches) but still compares Jan 1–Sep 3 in both years. Because September 2018 contains only residual records at the extraction cutoff, the window includes real 2017 September sales but no comparable 2018 sales, giving +132.67% instead of the reference like-for-like +138.28%. Primary label `date_boundary`.

- **Q24 now fails:** the category ranking and sales values are correct, but the answer table reports 4,325 orders for Garden Tools where the SQL returned 3,505. Counts in the answer must match exactly.

## Unchanged failures

Q23 (accounting caveat), Q27 (2,961 vs 2,920), Q38 (asks which measure, not which comparison baseline).
