# Version C Development Evaluation

> Run `C-dev-20261014T093341Z` · 26 development questions · graded on 2026-10-18 with the same standard as Version B (grading decisions logged in `results/evaluation-change-log.md`, 2026-10-18), independently re-verified, and confirmed by Claire (Q38 graded strictly).

## Headline results

| | A | B | C |
| --- | ---: | ---: | ---: |
| Fully correct | 4/26 | 17/26 | **20/26** |
| Behavior pass | 24/26 | 24/26 | 24/26 |
| Result pass | 4/26 | 19/26 | 20/26 |
| Assumption transparency | 0/7 | 3/7 | 5/7 |
| `execute_sql` fully correct | 3/23 | 16/23 | 18/23 |
| `clarify` fully correct | 0/2 | 0/2 | 1/2 |
| `insufficient_data` fully correct | 1/1 | 1/1 | 1/1 |
| Over-clarification on `execute_sql` | 0 | 0 | 2 |

Fully correct in C: B's 17 plus Q02, Q05 and Q37. No question that was fully correct in B fails in C.

Primary labels in C: `over_clarification` 2 (Q17, Q18), `metric_definition` 1 (Q01), `wrong_interpretation` 1 (Q23), `population_filter` 1 (Q27), `other` 1 (Q38).

## Code-level checks

The code checks ran but never raised a warning: 25 pre-execution validations passed, 9 join fan-out checks and 3 duplicate-entity checks returned ok, and there were 0 SQL errors and 0 repair rounds. Five items ran no SQL (Q17, Q18, Q30, Q37, Q38). **No corrective contribution from the code-level checks was observed on development**; the observed B → C changes are in answer text and behaviour, which is consistent with the prompt-level rules. Development gave the checks little to catch, because B already made no execution or join-amplification errors. This is a finding to report, not a reason to drop them. With a single run per version and no rule-by-rule ablation, the effect of any individual rule cannot be isolated, and run-to-run variation cannot be excluded.

## Changes consistent with the prompt rules

- **Disclosure (consistent with C2, state assumptions).** Transparency changed on four items: Q01, Q02 and Q05 improved, Q18 regressed (no threshold declared because C asked instead of answering), net 3/7 → 5/7. Q02 and Q05 became fully correct. Nearly every C answer that runs SQL ends with an explicit method paragraph; Q01 states all three required disclosures, so its transparency passes even though the revenue basis is not accepted (judged under `result`).
- **Grain (consistent with C3, grain before aggregating).** In Q13, C aggregates to `product_id` with `MAX(price)` instead of ranking raw item rows. A's and B's row-level outputs happened to match Interpretation B; A still failed on population, and B passed on output with the method risk noted.
- **Clarification (consistent with C1, clarify only when genuinely ambiguous).** Q37 now gets one focused question with data-supported options, and Q38 no longer presents a final list. C1 was written from these two development failures, so this improvement is partly by design and must be confirmed on held-out.
- **Over-clarification appears (Q17, Q18), coinciding with C1.** On both review questions C ran no SQL and asked how order-level reviews should be attributed to products or sellers. B answered these (with grain errors); C asks instead, so the failure type changed from `wrong_grain` to `over_clarification` and behavior regressed on these two items. A plausible mechanism is a context gap combined with the rule: `02-tables-model-context.md` warns that review analysis by product or seller needs a defined attribution grain or rule, but neither context file states one, which could make the attribution look genuinely ambiguous under C1. This is an interpretation, not a tested cause.

## What C did not fix

- **Q01:** revenue is still price + freight, not an accepted basis, and C8 (coverage) did not produce the sparse-2016 or Sep-2018 cutoff caveats; the like-for-like window still runs to Sep 3.
- **Q23:** numbers perfect, the accounting-convention caveat is still missing. No rule or context line asks for it.
- **Q27:** still 2,961 vs 2,920. C states that it used all payment records but does not say why. One possible explanation is that the model read the question as a raw-table data-quality count, which the semantics treats separately from the commercial valid-order default; the answer text does not confirm this.
- **Q38:** C asks which measure defines underperformance (sales, volume, ratings, delivery), essentially the same clarification as Q37, rather than which comparison baseline the judgement is made against; "comparison threshold" appears only in passing. Graded as behavior pass, result fail (`other`). The question was designed to separate a missing metric (Q37) from a missing baseline (Q38), and C's clarification does not make that distinction.
