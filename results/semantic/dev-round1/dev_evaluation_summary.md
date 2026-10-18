# Version B Development Evaluation

> Run `B-dev-20261014T093016Z` · 26 development questions · graded on 2026-10-18 against the frozen answer key and Evaluation Methodology v1. Draft pre-filled, independently re-verified (all 23 `execute_sql` reference queries re-run read-only, Q17 at the declared 10 for diagnosis, Q18 at the declared 20), and confirmed by Claire. The grading decisions that apply to all versions are logged in `results/evaluation-change-log.md` (2026-10-18). Superseded drafts are kept in `drafts/`.

## Headline results

| | Version A | Version B |
| --- | ---: | ---: |
| Fully correct | 4/26 (15.4%) | **17/26 (65.4%)** |
| Behavior pass | 24/26 | 24/26 |
| Result pass | 4/26 | 19/26 |
| Assumption transparency | 0/7 | 3/7 |
| `execute_sql` fully correct | 3/23 | 16/23 |
| `clarify` fully correct | 0/2 | 0/2 |
| `insufficient_data` fully correct | 1/1 | 1/1 |

Fully correct in B: Q04, Q07, Q08, Q09, Q11, Q13, Q14, Q19, Q20, Q22, Q24, Q25, Q26, Q30, Q31, Q32, Q33.

Question-level change A → B: 13 questions newly fully correct, 0 regressions (A's four passes, Q08, Q09, Q19 and Q30, all hold).

## Error labels

| Primary label | A | B |
| --- | ---: | ---: |
| `population_filter` | 15 | 1 (Q27) |
| `metric_definition` | 2 | 1 (Q01) |
| `wrong_grain` | 1 | 2 (Q17, Q18) |
| `date_boundary` | 1 | 0 |
| `wrong_interpretation` | 1 | 1 (Q23) |
| `missed_clarification` | 2 | 2 (Q37, Q38) |
| `silent_assumption` | 0 | 2 (Q02, Q05) |
| `sql_execution`, `hallucinated_column`, `join_amplification`, `over_clarification` | 0 | 0 |

Secondary labels in B: `wrong_interpretation` (Q01), `metric_definition` (Q17), `other` (Q18, rounding before ranking).

## Key findings

**The A → B gain is almost entirely the population fix.** Fifteen of A's 22 failures were wrong order populations. B applies the documented valid-order statuses on every question that says "valid" and, by default, on Q01, Q02, Q05, Q11, Q13, Q14 and Q22–Q26, which is the default behaviour the Version A summary named as the main thing to watch. The single remaining population failure is Q27 (2,961 vs 2,920): the model counted payment rows with no valid-order filter. The calendar-date rule in the semantics also fixes A's Q07 date-boundary failure.

**What B gets right is mostly no longer the bottleneck.** Of B's nine failures, only Q01 (revenue taken as price + freight, which is not an accepted interpretation) and Q27 are knowledge or definition misses. The rest are procedure and behaviour:

- **Review-grain procedure (Q17, Q18).** B followed the semantics far enough to exclude ambiguous review IDs and attribute order-level reviews once per product or seller, but it collapsed distinct reviews on the same order: through `DISTINCT … review_score` in Q17 and an order-level average in Q18. Q17 also declared a 10-review minimum, below the frozen range; Q18 rounded averages before ranking.
- **Noticed but did not ask (Q37, Q38).** Both responses open by saying the term needs a definition, then pick one and give a final list. Recognising the ambiguity is not new in itself (A's Q38 also opened by naming several meanings of "underperforming"); in neither version does that recognition lead to a clarifying question, and B has no instruction to stop.
- **Disclosure and caveats (Q02, Q05, Q23, Q01 secondary).** The numbers are right, but a required disclosure or caveat is missing from the answer text. Transparency improved from 0/7 to 3/7 (Q11, Q13, Q18). Q01's transparency fails because purchase-date attribution is not clearly stated; whether the revenue basis is accepted is judged under `result`, not transparency.

## Hypothesis 1

H1 predicted that A → B gains would come mainly from fewer metric-definition, wrong-grain and join-amplification errors. On development, the mechanism holds (business semantics, not SQL ability, was the bottleneck), but the categories do not: the gain came from population (15 → 1) and date-boundary (1 → 0). Join amplification never appeared, and primary `wrong_grain` did not fall (1 → 2): A's Q17 was already `wrong_grain` (A's Q18 was `metric_definition` with secondary `wrong_grain`), and in B both review questions remain grain failures, now in how distinct reviews on one order are counted. This is a development result; the held-out run decides what is reported.

## Interpretation notes

- **Wrong grain hidden by output.** In Q17 and Q18 the review-grain errors did not change the displayed Top 10 review counts; they are failures because the answer key requires each retained `review_id` to contribute once, independently of output coincidence. Q13 is the opposite case: the query ranks raw item rows, but the evaluation rule grades the returned ranking, which matches Interpretation B exactly, so it passes with the method risk noted.
- **Model-side arithmetic persists.** In Q01 the split of the R$15.74M total into R$13.49M merchandise and R$2.24M freight was summed by the model from the yearly rows, not returned by SQL (the figures are arithmetically correct). Q02's "about 2×" is a model-side ratio. As in Version A, the database is the source of truth for queried values, but the answer text can still contain model arithmetic.
