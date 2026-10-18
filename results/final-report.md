# Reliable AI Analytics Agent — Final Report

> Evaluation case study, completed 2026-10-18. How reliably can an LLM answer business questions over a multi-table database, which analytical errors does it make, and how much do business context and workflow controls each improve reliability? Detailed records: `results/heldout-results.md`, `results/dev-comparison-abc.md`, `results/repeatability-results.md`, `results/evaluation-change-log.md`.

## Answer in brief

On questions the system had never been tuned on, giving the model analyst-written business definitions raised fully correct answers from **2/10 to 6/10**. Adding workflow controls on top (prompt rules plus code-level SQL checks and bounded self-repair) improved behaviour, with better clarification of ambiguous questions, complete disclosure of analytical choices and no answers lost to SQL errors, but it did **not** raise result accuracy (**4/10**). Several of its losses came from rules being applied to situations they were not written for.

The model's main weakness was not SQL. It was business semantics: which orders count, which date defines a period, what a metric means. That knowledge has to come from an analyst.

## Setup

| | |
| --- | --- |
| Data | Olist Brazilian e-commerce dataset, 9 tables, 99,441 orders, local DuckDB |
| Model | `gpt-5.6-terra`, reasoning effort medium, one `run_sql` tool, max 5 tool rounds |
| Benchmark | 39 business questions written in stakeholder language: 26 development, 13 held-out (frozen 2026-10-02 with connected contrast groups kept on one side) |
| Expected behaviours | `execute_sql` (33), `clarify` (4), `insufficient_data` (2) |
| Grading | On results, not SQL text: behaviour, result (values, required caveats, disallowed claims) and, for disclosed-assumption questions, transparency. Fully correct only when every applicable dimension passes. |

| Version | Adds |
| --- | --- |
| A — raw schema | Schema and `run_sql` only |
| B — business semantics | A + data dictionary and business-semantics documents |
| C — workflow controls | B + 12 prompt rules and code checks (schema validation, ≤2 repairs, join fan-out and duplicate-entity checks) |

All three share the model, runner, tool and database, so only the layer under test changes.

## Results

### Held-out (headline)

| | A | B | C |
| --- | ---: | ---: | ---: |
| **Fully correct, `execute_sql` (10)** | **2/10** | **6/10** | **4/10** |
| Fully correct, all 13 | 2/13 | 8/13 | 7/13 |
| Assumption transparency (3) | 2/3 | 1/3 | 3/3 |
| Behaviour pass (13) | 10/13 | 12/13 | 13/13 |
| Items ended by an SQL error | 0 | 2 | 0 |

Pooled descriptive counts (development + held-out): `clarify` A 0/4, B 1/4, C 3/4; `insufficient_data` A 1/2, B 2/2, C 2/2.

### Development (pre-freeze re-run, tuning set)

A 4/26, B 16/26, C 19/26 fully correct. These are practice-set scores: B's context and C's rules were revised using these questions, so they overstate held-out performance. The C > B ordering on development did not hold on held-out.

## Findings

**1. Population definition was the dominant failure, and business semantics fixed it.** In both development runs, 15 of Version A's 22 failures were wrong order populations: inventing or omitting the "valid order" definition. A also guessed a different definition from run to run (for example 98,207 vs 96,478 valid orders for the same question). B, given the documented definition, dropped development population failures to 1–2 and got all four held-out population questions right.

**2. Join amplification never occurred.** The pre-registered hypothesis expected join double-counting to be a major error source. In 117 graded items it never appeared as a primary error. The failures were semantic, not mechanical.

**3. Workflow controls changed behaviour more than results.** C asked focused clarifying questions where definitions were missing (3/4 pooled vs B 1/4), stated every analytical choice (transparency 3/3 held-out, 7/7 development) and recovered from SQL errors. On held-out Q03, B and C hit the same DuckDB cast error: B stopped, and C repaired the query and answered.

**4. Rules over-generalised on unseen questions.** C's three held-out regressions are each consistent with a rule applied outside its intended situation: a minimum-sample rule removed the two slowest states from a ranking that needed no threshold (Q34); a coverage rule produced a "like-for-like" comparison that repeated a data-cutoff error (Q28); and a review-attribution definition added before freeze was applied to a review-year average that needed no attribution (Q36). Development tuning made these rules look beneficial; the held-out set exposed their side effects.

**5. Stable computation, unstable judgement.** In the repeatability test (5 questions × 3 runs on C), defined calculations returned identical numbers every time, but judgement calls varied: the growth window, whether to ask or answer, rounding before ranking. Pass/fail outcomes matched the earlier run on all 15 items, while failure reasons sometimes changed.

**6. Gaps no version closed.** Required caveats that a careful analyst would add were missed by every version: merchandise sales is not accounting revenue; the dataset does not record who initiated a cancellation. The extraction cutoff in September 2018 also repeatedly distorted period comparisons.

## Hypotheses

- **H1** (A → B gains mainly from fewer metric-definition, wrong-grain and join-amplification errors): mechanism supported, categories not. B's gain came from population and date definitions.
- **H2** (B → C gains mainly from ambiguous questions and execution errors): partly supported. Clarification and error recovery improved, but result accuracy did not.

## Method notes and limitations

- **Small sample.** Ten held-out `execute_sql` questions: one question is 10 percentage points, each version ran once, and repeat runs showed item-level variation. The findings are directions (A well below B; C not above B on accuracy, above B on clarification and disclosure), not precise rates.
- **Same author.** I wrote the benchmark, the answer key and the business-semantics documents. The held-out split, frozen answer key and connected contrast groups limit this but do not remove it.
- **One pre-freeze revision.** A review-attribution definition was added to B after development round 1 (logged with its trigger and rationale), followed by a full development re-run before freeze.
- **Grading.** Strict and pre-specified; every round was independently re-verified (four rounds). Grading clarifications made after results were visible are logged with reasons: ranking order, caveats, disclosure reading, and one precision clarification on held-out (a correctly rounded percentage is not failed for fewer decimals).
- **Not in scope.** Single model, no fine-tuning, no production UI or deployment. The RAG and MCP extensions were not attempted.

## Implications for using LLMs on company data

An LLM connected to a database will write executable SQL and plausible numbers, and a large share of them will rest on guessed business definitions. The highest-leverage investment is an analyst-maintained semantic layer: populations, metric definitions, date conventions and known data limits. Workflow rules help the model ask and disclose, but they need their own held-out testing, because rules tuned on known questions can misfire on new ones. Human review remains necessary for caveats and judgement calls, which were the least stable part of every version.
