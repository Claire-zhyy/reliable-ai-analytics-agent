---
type: note
status: active
created: 2026-10-02
updated: 2026-10-02
project: job-search
tags: [type/note, status/active, topic/ai]
---

# Benchmark Split · Development / Held-out

> Benchmark v4, split and locked on 2026-10-02. Development questions may be used repeatedly to diagnose failures and improve Version B and Version C. Held-out questions are run once, on all three versions, after the system is frozen. Per-question grading stays in `04-2-benchmark-answer-key.md`; how grading is applied is defined in `05-evaluation-methodology.md`.

## 1. Result

| Split | Count | Questions |
| --- | ---: | --- |
| Development | 26 | Q01, Q02, Q04, Q05, Q07, Q08, Q09, Q11, Q13, Q14, Q17, Q18, Q19, Q20, Q22, Q23, Q24, Q25, Q26, Q27, Q30, Q31, Q32, Q33, Q37, Q38 |
| Held-out | 13 | Q03, Q06, Q10, Q12, Q15, Q16, Q21, Q28, Q29, Q34, Q35, Q36, Q39 |

| Expected behavior / handling | Development | Held-out | Total |
| --- | ---: | ---: | ---: |
| `execute_sql` · `defined` | 16 | 7 | 23 |
| `execute_sql` · `disclosed_assumption` | 7 | 3 | 10 |
| `clarify` | 2 | 2 | 4 |
| `insufficient_data` | 1 | 1 | 2 |
| **Total** | **26** | **13** | **39** |

| Difficulty | Development | Held-out |
| --- | ---: | ---: |
| Easy | 2 | 1 |
| Easy–Medium | 3 | 1 |
| Medium | 15 | 7 |
| Medium–Hard | 0 | 1 |
| Hard | 6 | 3 |

The held-out headline set is its 10 `execute_sql` questions (7 defined, 3 disclosed-assumption). The two held-out `clarify` questions and one `insufficient_data` question are reported with their development counterparts as pooled descriptive counts, as stated in the project brief.

## 2. Constraints applied

**Contrast groups from the project brief.** All five groups stay whole: `{Q13, Q24, Q38}`, `{Q05, Q14}` and `{Q37, Q25}` are in development; `{Q16, Q35}` and `{Q39, Q34}` are in held-out.

**Q31, Q32 and Q33 in development.** The pre-registered Version C rules for direct measures, sequential-event metrics and two-table reconciliation were drafted with these three questions in view. Keeping them in development means any held-out gain from Version C comes from questions those rules were not written against.

**Additional co-location.** Four further questions were kept with a partner because one question's reference metric or method is reused directly in the other, so a development fix on one would effectively answer the other. Questions that only share a general rule (customer identity, the valid-order default, the delivery-time definition, coverage checks) were allowed to sit on opposite sides, because generalising a rule to new questions is what the held-out set is meant to test.

| Question | Placed with | Reason |
| --- | --- | --- |
| Q03 | Q16, Q35 (held-out) | Q16's answer key contrasts its cancellation definition directly with Q03's "stopped or cancelled". |
| Q11 | Q05, Q14 (development) | Q11's reference interpretation is Q14's units-sold metric by year. |
| Q12 | Q34, Q39 (held-out) | Q12's first reference finding is Q34's state-level delivery result. |
| Q17 | Q18 (development) | Identical review-attribution method and threshold rule. |

The project brief lists only the five original groups. These four placements are recorded here and do not change the brief's rule.

**Balance.** The remaining questions were assigned so that behavior, ambiguity handling and difficulty sit close to a one-third share in held-out. With only four `clarify` and two `insufficient_data` questions, exact proportions are not possible; the split gives each side two `clarify` and one `insufficient_data` question.

## 3. What each side tests

The two `clarify` questions on each side test different ambiguity types: development has a composite concept flagged in the semantics (Q37) and a missing comparison baseline (Q38); held-out has an undefined concept (Q06) and a missing decision purpose (Q39). A clarification rule developed on one side is therefore tested on a different kind of ambiguity, not a repeat. The `insufficient_data` questions follow the same logic: schema boundary in development (Q30), unsupported business metric in held-out (Q15).

Held-out `execute_sql` questions cover the valid-order default with a join (Q10), customer identity (Q21), coverage-aware period comparison (Q28), missing-record and denominator control (Q29), delivery geography (Q34), explicit all-record denominators (Q35), review grain and review-time attribution (Q36), status semantics and anomaly rules (Q03, Q16), and exploratory association analysis (Q12).

**Known gap.** Because Q31 and Q33 are fixed in development, held-out has no item-by-payment join-amplification question. Held-out still tests duplication control through multiple review rows per order (Q29), repeated `review_id` mappings (Q36) and customer grain (Q21), but conclusions about item–payment amplification will rest on development evidence and must be reported that way.

## 4. Lock rules

Frozen from this point: question wording, split membership, the answer key (including every held-out entry), reference SQL and grading rules. During development, changes are allowed only to the Version B context (`03-olist-business-semantics.md`, `02-tables-model-context.md`) and Version C prompt rules and code checks, only in response to development failures, and only as generalisable rules logged under `05-evaluation-methodology.md` §7.

Not allowed before the system freeze: running any version on held-out questions, reading held-out questions while designing rules, or editing held-out answer-key entries. Not allowed after the held-out run: changing anything and re-running. The held-out protocol is in `05-evaluation-methodology.md` §8.

The runner reads questions from `benchmark/questions-dev.csv` during development. `benchmark/questions-heldout.csv` is not loaded until the freeze. Only the `question` column is sent to the model; the other columns are grader metadata.

## 5. Lock record

| Item | Value |
| --- | --- |
| Lock date | 2026-10-02 |
| Benchmark version | v4 (frozen) |
| `questions-heldout.csv` SHA-256 | `4492c6d1636812f8a13f88b189fbd43e892d8b18560d095f9e6f4465ac61f10d` |
| Frozen source files (Drive last-modified, UTC) | `01-project-brief.md` 09:39 · `02-tables-model-context.md` 10:03 · `03-olist-business-semantics.md` 09:40 · `04-1-olist-benchmark-questions.md` 10:03 · `04-2-benchmark-answer-key.md` 10:04 · `reference-queries.sql` 10:04 |

To complete the lock in the repository, commit the frozen files and these two CSVs together, record their hashes, and tag the commit:

```bash
shasum -a 256 benchmark/questions-heldout.csv benchmark/questions-dev.csv \
  benchmark/reference-queries.sql docs/*.md > benchmark/FREEZE-SHA256.txt
git add . && git commit -m "Freeze benchmark v4 and lock held-out split"
git tag benchmark-v4-frozen
```

README line:

> Held-out set locked on 2026-10-02 (benchmark v4, tag `benchmark-v4-frozen`). The 13 held-out questions were not used for tuning and are run once on all three versions after the system freeze.
