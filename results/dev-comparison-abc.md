# A / B / C Development Comparison — Pre-freeze Re-run (Day 10)

> Development set only (26 questions): tuning-set results, not held-out results. Runs `A-dev-20261018T083037Z`, `B-dev-20261018T083414Z`, `C-dev-20261018T083658Z` on commit `7307052`, after the B-layer review-attribution definition. Grades: `results/{baseline,semantic,improved}/dev_evaluation.csv`, independently re-verified (round 3). Round 1 comparison: `dev-comparison-abc-round1.md`.

## Scores

| | A — raw schema | B — + business semantics | C — + workflow controls |
| --- | ---: | ---: | ---: |
| Fully correct | 4/26 | 16/26 | 19/26 |
| `execute_sql` fully correct | 3/23 | 15/23 | 17/23 |
| `clarify` (pooled later with held-out) | 0/2 | 0/2 | 1/2 |
| `insufficient_data` | 1/1 | 1/1 | 1/1 |
| Behavior pass | 24/26 | 24/26 | 26/26 |
| Assumption transparency | 1/7 | 4/7 | 7/7 |
| Over-clarification | 0 | 0 | 0 |

Round 1 for comparison: A 4/26, B 17/26, C 20/26.

Question-level movement: A → B fixes 13 questions and regresses 1 (Q08). B → C fixes 4 (Q02, Q08, Q33, Q37) and regresses 1 (Q24).

## Question-level table

| Q | Expected | A | B | C | Change |
| --- | --- | --- | --- | --- | --- |
| Q01 | execute_sql | ✗ population_filter / wrong_interpretation | ✗ metric_definition / wrong_interpretation | ✗ date_boundary / wrong_interpretation |  |
| Q02 | execute_sql | ✗ metric_definition | ✗ wrong_interpretation | ✓ | B→C fixed |
| Q04 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q05 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q07 | execute_sql | ✗ date_boundary | ✓ | ✓ | A→B fixed |
| Q08 | execute_sql | ✓ | ✗ population_filter | ✓ | A→B regression; B→C fixed |
| Q09 | execute_sql | ✓ | ✓ | ✓ |  |
| Q11 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q13 | execute_sql | ✗ population_filter / wrong_grain | ✓ | ✓ | A→B fixed |
| Q14 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q17 | execute_sql | ✗ sql_execution | ✗ metric_definition / wrong_interpretation | ✗ wrong_interpretation |  |
| Q18 | execute_sql | ✗ wrong_grain / wrong_interpretation | ✗ metric_definition / wrong_interpretation | ✗ other / wrong_interpretation |  |
| Q19 | execute_sql | ✓ | ✓ | ✓ |  |
| Q20 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q22 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q23 | execute_sql | ✗ population_filter / wrong_interpretation | ✗ wrong_interpretation | ✗ wrong_interpretation |  |
| Q24 | execute_sql | ✗ population_filter | ✓ | ✗ other | A→B fixed; B→C regression |
| Q25 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q26 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q27 | execute_sql | ✗ population_filter | ✗ population_filter | ✗ population_filter |  |
| Q30 | insufficient_data | ✓ | ✓ | ✓ |  |
| Q31 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q32 | execute_sql | ✗ population_filter | ✓ | ✓ | A→B fixed |
| Q33 | execute_sql | ✗ wrong_interpretation | ✗ wrong_interpretation | ✓ | B→C fixed |
| Q37 | clarify | ✗ missed_clarification | ✗ missed_clarification | ✓ | B→C fixed |
| Q38 | clarify | ✗ missed_clarification | ✗ missed_clarification | ✗ other |  |

## Primary labels

| Label | A | B | C |
| --- | ---: | ---: | ---: |
| `population_filter` | 15 | 2 | 1 |
| `metric_definition` | 1 | 3 | 0 |
| `wrong_interpretation` | 1 | 3 | 2 |
| `missed_clarification` | 2 | 2 | 0 |
| `date_boundary` | 1 | 0 | 1 |
| `wrong_grain` | 1 | 0 | 0 |
| `sql_execution` | 1 | 0 | 0 |
| `other` | 0 | 0 | 3 |
| `silent_assumption`, `over_clarification`, `hallucinated_column`, `join_amplification` | 0 | 0 | 0 |

## Round 1 vs re-run

**Scores are close across runs, and individual items move.** A scores 4/26 in both runs with the same four passes; B goes 17 → 16 and C 20 → 19. A re-guesses a different "valid order" definition on several questions. B gained Q05 and lost Q08 and Q33 through variation in population choice, disclosures and caveats. C changed revenue basis on Q01 and wrote one wrong count into Q24's answer table. With one run per version, differences of one or two questions should not be over-read.

**Review questions (Q17, Q18).** In this run, B's round-1 grain errors and C's round-1 over-clarifications do not recur, which is consistent with the review-attribution definition added before the re-run; a single run cannot prove cause. Both questions still fail: B on the minimum review count, C on a missing caveat (Q17) and on rounding before ranking (Q18). This is the one development-driven change made before freeze.

## Day 10 questions

**What did A → B mainly fix?** Population definition: 15 `population_filter` failures in A, 2 in B (Q08, Q27). B also fixes A's date-boundary failure (Q07). Thirteen questions move to fully correct; one regresses (Q08, where B narrowed the carrier-handoff population to valid orders).

**What did B → C mainly fix?** Disclosure and clarification. Transparency rises from 4/7 to 7/7 and behavior from 24/26 to 26/26, consistent with C2 (state every analytical choice) and C1 (clarify only when genuinely ambiguous). The four new passes are Q02 (disclosure and caveat), Q08 (correct observed-handoff population), Q33 (raw-table scope stated) and Q37 (clarification). One regression: Q24, a wrong order count in the answer table. The code checks fired once (Q01 schema-check rejection, repaired) without changing a grade. Single runs without rule-level ablation cannot isolate any one rule's effect.

**What did none of the versions solve?**
- **Q01 growth window:** B and C compare Jan 1–Sep 3 and miss that September 2018 is residual data at the extraction cutoff; B's revenue basis (price + freight) is also not accepted. A uses the accepted payment basis but the wrong population.
- **Q23 accounting caveat:** monthly values are exact from B onward; no version says merchandise sales is not accounting revenue.
- **Q27 payment-record population:** every version counts all payment rows (2,961 vs 2,920).
- **Q38 comparison baseline:** C asks which measure to use, not what to compare against.
- **Ranking, caveat and answer-text discipline:** C's Q18 repeats B round 1's rounding-before-ranking failure, C's Q17 misses only the significance caveat, and C's Q24 misreports one count from its own SQL.

## Hypotheses (development only)

- **H1 (A → B mainly from fewer metric-definition, wrong-grain and join-amplification errors):** consistent with the knowledge-gap explanation, but the predicted categories are not supported. The gain is population and date semantics; join amplification never occurs in any run.
- **H2 (B → C mainly from ambiguous questions and execution errors):** partly supported on clarification (Q37). Execution repair occurred once (Q01) and did not change a grade, so it is essentially untested on this set. Most of the measurable B → C gain is disclosure, plus one population correction (Q08), which H2 did not predict.

## Status

Development work is complete. The system (A prompt, B context with the review-attribution definition, C rules and code checks, runner and grading standard) is frozen for the Day 11 held-out run; see `results/system-freeze-record.md`.
