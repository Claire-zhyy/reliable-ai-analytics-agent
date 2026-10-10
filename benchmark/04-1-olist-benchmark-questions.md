# Olist Benchmark Questions v4

> Status: benchmark v4 — frozen 2026-10-02
> Total questions: 39
> Expected behavior types: `execute_sql` / `clarify` / `insufficient_data`
> Purpose: representative analytical capability and failure-mode test suite for evaluating AI analytics reliability.
> This benchmark is not a catalogue of all possible business questions. Each question represents a reusable analytical capability, business judgement, or failure mode.

## Changelog

**v4 (2026-10-02) — frozen.** Finalised elapsed-duration evaluation, submitted-review population, parameterised Q17/Q18 minimum-review thresholds, Q12 NULL-band results, evidence-free Version B context, and connected contrast-group split constraints. No new questions or analytical scope were added. After this freeze, held-out results must not be used to revise questions, groups, semantics, grading rules, prompts, or workflow controls.

**v3 (2026-09-29).** Adopted the minimum-interruption principle: ambiguity alone no longer implies `clarify`. Q01, Q02, Q03, Q05, Q11, Q12, Q13, Q16, Q17 and Q18 moved from `clarify` to `execute_sql` with a disclosed assumption. Q06 remains `clarify`. Q37–Q39 added as new `clarify` questions so the category stays measurable after the split. Q36 rule aligned with the answer key (`review_answer_timestamp`, not purchase year). Added the `Ambiguity Handling` column. Q16 accepted interpretations revised: order-level or customer-level cancellation; canceled + unavailable reclassified as a separately labelled failed/stopped-order metric.

## Expected Behavior Definitions

| Expected Behavior | Meaning |
| --- | --- |
| `execute_sql` | The available data can support a reliable answer, and either (a) the question and the semantic layer define what to calculate, or (b) one interpretation is a reasonable default. In case (b) the model should proceed, state the assumption explicitly in the response, and mention alternatives where they would materially change the result. |
| `clarify` | The required data exists, but several interpretations are similarly plausible, no semantic definition or defensible default resolves them, and choosing the wrong one would materially change the result or the business decision. The model should ask a focused clarification question before producing a final answer. |
| `insufficient_data` | The requested business conclusion cannot be reliably supported by the available dataset. The model should explain the specific data gap, avoid presenting an unsupported proxy as the requested metric, and state what analysis is still possible or what additional data would be required. |

## Ambiguity Handling Principle

Detecting ambiguity is not the capability under test; deciding what to do with it is. The expected handling follows this order:

1. **Defined.** If the question or the business semantics already defines the concept, use that definition without asking.
2. **Disclosed assumption.** If no definition exists but one interpretation is reasonably dominant and the analytical risk is limited, proceed with that default, state it in the response (not only inside the SQL), and mention material alternatives.
3. **Clarify.** If multiple interpretations are similarly plausible and would materially change the result or decision, ask one focused clarification question.
4. **Insufficient data.** If the required data does not exist, say so and explain what is missing.

The desired behavior is minimum interruption plus explicit assumptions plus risk-based clarification. The benchmark penalises both silent guessing and unnecessary clarification.

The `Ambiguity Handling` column records which case each question belongs to: `defined`, `disclosed_assumption`, `clarify`, or `n/a` (for `insufficient_data`).

## Benchmark Questions

| ID | Question | Difficulty | Question Type | Expected Behavior | Ambiguity Handling | Expected Clarification / Rule | Capability / Failure Mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | What was our revenue from 2015 to the latest available date, and how has it grown over that period? | Medium | metric_definition / date_logic | `execute_sql` | `disclosed_assumption` | Choose and state a monetary basis (payment value or merchandise value). Flag that data starts in Sep 2016, not 2015. Measure growth on a comparable basis and treat Sep–Oct 2018 as an extraction-cutoff tail, not a decline. | Monetary ambiguity / false premise / period coverage |
| Q02 | Which product is associated with the highest freight expense, and why? | Hard | multi_table_join / ambiguous | `execute_sql` | `disclosed_assumption` | State the product grain and freight metric (default: category, total freight). Explain "why" at least through a volume vs per-item freight decomposition; any further factors must be framed as associations. | Attribution / association vs causation |
| Q03 | How many orders were stopped or cancelled each month from 2017 onward, and were there any unusual spikes? | Hard | metric_definition / date_logic | `execute_sql` | `disclosed_assumption` | State the "stopped" definition, purchase-month attribution, and the spike rule used. Judge spikes on rate, not raw count. Treat Sep–Oct 2018 as a coverage artifact. | Status ambiguity / anomaly definition / coverage artifact |
| Q04 | Across our customers, how many placed only one valid order, two valid orders, and three or more valid orders? | Medium | metric_definition / multi_table_join | `execute_sql` | `defined` | Use `customer_unique_id` and the valid-order definition. | Customer identity / customer grain |
| Q05 | Year by year, which sellers sold the most products? | Medium | metric_definition / date_logic | `execute_sql` | `disclosed_assumption` | Default: units sold (item rows) per seller per year, valid orders. State the assumption; ranking by merchandise sales gives a different top seller in 2017 and 2018. | Metric ambiguity / ranking definition |
| Q06 | Which products are the most competitive? | Medium | ambiguous | `clarify` | `clarify` | Define "competitive": sales, unit volume, price, review score, growth, delivery performance, or another criterion. | Undefined business concept |
| Q07 | What percentage of delivered orders arrived on time? | Medium | metric_definition / date_logic | `execute_sql` | `defined` | Use delivered orders with usable actual and estimated delivery dates. | Business semantics / delivery metric |
| Q08 | For orders that were handed over to the carrier, on average, how long did it take from order placement to carrier handoff? | Medium | date_logic | `execute_sql` | `defined` | Use elapsed time from purchase timestamp to carrier handoff timestamp for orders where carrier handoff exists. | Process timing / date logic |
| Q09 | On average, how long does it take from order placement until the customer receives the order? | Medium | date_logic | `execute_sql` | `defined` | Use elapsed time from purchase timestamp to customer delivery timestamp; delivered orders only. | Delivery semantics / date logic |
| Q10 | Which customer cities generated the most valid orders? | Easy | simple_aggregation / multi_table_join | `execute_sql` | `defined` | Count valid orders by customer city. | Basic aggregation / geography join |
| Q11 | What was our most popular product each year? | Medium | ambiguous / date_logic | `execute_sql` | `disclosed_assumption` | "Popular" defaults to units sold. State the product grain (product_id or category); both are accepted if disclosed. | Ambiguous ranking / date logic |
| Q12 | What factors are associated with longer customer delivery times? | Hard | multi_table_join / failure_trap | `execute_sql` | `disclosed_assumption` | Delivery time is defined by the semantics. The model chooses and states the candidate factors from available data, compares delivery time across them with sample sizes, and frames findings as associations. Rubric-graded. | Analytical reasoning / causality boundary |
| Q13 | Which products are the most expensive? | Medium | metric_definition | `execute_sql` | `disclosed_assumption` | Default: product_id ranked by average selling price. State the assumption; ranking by maximum observed price is also accepted. | Metric definition |
| Q14 | Which individual products sold the most units? | Medium | multi_table_join | `execute_sql` | `defined` | Rank `product_id` by valid-order item count. | Product-level aggregation |
| Q15 | How has our profitability changed year over year? | Hard | insufficient_data / failure_trap | `insufficient_data` | `n/a` | The dataset does not contain the cost, commission, take-rate and other inputs required to calculate profitability reliably. Explain the gap and identify valid alternatives such as merchandise sales or payment-value trends without calling them profit. | Data sufficiency / unsupported metric |
| Q16 | What is our customer cancellation rate? | Medium | metric_definition | `execute_sql` | `disclosed_assumption` | Default: canceled orders as a share of all order records (order grain). Customer-level incidence (share of `customer_unique_id` with ≥1 canceled order) is also accepted. State grain, numerator and denominator; note the data does not record who initiated a cancellation. `canceled + unavailable` is a failed/stopped-order rate, not cancellation rate. | Grain ambiguity / status semantics / unverifiable qualifier |
| Q17 | Which products have the highest customer review ratings? | Hard | multi_table_join / failure_trap | `execute_sql` | `disclosed_assumption` | Use submitted reviews regardless of current order status. State the product grain, a minimum review count between 20 and 100 inclusive, and how uniquely mapped order-level reviews are attributed to products. Grade against the declared threshold. Ranking without a minimum review count fails. | Attribution risk / review grain / small samples |
| Q18 | Which sellers are associated with the lowest customer review ratings? | Hard | multi_table_join / failure_trap | `execute_sql` | `disclosed_assumption` | Use submitted reviews regardless of current order status. State a minimum review count between 20 and 100 inclusive and how uniquely mapped order-level reviews are attributed to sellers. Grade against the declared threshold. Ranking without a minimum review count fails. | Seller attribution / review grain / small samples |
| Q19 | How many order records are in the dataset? | Easy | simple_aggregation | `execute_sql` | `defined` | — | Basic SQL / COUNT |
| Q20 | How many valid orders do we have? | Easy | metric_definition | `execute_sql` | `defined` | Apply the valid-order status definition. | Business filter / semantic rule |
| Q21 | How many unique customers placed at least one valid order? | Easy–Medium | simple_aggregation / metric_definition | `execute_sql` | `defined` | Use `customer_unique_id`. | Customer identity |
| Q22 | How many valid orders did we receive each month in 2017? | Easy–Medium | date_logic | `execute_sql` | `defined` | Use `order_purchase_timestamp`. | Monthly aggregation / date logic |
| Q23 | What was our merchandise sales each month in 2017? | Medium | date_logic / multi_table_join | `execute_sql` | `defined` | Use `SUM(order_items.price)` for valid orders and purchase date for monthly attribution. | Defined monetary metric / join |
| Q24 | Which product categories generated the highest merchandise sales? | Medium | multi_table_join | `execute_sql` | `defined` | Use `SUM(order_items.price)` by product category for valid orders. | Category attribution / ranking |
| Q25 | Which sellers generated the highest merchandise sales? | Medium | multi_table_join | `execute_sql` | `defined` | Use `SUM(order_items.price)` by seller for valid orders. | Seller attribution / ranking |
| Q26 | How many orders contained more than one item? | Easy–Medium | simple_aggregation | `execute_sql` | `defined` | Group item rows by `order_id`. | Item grain |
| Q27 | How many orders had more than one payment record? | Easy–Medium | simple_aggregation | `execute_sql` | `defined` | Group payment rows by `order_id`. | Payment grain |
| Q28 | How did the number of valid orders change from 2017 to 2018? | Medium | date_logic / failure_trap | `execute_sql` | `defined` | Calculate the values, but interpretation must account for whether the two periods have comparable data coverage. | Time-period comparability / data coverage awareness |
| Q29 | What percentage of valid orders have no customer review? | Medium | multi_table_join / data_quality | `execute_sql` | `defined` | Use valid orders as the denominator and detect missing reviews with a safe left-join / existence check. | Missing records / denominator control |
| Q30 | Which marketing channels generated the most valid orders? | Medium | insufficient_data / schema_boundary | `insufficient_data` | `n/a` | The dataset does not contain acquisition or marketing-channel information. Explain the missing dimension and do not invent a channel/source column. | Schema boundary / hallucinated-column risk |
| Q31 | For valid orders in 2017 that contained more than one item, what was the average amount paid per order? | Hard | multi_table_join / failure_trap | `execute_sql` | `defined` | Identify multi-item orders, aggregate payments to order grain, then calculate the average. | Join amplification / grain control |
| Q32 | Among repeat customers, what was the average number of days between their first and second valid orders? | Hard | date_logic / metric_definition | `execute_sql` | `defined` | Use `customer_unique_id`, valid orders, and first-to-second purchase interval. | Window logic / repeat-purchase semantics |
| Q33 | How many orders have payment records but no order items, and how many have order items but no payment records? | Hard | reconciliation / data_quality | `execute_sql` | `defined` | Reconcile both sides at `order_id` grain and count missing-side records. | Reconciliation / missing-side detection / join safety |
| Q34 | Which customer states have the longest average delivery times? | Medium–Hard | multi_table_join / date_logic | `execute_sql` | `defined` | Join customer geography to delivered orders and calculate elapsed delivery time using the defined delivery metric. | Geography join / delivery metric |
| Q35 | What percentage of all order records were cancelled each month in 2017? | Medium | date_logic / metric_definition | `execute_sql` | `defined` | Explicit denominator = all order records in each month. | Cancellation trend / denominator control |
| Q36 | How did the average review score across submitted reviews change year over year? | Medium | date_logic / multi_table_join | `execute_sql` | `defined` | Use submitted review records regardless of current order status, deduplicate at `review_id` grain, and attribute them to the year of `review_answer_timestamp`. | Review trend / review grain |
| Q37 | Who are our best-performing sellers? | Medium | ambiguous | `clarify` | `clarify` | Clarify which performance dimension (sales, order volume, delivery performance, review score, cancellation rate) or which decision the ranking supports. The semantics file explicitly flags this term as ambiguous. | Composite performance concept / use of semantic ambiguity flag |
| Q38 | Which product categories are underperforming? | Medium | ambiguous | `clarify` | `clarify` | Clarify the comparison baseline: decline versus a prior period, low results versus other categories, weak service quality, or a target (targets are not in the data). | Missing comparison baseline |
| Q39 | Which customer states should we prioritise? | Medium | ambiguous | `clarify` | `clarify` | Clarify the goal: growing sales, improving delivery / service, or another objective. Different goals produce opposite state rankings. | Decision-purpose ambiguity |

## Benchmark Composition

| Expected Behavior | Ambiguity Handling | Count | Questions |
| --- | --- | ---: | --- |
| `execute_sql` | `defined` | 23 | Q04, Q07–Q10, Q14, Q19–Q29, Q31–Q36 |
| `execute_sql` | `disclosed_assumption` | 10 | Q01, Q02, Q03, Q05, Q11, Q12, Q13, Q16, Q17, Q18 |
| `clarify` | `clarify` | 4 | Q06, Q37, Q38, Q39 |
| `insufficient_data` | `n/a` | 2 | Q15, Q30 |
| **Total** | | **39** | |

Contrast pairs that must stay in the same split (development or held-out): Q16/Q35, Q05/Q14, Q13/Q24, Q37/Q25, Q38/Q24, Q39/Q34. Where one question appears in two pairs (Q24), keep all three together.

## Hidden Answer Key Fields

The benchmark question file defines what is being tested. The hidden answer key is maintained separately and may contain the following fields:

```text
question_id
expected_behavior
ambiguity_handling

reference_sql
acceptable_interpretations
expected_result

required_assumption_disclosure
expected_clarification

required_caveat
evaluation_rule
disallowed_claims

notes
```

Not every question requires every field.

- `reference_sql` and `expected_result` apply primarily to `execute_sql`.
- `acceptable_interpretations` applies only to `disclosed_assumption` questions. It lists at most two accepted interpretations, each with its own expected result.
- `required_assumption_disclosure` lists what the response itself must state, not only what the SQL does.
- `expected_clarification` defines the minimum acceptable clarification for `clarify`.
- `required_caveat` is used only when a numerically correct answer could still materially mislead a stakeholder.
- `evaluation_rule` defines how outputs are compared, especially for rankings, tolerances, or multi-row results.
- `disallowed_claims` captures conclusions the model must not make, such as unsupported causality or treating a proxy as profitability.

## Benchmark Design Principles

1. The benchmark is a representative test suite, not an exhaustive list of every business question that could ever be asked.
2. Each question should represent a reusable analytical capability, business judgement, or failure mode.
3. Improvements made after development-set failures must be generalisable workflow or semantic rules, not question-specific prompt patches.
4. The model should never receive the hidden answer key.
5. Ambiguity does not automatically require clarification. `clarify` is used only when interpretations are similarly plausible and materially change the result or decision; otherwise the model should proceed with a disclosed assumption.
6. Assumptions must be visible in the response. A numerically correct answer built on an undisclosed assumption is a transparency failure.
7. Asking for clarification on a `disclosed_assumption` question is an over-clarification failure.
8. `insufficient_data` is used when the requested business conclusion cannot be reliably supported even after the question is understood.
9. A strong `insufficient_data` response should identify the specific gap, avoid unsupported proxies, and explain what analysis is still possible or what additional data would be needed.
10. Time comparisons should be interpreted only when period coverage is comparable; otherwise the limitation should be surfaced.
11. The benchmark question scope should be frozen before the development / held-out split. After that point, new failures discovered during development should generally become future benchmark additions rather than retroactive held-out edits.

## Current Coverage

The 39 questions collectively test:

- basic aggregation and SQL execution
- business metric semantics
- customer identity and analytical grain
- one-to-many joins and join amplification
- reconciliation and missing-side records
- date logic, period comparability and data-coverage artifacts
- ambiguity handling: defined terms, disclosed assumptions, and genuine clarification
- insufficient-data and schema boundaries
- attribution risk
- association versus causation
- missing records and denominator control
- ranking, small-sample control and grouped analysis
- delivery and review metrics
