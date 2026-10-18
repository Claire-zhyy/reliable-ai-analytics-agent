# Version A Development Evaluation — Pre-freeze Re-run

> Run `A-dev-20261018T083037Z` (commit `7307052`) · 26 development questions · graded on 2026-10-18 with the standard in `results/evaluation-change-log.md`. Version A's instructions are unchanged from round 1 (`prompt_hash 7192e95c…`), so this run is a repeat of the same system. Round 1 (`A-dev-20261011T123502Z`) is in `dev-round1/`.

| | Round 1 | Re-run |
| --- | ---: | ---: |
| Fully correct | 4/26 | 4/26 |
| Behavior pass | 24/26 | 24/26 |
| Result pass | 4/26 | 4/26 |
| Assumption transparency | 0/7 | 1/7 (Q18) |
| Primary `population_filter` | 15 | 15 |

The same four questions pass in both runs (Q08, Q09, Q19, Q30), and population definition is again the dominant failure (15 of 22). Label changes from round 1: Q17 ended on an SQL Binder error before any answer (`sql_execution`; A has no repair); Q18 now declares a 20-review minimum but merges distinct reviews and keeps ambiguous review IDs (`wrong_grain` / `wrong_interpretation`); Q02 loses its round-1 secondary label (`population_filter`); Q37 loses its round-1 secondary label (`sql_execution`), because no SQL error occurred this time. Transparency changed on Q18 only (False → True).

The headline is stable, but the guessed population is not. Q20 answered 96,478 (valid = delivered) in this run and 98,207 (valid = not canceled/unavailable) in round 1; Q22, Q32 and Q11 also used delivered-only here; Q04 and Q31 used not-canceled/unavailable, which keeps `created` orders. As in round 1, A does not converge on one stable wrong definition: it re-guesses business semantics per question and per run.
