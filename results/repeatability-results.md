# Repeatability Test (methodology §8.6)

> Run `C-repeat-20261018T093723Z`: Version C, the five questions pre-registered in `results/system-freeze-record.md` before the held-out run, three repetitions each (15 items, all `completed`). Same frozen prompt and context hashes as the held-out run (`aa536654…`, `e9099d59…`); executed with `src/core/repeatability.py`, which reuses the frozen runner unchanged. Descriptive only: no grade or system change follows. The development re-run (`C-dev-20261018T083658Z`) is shown as a fourth observation.

## Summary

| Q | Expected | SQL / numbers | Behaviour | Final answer | Pass in 3 reps | Dev re-run |
| --- | --- | --- | --- | --- | ---: | --- |
| Q31 | execute_sql | Identical result (4,426 orders, 246.93) | Stable | Stable, full method stated | 3/3 | pass |
| Q37 | clarify | No SQL | Stable: one clarifying question | Same options each time | 3/3 | pass |
| Q23 | execute_sql | Identical 12 monthly values | Stable | Accounting caveat missing every time | 0/3 | fail (same reason) |
| Q01 | execute_sql | Revenue basis price + freight in all 3 (dev re-run used merchandise value); growth window varies | Stable: answers | Like-for-like Jan 1–Sep 3 (+134.9%) in rep 1; Jan–Aug (+140.37%) in reps 2–3 | 0/3 | fail |
| Q18 | execute_sql | Rep 3: n ≥ 30, averages to 3 dp, ranking matches the reference in order | **Unstable:** reps 1–2 asked which threshold to use (over-clarification); rep 3 answered | Rep 3 states association but not that reviews also reflect delivery and platform experience | 0/3 | fail (rounding reversed ranks) |

## Findings

**Deterministic computations are stable; judgement calls are not.** Questions with one defined calculation (Q31, Q23) returned identical numbers in every run, and the clarify item (Q37) asked the same question each time. Where the model has to choose, it chose differently across runs: the growth window on Q01, the revenue basis on Q01 across the development and repeat runs, whether to ask or answer on Q18, and the rounding precision used before ranking on Q18.

**Pass/fail outcomes were consistent; failure reasons were not.** All 15 items had the same pass/fail outcome as the development re-run. But on Q01 and Q18 the reason for failing changed from run to run. Rep 3 of Q18 fixed the ordering error seen in the development re-run but missed part of a caveat, and reps 2–3 of Q01 used the correct Jan–Aug window while keeping an unaccepted revenue basis.

**Over-clarification is intermittent.** On Q18, the round-1 over-clarification (about attribution) disappeared after the review-attribution definition was added, but two of three repetitions still asked, now about the minimum review count. C1's boundary between "genuinely ambiguous" and "state a reasonable choice" is not applied consistently.

**Implication for the headline.** With single runs per version, an individual question can flip between runs for reasons unrelated to the layer under test. This supports reporting the held-out comparison as a direction (A well below B; C not above B on `execute_sql`, above B on clarification and disclosure) rather than as precise rates.
