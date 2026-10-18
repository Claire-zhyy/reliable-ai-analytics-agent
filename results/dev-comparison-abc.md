# A / B / C Development Comparison (Day 10)

> Development set only (26 questions). These are tuning-set results with the usual caveat: they are the "practice book" score, not the held-out result. Grades: `results/{baseline,semantic,improved}/dev_evaluation.csv`. Grading standard: `results/evaluation-change-log.md` (2026-10-18). Graded on 2026-10-18.

## Scores

| | A — raw schema | B — + business semantics | C — + workflow controls |
| --- | ---: | ---: | ---: |
| Fully correct | 4/26 | 17/26 | 20/26 |
| `execute_sql` fully correct | 3/23 | 16/23 | 18/23 |
| `clarify` (pooled later with held-out) | 0/2 | 0/2 | 1/2 |
| `insufficient_data` | 1/1 | 1/1 | 1/1 |
| Assumption transparency | 0/7 | 3/7 | 5/7 |
| Over-clarification | 0 | 0 | 2 |

Question-level movement: A → B fixes 13 questions with 0 regressions; B → C fixes 3 (Q02, Q05, Q37) with 0 fully-correct regressions. Q17 and Q18 change failure type in C (`wrong_grain` → `over_clarification`), so behavior regresses on those two items even though neither was correct in B.

## Question-level table

Primary / secondary label shown for failures.

| Q | Expected | A | B | C | Change |
| --- | --- | --- | --- | --- | --- |
| Q01 | execute_sql | ✗ population_filter / wrong_interpretation | ✗ metric_definition / wrong_interpretation | ✗ metric_definition / wrong_interpretation |  |
| Q02 | execute_sql | ✗ metric_definition / population_filter | ✗ silent_assumption | ✓ | B→C fixed |
| Q04 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q05 | execute_sql | ✗ population_filter | ✗ silent_assumption | ✓ | B→C fixed |
| Q07 | execute_sql | ✗ date_boundary | ✓ | ✓ | A→B fixed |
| Q08 | execute_sql | ✓ | ✓ | ✓ |  |
| Q09 | execute_sql | ✓ | ✓ | ✓ |  |
| Q11 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q13 | execute_sql | ✗ population_filter / wrong_grain | ✓ | ✓ | A→B fixed |
| Q14 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q17 | execute_sql | ✗ wrong_grain / wrong_interpretation | ✗ wrong_grain / metric_definition | ✗ over_clarification |  |
| Q18 | execute_sql | ✗ metric_definition / wrong_grain | ✗ wrong_grain / other | ✗ over_clarification |  |
| Q19 | execute_sql | ✓ | ✓ | ✓ |  |
| Q20 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q22 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q23 | execute_sql | ✗ population_filter / wrong_interpretation | ✗ wrong_interpretation | ✗ wrong_interpretation |  |
| Q24 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q25 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q26 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q27 | execute_sql | ✗ population_filter | ✗ population_filter | ✗ population_filter |  |
| Q30 | insufficient_data | ✓ | ✓ | ✓ |  |
| Q31 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q32 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q33 | execute_sql | ✗ wrong_interpretation | ✓ | ✓ | A→B fixed |
| Q37 | clarify | ✗ missed_clarification / sql_execution | ✗ missed_clarification | ✓ | B→C fixed |
| Q38 | clarify | ✗ missed_clarification | ✗ missed_clarification | ✗ other |  |

## Primary labels by version

| Label | A | B | C |
| --- | ---: | ---: | ---: |
| `population_filter` | 15 | 1 | 1 |
| `metric_definition` | 2 | 1 | 1 |
| `wrong_grain` | 1 | 2 | 0 |
| `date_boundary` | 1 | 0 | 0 |
| `wrong_interpretation` | 1 | 1 | 1 |
| `missed_clarification` | 2 | 2 | 0 |
| `silent_assumption` | 0 | 2 | 0 |
| `over_clarification` | 0 | 0 | 2 |
| `other` | 0 | 0 | 1 |
| `sql_execution`, `hallucinated_column`, `join_amplification` | 0 | 0 | 0 |

## Day 10 questions

**What did A → B mainly fix?** Population definition. Fifteen A failures came from inventing or omitting the valid-order population; B no longer has 14 of them, consistent with the semantics defining valid orders and making them the default for commercial analysis. The calendar-date rule fixes the one date-boundary failure (Q07). Thirteen questions move to fully correct and none move back.

**What did B → C mainly fix?** Behaviour, not numbers. Of the three new fully correct answers, two come from disclosure (Q02, Q05) and one from clarification (Q37). Transparency improved on Q01, Q02 and Q05 and regressed on Q18 (net 3/7 → 5/7), consistent with C2 (state every analytical choice). Q37's clarification and Q38's withheld list are consistent with C1, and Q13's product-level aggregation with C3. The code-level checks ran but raised no warning (0 warnings, 0 repairs), so no corrective contribution from them was observed on this set. The first over-clarifications (Q17, Q18) appear alongside C1. Single runs without rule-by-rule ablation cannot isolate any one rule's effect.

**What did none of the three versions solve, and why?**
- **Q01 revenue and growth:** A chose an accepted basis (payment value) but failed on population and on its growth interpretation; B and C apply the right population but define revenue as price + freight, which is not an accepted basis. The semantics deliberately leaves revenue undefined. The coverage caveats (sparse 2016, Sep-2018 cutoff) are never complete in any version, even though C has a coverage rule (C8).
- **Q23 accounting caveat:** numbers are right from B onward, but no version says merchandise sales is not accounting revenue. Nothing in the context asks for it.
- **Q27 payment-record population:** every version counts all payment rows. One possible explanation is that the question was read as a raw-table data-quality count, which the semantics treats separately from the commercial valid-order default; no response states that reasoning.
- **Q17 / Q18 review attribution:** A and B attempt the calculation with grain errors (B collapses distinct reviews on the same order); C stops and asks. The model context warns that review analysis by product or seller needs a defined attribution grain or rule but does not state one, which is a plausible contributor.

## Hypotheses (development only)

- **H1 (A → B mainly from fewer metric-definition, wrong-grain and join-amplification errors):** consistent with the knowledge-gap explanation, but the predicted categories are not supported. The gain is population and date semantics; join amplification never occurs; primary wrong grain does not fall (1 → 2).
- **H2 (B → C mainly from ambiguous questions and execution errors):** partly supported on clarification (Q37 fixed, Q38 behaviour improved); the execution-repair part is untested, because B made no execution errors. The prediction that these two sources would account for most of the gain is not borne out: two of the three new fully correct answers come from disclosure. C also adds over-clarification as a new failure mode.

## Decisions and open items

- **Q38** is graded strictly (behavior pass, result fail): C asks which measure to use, not which comparison baseline. C = 20/26.
- **Pre-freeze revision** is a separate decision. Methodology §7 allows development-driven changes if they are general, layer-tagged and logged, followed by a full re-run of all 26 development questions on A, B and C. Candidates under consideration: a B-layer review-attribution definition (Q17, Q18); possibly the general commercial-vs-accounting caveat (Q23) and the scope boundary of the raw-table rule (Q27). Q01's accepted-basis list should not be written into the context. No system change has been made.
