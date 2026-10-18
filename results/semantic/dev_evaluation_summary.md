# Version B Development Evaluation — Pre-freeze Re-run

> Run `B-dev-20261018T083414Z` (commit `7307052`) · 26 development questions · graded on 2026-10-18 with the standard in `results/evaluation-change-log.md`. Context now includes the review-attribution definition added to `03-olist-business-semantics.md` §5 (`context_hash e9099d59…`). Round 1 (`B-dev-20261014T093016Z`) is in `dev-round1/`.

| | Round 1 | Re-run |
| --- | ---: | ---: |
| Fully correct | 17/26 | 16/26 |
| Behavior pass | 24/26 | 24/26 |
| Result pass | 19/26 | 16/26 |
| Assumption transparency | 3/7 | 4/7 |

Fully correct: Q04, Q05, Q07, Q09, Q11, Q13, Q14, Q19, Q20, Q22, Q24, Q25, Q26, Q30, Q31, Q32.

## Effect of the review-attribution definition (Q17, Q18)

In this run, neither review question shows the round-1 grain error: each `review_id` is kept as its own review and attributed once to each distinct product or seller, and Q18's review counts match the reference (for example 1ca7077d… 113). This is consistent with the new definition, though a single run cannot prove cause. Neither question passes, because of the minimum review count: Q17 applies no minimum at all (the SQL only sorts and limits to 20 rows) and declares none, and Q18 declares 10, outside the frozen 20–100 range. Choosing a minimum is C7's job in Version C and is not knowledge the B context provides. The primary label moves from `wrong_grain` to `metric_definition` on both.

## Other changes from round 1

- **Q05 now passes:** purchase-year attribution is stated this time.
- **Q08 now fails:** B restricted the carrier-handoff population to valid orders, dropping 75 handed-over orders that were later canceled (97,583 vs 97,658). The average stays within tolerance, but the population is narrower than the question asks.
- **Q33 now fails:** counts are right (775 / 1), but the answer no longer says it used the raw tables without a valid-order filter (round 1 did). Required caveat missing.
- **Q02 still fails, for a different reason:** the result is correct, but the "why" carries no association caveat and the valid-order population is not stated.
- **Transparency changes:** Q01 and Q05 False → True; Q18 True → False (declared threshold out of range); net 3/7 → 4/7.

Q05, Q08 and Q33 changed with no relevant context change, so they show run-to-run variation, especially in disclosures, caveats and population choices. The total moves from 17/26 to 16/26.

## Unchanged failures

Q01 (price + freight revenue basis; Sep-2018 cutoff), Q23 (accounting caveat), Q27 (2,961 vs 2,920), Q37 and Q38 (recognise the ambiguity, then answer anyway).
