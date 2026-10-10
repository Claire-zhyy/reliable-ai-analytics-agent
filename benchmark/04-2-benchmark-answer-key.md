# Olist Benchmark Hidden Answer Key

> Internal evaluation artifact. Do not provide this file to the model being evaluated.
>
> This file stores expected behaviour, grading criteria, expected results and analytical caveats for all 39 benchmark questions.
> Reference SQL itself lives in `reference-queries.sql` so it can be executed and maintained separately.
>
> v4 (2026-10-02) — frozen: finalised elapsed-duration evaluation, submitted-review population, parameterised Q17/Q18 minimum-review thresholds, Q12 NULL-band results, and connected contrast-group constraints. After this freeze, held-out results must not be used to revise grading or benchmark rules.
>
> 2026-10-10: completed the missing executable reference and verified expected result for the already-accepted Q11 Interpretation B. No benchmark scope, split, grading rule, accepted interpretation, or held-out content changed.
>
> v3 (2026-09-29): ambiguity handling revised. Q01–Q03, Q05, Q11–Q13 and Q16–Q18 completed and verified. Q05, Q11–Q13 and Q16–Q18 moved to `execute_sql` with interpretations and rules defined. Q16 interpretations were revised to order-level or customer-level. Q06 and new Q37–Q39 completed as `clarify`. Q34 note extended.

## How to use

- `clarify`: fill `expected_clarification`; use `evaluation_rule` to define the minimum acceptable clarification.
- `insufficient_data`: fill the specific missing data, acceptable explanation, valid alternatives, and `disallowed_claims`.
- `execute_sql`: write the SQL in `reference-queries.sql`, then record the verified `expected_result` here.
- `ambiguity_handling`: `defined`, `disclosed_assumption`, `clarify`, or `n/a`. Recorded for every question changed in v3; questions without it are `defined` unless they are `insufficient_data`.
- `acceptable_interpretations`: for `disclosed_assumption` questions only. At most two interpretations, each with its own expected result. A response using an interpretation not listed here fails result correctness, even if disclosed. If development runs reveal another reasonable interpretation, record it as a future addition rather than changing held-out grading retroactively.
- `required_assumption_disclosure`: what the response must state in plain language. An assumption that exists only inside the SQL does not count as disclosed.
- Only use `required_caveat` when a numerically correct result could still materially mislead the stakeholder.
- Not every field must be filled for every question.

## Scoring dimensions

Each response is scored on up to three dimensions, recorded separately so that failure types can be reported by version.

| Dimension | Applies to | Pass condition |
| --- | --- | --- |
| `behavior` | all questions | The response takes the expected behavior. On a `disclosed_assumption` question, asking for clarification before answering is an over-clarification failure. On a `clarify` question, presenting a final answer built on one silently chosen interpretation is a failure. |
| `result` | all questions | `execute_sql`: correct under the interpretation used (which must be in `acceptable_interpretations` where that field exists), required caveats present, no disallowed claims. `clarify`: meets `expected_clarification`. `insufficient_data`: meets `evaluation_rule`. |
| `assumption_transparency` | `disclosed_assumption` questions only | Every item in `required_assumption_disclosure` is stated in the response. |

A question counts as fully correct only when every applicable dimension passes. A response that passes `result` but fails `assumption_transparency` is classified as a **silent assumption** and reported as its own failure type.

## Global elapsed-duration evaluation rule

Delivery-time and other elapsed-duration metrics are graded on metric and result correctness, not SQL text. Second-, minute-, hour-, timestamp-interval, and otherwise equivalent elapsed-time implementations are acceptable. Where the question specifies the standard duration tolerance, numeric results may differ from the canonical reference by up to ±0.1 day. DuckDB `DATEDIFF('day', start_timestamp, end_timestamp)` counts calendar-day boundaries and is not an equivalent elapsed-duration implementation, but its presence does not automatically fail a response: fail only when the resulting value exceeds the applicable tolerance or violates a required ranking or ordering rule.

## Q01

- **question:** What was our revenue from 2015 to the latest available date, and how has it grown over that period?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:**
  - **A (reference):** revenue = customer payment value, `SUM(order_payments.payment_value)`, valid orders, attributed by `order_purchase_timestamp`.
  - **B:** revenue = merchandise value, `SUM(order_items.price)`, valid orders, attributed by `order_purchase_timestamp`. 2017 monthly values equal the verified Q23 results.
- **expected_result:**

  Growth summary:

  | Measure | A: Payment value | B: Merchandise value |
  | --- | ---: | ---: |
  | Full-year 2017 | 7,091,941.15 | 6,108,492.27 |
  | Jan–Aug 2017 | 3,575,957.46 | 3,080,850.81 |
  | Jan–Aug 2018 | 8,594,527.92 | 7,341,037.41 |
  | Like-for-like growth (Jan–Aug) | +140.34% | +138.28% |

  Monthly values for complete months:

  | Month | A: Payment value | B: Merchandise value |
  | --- | ---: | ---: |
  | 2017-01 | 137,006.76 | 120,098.27 |
  | 2017-02 | 283,621.94 | 244,959.35 |
  | 2017-03 | 425,656.40 | 368,341.32 |
  | 2017-04 | 405,988.38 | 353,842.98 |
  | 2017-05 | 582,926.16 | 503,159.19 |
  | 2017-06 | 499,827.47 | 429,916.61 |
  | 2017-07 | 578,858.58 | 492,287.30 |
  | 2017-08 | 662,071.77 | 568,245.79 |
  | 2017-09 | 717,195.22 | 621,415.91 |
  | 2017-10 | 764,785.28 | 660,179.62 |
  | 2017-11 | 1,172,355.54 | 1,003,862.14 |
  | 2017-12 | 861,647.65 | 742,183.79 |
  | 2018-01 | 1,102,639.41 | 945,456.29 |
  | 2018-02 | 979,828.63 | 837,895.43 |
  | 2018-03 | 1,152,736.74 | 981,051.06 |
  | 2018-04 | 1,156,303.91 | 993,592.98 |
  | 2018-05 | 1,145,748.63 | 992,871.75 |
  | 2018-06 | 1,020,494.29 | 863,265.53 |
  | 2018-07 | 1,039,880.16 | 878,044.27 |
  | 2018-08 | 996,896.15 | 848,860.10 |

  Coverage outside the complete months (payment basis): 2016-09 `136.23`, 2016-10 `51,657.53`, 2016-11 no orders, 2016-12 `19.62`, 2018-09 `166.46`, 2018-10 no valid orders.

- **required_assumption_disclosure:** The monetary basis used (payment value including freight, or merchandise value excluding freight); valid orders only; purchase-date attribution.
- **required_caveat:** (1) The dataset starts in September 2016, so there is no 2015 data. (2) 2016 coverage is sparse (4 orders in September, 324 in October, none in November, 1 in December) and is not a usable growth baseline. (3) The last complete month is 2018-08. September and October 2018 contain only residual records (16 and 4 order records, almost all canceled), which reflects the extraction cutoff rather than a fall in demand. (4) Full-year 2017 and partial-year 2018 totals are not directly comparable.
- **evaluation_rule:** Must use one acceptable interpretation, the valid-order population and purchase-date attribution; monthly or period values must match the reference for that interpretation to two decimal places. Must give an overall growth conclusion on a comparable basis: either the Jan–Aug like-for-like comparison, or a trend description through 2018-08 (strong growth through 2017, a November 2017 peak, then a broadly flat 2018). A month-over-month table without any overall growth conclusion fails `result`. Caveats (1) and (3) are required; (2) and (4) are required only if the response uses 2016 or compares full-year totals.
- **disallowed_claims:** Must not report 2015 figures or imply data exists before September 2016; describe September or October 2018 as a revenue collapse; present full-year 2017 versus partial 2018 as unqualified growth; use 2016 months as a growth baseline without flagging sparse coverage; compute month-over-month with `LAG()` over existing rows so that 2016-12 is compared with 2016-10 and labelled as month-over-month.
- **notes:** The semantics file does not define revenue (sections 2 and 6 say no canonical revenue field exists), so this is a disclosed-assumption case, not a defined case. Asking what "revenue" means before answering is over-clarification. Desirable but not required: noting that growth decelerated in 2018, with monthly payment value holding around 1.0–1.16 million. Verified in DuckDB on 2026-09-29.

## Q02

- **question:** Which product is associated with the highest freight expense, and why?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:**
  - **A (reference):** product = product category; freight expense = total `SUM(order_items.freight_value)`; valid orders.
  - **B:** product = individual `product_id`; freight expense = total freight; valid orders.
- **expected_result:**

  Interpretation A, top five categories by total freight:

  | Category | Item rows | Total freight | Avg freight per item | Rank by avg freight |
  | --- | ---: | ---: | ---: | ---: |
  | cama_mesa_banho | 11,097 | 204,422.07 | 18.42 | 45 |
  | beleza_saude | 9,634 | 181,970.65 | 18.89 | 40 |
  | moveis_decoracao | 8,298 | 172,160.99 | 20.75 | 28 |
  | esporte_lazer | 8,590 | 167,503.71 | 19.50 | 35 |
  | informatica_acessorios | 7,781 | 146,619.56 | 18.84 | 42 |

  Overall: 112,101 item rows, total freight `2,241,126.29`, average freight per item `19.99`.

  Highest average freight per item (categories with at least 100 item rows): pcs `48.45`, eletrodomesticos_2 `44.28`, moveis_quarto `42.50`, moveis_cozinha_area_de_servico_jantar_e_jardim `42.42`, moveis_escritorio `40.53`.

  Interpretation B: highest product is `d1c427060a0f73f6b889a5c7c61f2ac4` (informatica_acessorios), 341 item rows, total freight `13,680.78`.

- **required_assumption_disclosure:** Product grain (category or product_id); freight metric (total, not average); valid orders only.
- **required_caveat:** "Why" findings are associations, not causes.
- **evaluation_rule:** The "what" part must match the reference for the interpretation used. The "why" part passes if it separates volume from per-item freight, for example by showing that the top category's average freight per item (18.42) is below the overall average (19.99), so its position is driven mainly by volume. Further factors (product weight or dimensions, seller-to-customer same-state versus cross-state shipping, price) are welcome but not required, and must be framed as associations with supporting numbers.
- **disallowed_claims:** Must not state an untested cause as fact (for example "this category is expensive to ship because it is heavy" without showing weight data); allocate `payment_value` to products or categories; describe `freight_value` as Olist's or the seller's actual logistics cost without qualification (it is the freight amount charged on the order item); rank by average freight without a minimum volume, which lets a handful of items dominate.
- **notes:** `freight_value` is item-level and is split across items in multi-item orders, so category attribution is safe, unlike `payment_value`. The `sellers` table provides seller location, so seller-to-customer state is a usable distance proxy. Special packaging by specific sellers is not observable in the data and should not be rewarded as an explanation. A quick directional answer plus an offer to go deeper is the expected shape; a full multivariate study is not required. Verified in DuckDB on 2026-09-29.

## Q03

- **question:** How many orders were stopped or cancelled each month from 2017 onward, and were there any unusual spikes?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:**
  - **A (reference):** stopped or cancelled = `order_status IN ('canceled', 'unavailable')`; denominator for the rate = all order records in the purchase month. Adding `created` is also accepted if disclosed; it adds 5 orders in total (Nov 2017–Feb 2018) and does not change any conclusion.
- **expected_result:**

  | Month | All order records | Canceled | Unavailable | Stopped | Stopped rate | Rate vs median |
  | --- | ---: | ---: | ---: | ---: | ---: | ---: |
  | 2017-01 | 800 | 3 | 10 | 13 | 1.63% | 1.20 |
  | 2017-02 | 1,780 | 17 | 45 | 62 | 3.48% | 2.57 |
  | 2017-03 | 2,682 | 33 | 32 | 65 | 2.42% | 1.78 |
  | 2017-04 | 2,404 | 18 | 9 | 27 | 1.12% | 0.83 |
  | 2017-05 | 3,700 | 29 | 31 | 60 | 1.62% | 1.19 |
  | 2017-06 | 3,245 | 16 | 24 | 40 | 1.23% | 0.91 |
  | 2017-07 | 4,026 | 28 | 52 | 80 | 1.99% | 1.46 |
  | 2017-08 | 4,331 | 27 | 32 | 59 | 1.36% | 1.00 |
  | 2017-09 | 4,285 | 20 | 38 | 58 | 1.35% | 1.00 |
  | 2017-10 | 4,631 | 26 | 58 | 84 | 1.81% | 1.34 |
  | 2017-11 | 7,544 | 37 | 84 | 121 | 1.60% | 1.18 |
  | 2017-12 | 5,673 | 11 | 42 | 53 | 0.93% | 0.69 |
  | 2018-01 | 7,269 | 34 | 48 | 82 | 1.13% | 0.83 |
  | 2018-02 | 6,728 | 73 | 30 | 103 | 1.53% | 1.13 |
  | 2018-03 | 7,211 | 26 | 17 | 43 | 0.60% | 0.44 |
  | 2018-04 | 6,939 | 15 | 5 | 20 | 0.29% | 0.21 |
  | 2018-05 | 6,873 | 24 | 16 | 40 | 0.58% | 0.43 |
  | 2018-06 | 6,167 | 18 | 4 | 22 | 0.36% | 0.26 |
  | 2018-07 | 6,292 | 41 | 18 | 59 | 0.94% | 0.69 |
  | 2018-08 | 6,512 | 84 | 7 | 91 | 1.40% | 1.03 |
  | 2018-09 | 16 | 15 | 0 | 15 | 93.75% | coverage artifact |
  | 2018-10 | 4 | 4 | 0 | 4 | 100.00% | coverage artifact |

  Median monthly stopped rate across complete months (2017-01 to 2018-08): `1.36%`. Reference spike: **2017-02** (3.48%, 2.57 × median). The same month, and only that month, is flagged by the mean + 2 SD threshold (2.84%) and the 1.5 × IQR upper fence (2.65%). 2017-03 (2.42%) is elevated but below all three thresholds.

- **required_assumption_disclosure:** The definition of "stopped or cancelled"; that months are purchase months (the dataset has no cancellation timestamp); the spike rule used.
- **required_caveat:** September and October 2018 show near-100% rates because only a handful of residual records exist after the extraction cutoff. These are coverage artifacts, not operational spikes.
- **evaluation_rule:** Monthly stopped counts for 2017-01 to 2018-08 must match the reference. The tail months may be shown or excluded, but must be explained either way. Spikes must be judged on the rate (or on counts explicitly normalised for volume). Any reasonable, explicitly stated spike rule is accepted; the response must either flag 2017-02 or explain why its stated rule does not. Must flag the 2018 tail as a coverage artifact.
- **disallowed_claims:** Must not report September or October 2018 as unusual spikes or operational problems; call November 2017 a spike on raw count alone (121 is the highest stopped count, but the rate of 1.60% is normal because order volume peaked that month); claim that the month shown is when the cancellation happened; state a cause for the February 2017 spike without evidence.
- **notes:** Desirable but not required: noting a composition shift. `unavailable` falls sharply in 2018 while `canceled` in August 2018 (84) is the highest canceled count in the series, roughly three times the typical month, even though the combined stopped rate looks normal. Reporting the two statuses separately surfaces this. A chart is a legitimate way to set the answer key; the model is not required to produce one. Verified in DuckDB on 2026-09-29.

## Q04

- **question:** Across our customers, how many placed only one valid order, two valid orders, and three or more valid orders?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `defined`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** 92,099 customers placed one valid order; 2,651 placed two valid orders; 236 placed three or more valid orders.
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must use `customer_unique_id` as the customer grain, count valid orders using the benchmark valid-order definition, and return the three customer buckets matching the reference results. Equivalent SQL is acceptable.
- **disallowed_claims:** Must not use `customer_id` as the customer identity across orders, because `customer_id` is order-specific in this dataset. Must not include canceled, unavailable or created orders in the valid-order count.
- **notes:** There are 94,986 customers with at least one valid order under this definition, of whom 2,887 have at least two valid orders.

## Q05

- **question:** Year by year, which sellers sold the most products?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:**
  - **A (reference):** units sold = count of `order_items` rows per `seller_id` per purchase year, valid orders.
- **expected_result:**

  | Purchase Year | Top Seller | Units Sold |
  | ---: | --- | ---: |
  | 2016 | `620c87c171fb2a6dd6e8bb4dec959fc6` | 24 |
  | 2017 | `cc419e0650a3c5ba77189a1882b7556a` | 1,258 |
  | 2018 | `955fee9216a65b617aa5c0531780ce60` | 1,274 |

- **required_assumption_disclosure:** That "most products" is measured as units sold (item rows); valid orders only; purchase year is based on `order_purchase_timestamp`.
- **required_caveat:**
- **evaluation_rule:** The top seller in each year must match the reference, and any Top N returned must match the first N rows of the reference ranking for that year. No fixed N is required.
- **disallowed_claims:** Must not rank by distinct product count, order count or merchandise sales while presenting it as "products sold" without disclosure; must not include non-valid orders.
- **notes:** Paired with Q14. Ranking by merchandise sales gives a different top seller in 2017 and 2018, so mentioning that alternative is desirable. 2016 has very little data (the top seller sold 24 units), so a note on sparse 2016 coverage is desirable but not required. No first-place ties were returned. Verified in DuckDB on 2026-09-29.

## Q06

- **question:** Which products are the most competitive?
- **expected_behavior:** `clarify`
- **ambiguity_handling:** `clarify`
- **reference_sql:** N/A
- **expected_result:** N/A
- **expected_clarification:** Ask what "competitive" should mean, offering the plausible definitions supported by the data, for example sales or units, growth, price relative to similar products, review score, or delivery performance, or ask what decision the ranking will support.
- **required_caveat:**
- **evaluation_rule:** Pass if the response asks one focused clarification (optionally with a short list of options) before giving a final ranking. A brief provisional view across two or three metrics is acceptable if clearly labelled provisional and followed by the question. Fail if the response presents a single ranking built on one silently chosen definition, invents a composite "competitiveness score" without asking, or asks a long series of specification questions.
- **disallowed_claims:** Must not present any single metric as "the" measure of competitiveness.
- **notes:** Undefined business concept: no semantic definition, no dominant default, and the rankings under different definitions have little overlap.

## Q07

- **question:** What percentage of delivered orders arrived on time?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `defined`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** 89,936 of 96,470 eligible delivered orders arrived on or before the estimated delivery date, giving an on-time delivery rate of 93.23%.
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must restrict the population to delivered orders with usable actual and estimated customer delivery dates. An order counts as on time when the actual customer delivery date is on or before the estimated delivery date. The numerator, denominator and resulting rate must match the reference result, allowing normal rounding.
- **disallowed_claims:** Must not include undelivered orders in the denominator; must not use carrier handoff date as the customer delivery date; must not classify delivery on the estimated date as late.
- **notes:** The benchmark compares the two fields at calendar-date grain because `order_estimated_delivery_date` has no meaningful time-of-day precision. A literal timestamp comparison produces `88,644 / 96,470 = 91.89%`; this is a date-boundary failure signature because it incorrectly classifies 1,292 orders delivered later on their estimated date as late.

## Q08

- **question:** For orders that were handed over to the carrier, on average, how long did it take from order placement to carrier handoff?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `defined`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** Average elapsed time from order placement to carrier handoff is `3.23 days`.
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must measure elapsed time from `order_purchase_timestamp` to `order_delivered_carrier_date` for orders where carrier handoff is observed. Apply the global elapsed-duration evaluation rule; the average must be within ±0.1 day of the 3.23-day reference.
- **disallowed_claims:** Must not start the interval from approval or another later timestamp; must not use customer delivery date as carrier handoff; must not exclude weekends unless the question explicitly asks for business days.
- **notes:** `order_delivered_carrier_date IS NOT NULL` directly defines the observed carrier-handoff population. The reference SQL therefore does not additionally filter current `order_status`. There are 166 source records in which carrier handoff precedes the purchase timestamp; the reference retains them, so the average describes the observed data and should not be interpreted as a clean operational SLA without a separate data-quality policy.

## Q09

- **question:** On average, how long does it take from order placement until the customer receives the order?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `defined`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** Average elapsed time from order placement to customer receipt is `12.56 days`.
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must measure elapsed time from `order_purchase_timestamp` to `order_delivered_customer_date` for delivered orders with usable timestamps. Apply the global elapsed-duration evaluation rule; the average must be within ±0.1 day of the 12.56-day reference. An implementation that relies on non-null `order_delivered_customer_date` rather than explicitly filtering `order_status = 'delivered'` remains acceptable if it produces an in-tolerance result on the appropriate observed-delivery population.
- **disallowed_claims:** Must not start the interval at carrier handoff; must not use estimated delivery date as the actual delivery date; must not include orders without a usable customer delivery timestamp.
- **notes:** The reference SQL explicitly filters `order_status = 'delivered'` to make the semantic population clear. Filtering only on non-null `order_delivered_customer_date` yields 96,476 rows rather than 96,470; the rounded average remains 12.56 days, but the populations are not identical.

## Q10

- **question:** Which customer cities generated the most valid orders?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `defined`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:**

  | Rank | Customer City | Valid Orders |
  | ---: | --- | ---: |
  | 1 | `sao paulo` | 15,291 |
  | 2 | `rio de janeiro` | 6,800 |
  | 3 | `belo horizonte` | 2,737 |
  | 4 | `brasilia` | 2,111 |
  | 5 | `curitiba` | 1,502 |
  | 6 | `campinas` | 1,422 |
  | 7 | `porto alegre` | 1,370 |

- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must count valid orders by `customer_city` using the benchmark valid-order definition and sort descending by order count. No fixed Top N is required. If the response returns Top N cities, those rows and counts must match the first N rows of the reference ranking.
- **disallowed_claims:** Must not count canceled, unavailable or created orders as valid; must not group by seller city or another geography while presenting it as customer city; must not count customer rows instead of orders.
- **notes:** `sao paulo` is the clear highest-volume customer city in the dataset, followed by `rio de janeiro`.

## Q11

- **question:** What was our most popular product each year?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:**
  - **A (reference):** popular = units sold (item rows); product = `product_id`; valid orders; purchase year.
  - **B:** popular = units sold (item rows); product = product category; valid orders; purchase year.
- **expected_result:**

  Interpretation A (reference):

  | Purchase Year | Most Popular Product ID | Units Sold |
  | ---: | --- | ---: |
  | 2016 | `eba7488e1c67729f045ab43fac426f2e` | 9 |
  | 2017 | `99a4788cb24856965c36a24e339b6058` | 359 |
  | 2018 | `aca2eb7d00ea1a7b8ebd4e68314663af` | 413 |

  Interpretation B — product category ranked by units sold:

  | Purchase Year | Most Popular Product Category | Units Sold |
  | ---: | --- | ---: |
  | 2016 | `moveis_decoracao` | 69 |
  | 2017 | `cama_mesa_banho` | 5,216 |
  | 2018 | `beleza_saude` | 5,924 |

- **required_assumption_disclosure:** That popularity is measured by units sold; the product grain used; valid orders.
- **required_caveat:**
- **evaluation_rule:** The top product (or category) in each year must match the reference for the interpretation used.
- **disallowed_claims:** Must not rank by review count, revenue or order count without disclosing that choice; must not include non-valid orders.
- **notes:** Interpretation A is consistent with Q14's "individual products" and is the primary reference interpretation. Interpretation B (product category by units sold) remains acceptable if disclosed. Both interpretations now have verified reference queries and expected results. No first-place ties were returned under either interpretation. Noting that 2016 rankings rest on very few orders is desirable. Interpretation A verified in DuckDB on 2026-09-29; Interpretation B verified in DuckDB on 2026-10-10.

## Q12

- **question:** What factors are associated with longer customer delivery times?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:** Delivery time is defined by the semantics (purchase to customer delivery, delivered orders only). The choice of factors is open; the model may choose any factors supported by the data.
- **expected_result:** Rubric-graded rather than one fixed answer. Reference findings:
  1. **Customer geography:** Customer state is strongly associated with delivery time. RR averages `29.39` days across 41 orders, AP `27.18` across 67, and AM `26.43` across 145. State-level differences are driven primarily by post-handoff transit rather than pre-carrier handoff.
  2. **Seller-to-customer geography:** The reference restricts this comparison to single-seller orders because delivery timestamps are order-level. Same-state shipments average `7.97` days across 34,234 orders, versus `15.21` days across 60,960 different-state orders. Pre-carrier time is similar (`3.15` vs `3.29` days), while post-handoff transit differs substantially (`4.81` vs `11.92` days).
  3. **Order item count:** Overall delivery time remains broadly stable at approximately `11.6–12.6` days. Pre-carrier handoff rises directionally from `3.20` days for one-item orders to `4.78` days for orders with more than five items, but more items are not associated with longer end-to-end delivery.
  4. **Physical shipment characteristics:** Weight shows a moderate positive association: `<=200g` orders average `11.74` days versus `14.07` days for `>5000g`. Cubic volume supports the same pattern: the smallest band averages `11.60` days and the largest averages `14.26` days across 7,629 orders. These physical-size associations are materially weaker than the geographic associations.
- **required_assumption_disclosure:** State that delivery time is measured from `order_purchase_timestamp` to `order_delivered_customer_date`; the population is delivered orders with usable timestamps; which candidate factors were examined; and that findings are associations rather than causal effects. If seller-to-customer geography is analysed, disclose how multi-seller orders were handled. The reference restricts that analysis to single-seller orders to preserve one observation per order.
- **required_caveat:** Findings are associations, not causes, and factors may correlate with one another. Remote customer states may have more cross-state shipments; heavier orders may contain more items; and physical characteristics may differ by category or seller. Small geographic groups must also be interpreted with their sample sizes in mind.
- **evaluation_rule:** Pass if the response uses `order_purchase_timestamp → order_delivered_customer_date` on delivered orders; examines at least three factors available in the dataset; reports sample sizes for compared groups; identifies customer geography as materially associated with longer delivery time; compares groups rather than relying on anecdotes; and frames conclusions as associations. The model need not choose exactly the reference factors, and different reasonable factors or bucket definitions are acceptable. If it analyses a reference factor using materially the same definition, its result should be consistent with the reference. Asking the stakeholder which factors to analyse before attempting the exploration is an over-clarification failure.
- **disallowed_claims:** Must not claim that an observed factor causes longer delivery times; start the overall interval at `order_delivered_carrier_date`; include undelivered orders; cite unavailable variables such as carrier identity, traffic, weather, customer-service contacts, order changes or holidays as observed findings; describe pre-carrier time as pure seller preparation time; attribute post-handoff time to a specific logistics company; duplicate multi-seller orders across seller-state groups without addressing the grain issue; infer unobserved explanations such as rural infrastructure or labour shortages; or present item count, weight or volume associations as independent causal effects.
- **notes:** Q12 intentionally evaluates exploratory analytical reasoning rather than one exact SQL result. The reference dimensions are customer geography, seller-to-customer geography, order item count, and physical shipment characteristics. The strongest finding is geographic: longer delivery time is primarily associated with longer post-handoff transit. Weight and cubic volume are two checks within one broader physical-shipment factor. All reference decompositions use delivered orders with non-null purchase, carrier-handoff and customer-delivery timestamps and minute-level elapsed durations as the canonical implementation; equivalent second-, hour-, or interval-based elapsed-time calculations are acceptable.

## Q13

- **question:** Which products are the most expensive?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:**
  - **A (reference):** product = `product_id`; expensive = average selling price, `AVG(order_items.price)`; valid orders.
  - **B:** product = `product_id`; expensive = maximum observed selling price, `MAX(order_items.price)`; valid orders.
- **expected_result:**

  Interpretation A — individual products ranked by average selling price:

  | Rank | Product ID | Units Sold | Average Price |
  | ---: | --- | ---: | ---: |
  | 1 | `489ae2aa008f021502940f251d4cce7f` | 1 | 6,735.00 |
  | 2 | `69c590f7ffc7bf8db97190b6cb6ed62e` | 1 | 6,729.00 |
  | 3 | `1bdf5e6731585cf01aa8169c7028d6ad` | 1 | 6,499.00 |
  | 4 | `a6492cc69376c469ab6f61d8f44de961` | 1 | 4,799.00 |
  | 5 | `c3ed642d592594bb648ff4a04cee2747` | 1 | 4,690.00 |
  | 6 | `259037a6a41845e455183f89c5035f18` | 1 | 4,590.00 |
  | 7 | `a1beef8f3992dbd4cd8726796aa69c53` | 1 | 4,399.87 |
  | 8 | `6cdf8fc1d741c76586d8b6b15e9eef30` | 1 | 4,099.99 |
  | 9 | `6902c1962dd19d540807d0ab8fade5c6` | 1 | 3,999.90 |
  | 10 | `4ca7b91a31637bd24fb8e559d5e015e4` | 1 | 3,999.00 |

  Interpretation B — individual products ranked by maximum observed selling price:

  | Rank | Product ID | Units Sold | Maximum Price |
  | ---: | --- | ---: | ---: |
  | 1 | `489ae2aa008f021502940f251d4cce7f` | 1 | 6,735.00 |
  | 2 | `69c590f7ffc7bf8db97190b6cb6ed62e` | 1 | 6,729.00 |
  | 3 | `1bdf5e6731585cf01aa8169c7028d6ad` | 1 | 6,499.00 |
  | 4 | `a6492cc69376c469ab6f61d8f44de961` | 1 | 4,799.00 |
  | 5 | `c3ed642d592594bb648ff4a04cee2747` | 1 | 4,690.00 |
  | 6 | `259037a6a41845e455183f89c5035f18` | 1 | 4,590.00 |
  | 7 | `a1beef8f3992dbd4cd8726796aa69c53` | 1 | 4,399.87 |
  | 8 | `6cdf8fc1d741c76586d8b6b15e9eef30` | 1 | 4,099.99 |
  | 9 | `dd113cb02b2af9c8e5787e8f1f0722f6` | 2 | 4,059.00 |
  | 10 | `6902c1962dd19d540807d0ab8fade5c6` | 1 | 3,999.90 |

- **required_assumption_disclosure:** Product grain; whether average or maximum price is used; that freight is excluded.
- **required_caveat:**
- **evaluation_rule:** Top N returned must match the first N rows of the reference ranking for the interpretation used. No fixed N is required.
- **disallowed_claims:** Must not rank by summed price (that is merchandise sales, Q24's measure), include freight in price, introduce median price as a third accepted interpretation, rank product categories, or impose an unsupported minimum-sales threshold.
- **notes:** Paired with Q24. 5,900 products have more than one distinct price across orders, which is why average versus maximum must be stated. The top of the ranking consists mostly of products sold once, which is acceptable because Q13 tests metric interpretation rather than ranking robustness. Verified in DuckDB on 2026-09-29.

## Q14

- **question:** Which individual products sold the most units?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `defined`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:**

  | Rank | Product ID | Units Sold |
  | ---: | --- | ---: |
  | 1 | `aca2eb7d00ea1a7b8ebd4e68314663af` | 527 |
  | 2 | `99a4788cb24856965c36a24e339b6058` | 487 |
  | 3 | `422879e10f46682990de24d770e7f83d` | 484 |
  | 4 | `389d119b48cf3043d311335e499d9c6b` | 391 |
  | 5 | `368c6c730842d78016ad823897a372db` | 388 |
  | 6 | `53759a2ecddad2bb87a079a1f1519f73` | 373 |
  | 7 | `d1c427060a0f73f6b889a5c7c61f2ac4` | 341 |
  | 8 | `53b36df67ebb7c41585e8d54d6772e08` | 323 |
  | 9 | `154e7e31ebfa092203795c972e5804a6` | 281 |
  | 10 | `3dd2a17168ec895c781a9191c1e95ad7` | 274 |

- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must rank `product_id` by count of valid-order `order_items` rows. No fixed Top N is required. If Top N products are returned, their IDs and unit counts must match the first N rows of the reference ranking.
- **disallowed_claims:** Must not rank by order count, distinct customer count, revenue, average price or distinct seller count while presenting the result as units sold; must not include non-valid orders.
- **notes:** Each `order_items` row represents one product unit, so `COUNT(*)` at `product_id` grain is the correct unit-volume measure.

## Q15

- **question:** How has our profitability changed year over year?
- **expected_behavior:** `insufficient_data`
- **ambiguity_handling:** `n/a`
- **reference_sql:** N/A
- **expected_result:** N/A.
- **expected_clarification:** N/A.
- **required_caveat:** Transaction-value metrics such as merchandise value, payment value or freight amount are not profit and should not be interpreted as profitability.
- **evaluation_rule:** Pass if the response explains that profitability cannot be reliably calculated from the available dataset because platform revenue and cost components are missing. It should identify at least the need for platform monetisation data such as commission / take rate or other platform revenue and relevant costs. It may offer transaction-value trends as an alternative analysis, but must clearly distinguish them from profit.
- **disallowed_claims:** Must not treat `payment_value` as profit or platform revenue without supporting data; must not treat `order_items.price` as platform revenue; must not treat `freight_value` as logistics profit or logistics cost; must not invent a profit metric such as `price - freight_value`; must not infer profitability trends from GMV or payment growth alone.
- **notes:** The dataset contains transaction-value information but no reliable platform P&L structure. GMV, merchandise value and customer payment value can describe business scale but cannot answer how profitability changed over time.

## Q16

- **question:** What is our customer cancellation rate?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:**
  - **A (reference): order-level cancellation rate** = orders with `order_status = 'canceled'` / all order records (all statuses).
  - **B: customer-level cancellation incidence** = distinct `customer_unique_id` with at least one canceled order / all distinct `customer_unique_id` represented by at least one order record (all statuses).
- **expected_result:**

  | Interpretation | Numerator | Denominator | Rate |
  | --- | ---: | ---: | ---: |
  | A: order-level | 625 canceled orders | 99,441 order records | 0.63% |
  | B: customer-level | 616 customers with ≥1 canceled order | 96,096 customers | 0.64% |

- **required_assumption_disclosure:** Analytical grain (order-level or customer-level); numerator definition; denominator definition.
- **required_caveat:** The dataset does not record who initiated a cancellation, so the metric cannot distinguish customer-, seller- or platform-initiated cancellations and cannot be read as specifically customer-initiated cancellation.
- **evaluation_rule:** Pass if the response explicitly states whether cancellation is measured at order grain or customer grain, uses the corresponding documented numerator and denominator, and returns the reference result for that interpretation to two decimal places. Because A and B are numerically close in this dataset, grade against the grain the response states and the SQL it runs, not the number alone. A clearly labelled supplementary failed/stopped-order rate (canceled + unavailable, 1.24%) may accompany A or B, but it cannot replace them as the answer.
- **disallowed_claims:** Must not silently combine `canceled` and `unavailable` and present the result as cancellation rate; must not mix order and customer grain (for example a customer-count numerator over an order-count denominator); must not use the valid-order population as the denominator (it excludes canceled orders by definition); must not use `customer_id` as customer identity for interpretation B; must not claim the rate reflects customer-initiated cancellations.
- **notes:** Paired with Q35, which states the denominator explicitly. `unavailable` may reflect inventory, fulfilment or availability failure and is not inherently a cancellation, so canceled + unavailable is a broader failed/stopped-order metric that must be labelled as such (contrast Q03, where the question itself asks for "stopped or cancelled"). The two grains coincide closely here because most customers place a single order; in a business with more repeat purchasing they can diverge sharply, which is why the grain must be disclosed. Verified in DuckDB on 2026-09-29.

## Q17

- **question:** Which products have the highest customer review ratings?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:**
  - **A:** product = individual `product_id`; average `review_score`; uniquely mapped reviews attributed once to each distinct product in the order; declared minimum review count from 20 to 100 inclusive. The table below is the canonical example at `n >= 30`, not the only accepted result.
- **expected_result:**

  | Rank | Product ID | Review Count | Average Review Score |
  | ---: | --- | ---: | ---: |
  | 1 | `73326828aa5efe1ba096223de496f596` | 53 | 4.8491 |
  | 2 | `6a8631b72a2f8729b91514db87e771c0` | 57 | 4.7368 |
  | 3 | `dd6a505f83dd3c6326aa9856519e0978` | 36 | 4.6944 |
  | 4 | `f8b624d4e475bb8d1bddf1b65c6a64f6` | 42 | 4.6905 |
  | 5 | `aadff88486740e0b0ebe2be6c09476ae` | 40 | 4.6500 |
  | 6 | `fbc1488c1a1e72ba175f53ab29a248e8` | 55 | 4.6364 |
  | 7 | `aa280035c50ba62c746480a59045eec4` | 46 | 4.6304 |
  | 8 | `6109d0cae3bcb57d579bc0fab6e61814` | 37 | 4.6216 |
  | 9 | `57e089e3103f5cda6a4ce23b77399bdb` | 42 | 4.6190 |
  | 10 | `5328338cfaa16ba10561cd970c73ca11` | 34 | 4.6176 |

- **required_assumption_disclosure:** Product grain = individual `product_id`; the minimum review-count threshold used; order-level reviews are attributed to products in the order.
- **required_caveat:** An order-level review is not necessarily product-specific feedback when an order contains multiple products. A minimum-count threshold reduces small-sample noise but does not by itself establish statistical significance.
- **evaluation_rule:** Use submitted review records regardless of current order status. The response must declare an integer minimum review-count threshold from 20 to 100 inclusive. Exclude any `review_id` mapping to multiple distinct orders; attribute each retained review once to each distinct `product_id` in its order; rerun the parameterised reference query using the declared threshold; and match that descending ranking. Top N is acceptable if it matches the first N rows produced at the same threshold. A missing or out-of-range threshold fails assumption transparency and result correctness.
- **disallowed_claims:** Must not apply a valid-order filter unless the question explicitly requests one; rank products without a reasonable minimum review count; count the same review more than once for the same product; assign ambiguous `review_id` mappings to all candidate orders; arbitrarily choose one order for an ambiguous review; or describe order-level reviews as direct product-specific ratings without qualification.
- **notes:** Review-grain flow: uniquely mapped `review_id` → one order → distinct order-product relationship → one review contribution per product → declared minimum review-count threshold → average score → rank. The accepted threshold range is frozen at 20–100 inclusive; `30` remains the canonical example. `789` review IDs map ambiguously to multiple orders, affecting `1,603` source rows; their scores and timestamps are internally consistent, but correct order attribution is unknown, so they are excluded. `SELECT DISTINCT order_id, product_id` prevents multiple units of one product from multiplying review weight. Verified in DuckDB on 2026-09-29; threshold sensitivity reverified on 2026-10-02.

## Q18

- **question:** Which sellers are associated with the lowest customer review ratings?
- **expected_behavior:** `execute_sql`
- **ambiguity_handling:** `disclosed_assumption`
- **reference_sql:** see `reference-queries.sql`
- **acceptable_interpretations:**
  - **A:** `seller_id` grain; average `review_score`; uniquely mapped reviews attributed once to each distinct seller in the order; declared minimum review count from 20 to 100 inclusive. The table below is the canonical example at `n >= 30`, not the only accepted result.
- **expected_result:**

  | Rank | Seller ID | Review Count | Average Review Score |
  | ---: | --- | ---: | ---: |
  | 1 | `1ca7077d890b907f89be8c954a02686a` | 113 | 2.3451 |
  | 2 | `2eb70248d66e0e3ef83659f71b244378` | 197 | 2.6954 |
  | 3 | `a49928bcdf77c55c6d6e05e09a9b4ca5` | 96 | 2.9688 |
  | 4 | `972d0f9cf61b499a4812cf0bfa3ad3c4` | 78 | 3.0000 |
  | 5 | `dc8798cbf453b7e0f98745e396cc5616` | 40 | 3.0250 |
  | 6 | `54965bbe3e4f07ae045b90b0b8541f52` | 73 | 3.0274 |
  | 7 | `ad781527c93d00d89a11eecd9dcad7c1` | 43 | 3.1163 |
  | 8 | `2a1348e9addc1af5aaa619b1a3679d6b` | 51 | 3.1176 |
  | 9 | `602044f2c16190c2c6e45eb35c2e21cb` | 49 | 3.1429 |
  | 10 | `bbad7e518d7af88a0897397ffdca1979` | 68 | 3.1618 |

- **required_assumption_disclosure:** Seller grain = `seller_id`; the minimum review-count threshold used; order-level reviews are attributed to seller(s) associated with the order.
- **required_caveat:** "Associated with" lower ratings does not mean the seller caused them; reviews also reflect delivery and platform experience.
- **evaluation_rule:** Use submitted review records regardless of current order status. The response must declare an integer minimum review-count threshold from 20 to 100 inclusive. Exclude any `review_id` mapping to multiple distinct orders; attribute each retained review once to each distinct `seller_id` in its order; rerun the parameterised reference query using the declared threshold; and match that ascending ranking. Top N is acceptable if it matches the first N rows produced at the same threshold. A missing or out-of-range threshold fails assumption transparency and result correctness.
- **disallowed_claims:** Must not apply a valid-order filter unless the question explicitly requests one; rank sellers without a reasonable minimum review count; count the same review multiple times for the same seller; assign ambiguous `review_id` mappings to all candidate orders; arbitrarily choose one order for an ambiguous review; or claim that a seller caused the low review score.
- **notes:** Review-grain flow: uniquely mapped `review_id` → one order → distinct order-seller relationship → one review contribution per seller → declared minimum review-count threshold → average score → rank. The accepted threshold range is frozen at 20–100 inclusive; `30` remains the canonical example. `SELECT DISTINCT order_id, seller_id` prevents multiple item rows from one seller from multiplying review weight. Submitted reviews are retained regardless of current order status, and the attribution remains associative rather than causal. Verified in DuckDB on 2026-09-29; threshold sensitivity reverified on 2026-10-02.

## Q19

- **question:** How many order records are in the dataset?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** `99441`
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must return exactly `99441` by counting rows in the base `orders` table.
- **disallowed_claims:**
- **notes:** Basic SQL control question testing a simple aggregation; no special business semantics are required.

## Q20

- **question:** How many valid orders do we have?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** `98202`
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must return exactly `98202` using the documented valid-order statuses: `approved`, `invoiced`, `processing`, `shipped`, and `delivered`. `created`, `canceled`, and `unavailable` must be excluded.
- **disallowed_claims:** Must not invent a different valid-order definition or include excluded statuses.
- **notes:** Tests use of the documented valid-order population. Because `order_id` is unique in `orders`, `COUNT(DISTINCT order_id)` is unnecessary but produces the same result.

## Q21

- **question:** How many unique customers placed at least one valid order?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** `94986`
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must return exactly `94986` by joining `customers` to valid orders and counting distinct `customer_unique_id` values.
- **disallowed_claims:** Must not use `customer_id` as the identity of a unique real customer across orders.
- **notes:** Tests customer identity and analytical grain. `customer_id` identifies an order-specific customer record and would overcount unique customers.

## Q22

- **question:** How many valid orders did we receive each month in 2017?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:**

  | Month | Valid Orders |
  | ---: | ---: |
  | 1 | 787 |
  | 2 | 1,718 |
  | 3 | 2,617 |
  | 4 | 2,377 |
  | 5 | 3,640 |
  | 6 | 3,205 |
  | 7 | 3,946 |
  | 8 | 4,272 |
  | 9 | 4,227 |
  | 10 | 4,547 |
  | 11 | 7,421 |
  | 12 | 5,618 |

- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must match all 12 monthly counts, include only documented valid-order statuses, and attribute orders to months using `order_purchase_timestamp`.
- **disallowed_claims:** Must not use `order_approved_at` for monthly attribution under the current business semantics.
- **notes:** Tests both population definition and time attribution. Purchase timestamp is the project's commercial/customer analytics attribution convention.

## Q23

- **question:** What was our merchandise sales each month in 2017?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:**

  | Month | Merchandise Sales |
  | ---: | ---: |
  | 1 | 120,098.27 |
  | 2 | 244,959.35 |
  | 3 | 368,341.32 |
  | 4 | 353,842.98 |
  | 5 | 503,159.19 |
  | 6 | 429,916.61 |
  | 7 | 492,287.30 |
  | 8 | 568,245.79 |
  | 9 | 621,415.91 |
  | 10 | 660,179.62 |
  | 11 | 1,003,862.14 |
  | 12 | 742,183.79 |

- **expected_clarification:**
- **required_caveat:** This is a commercial analytics convention for the case study and must not be interpreted as accounting revenue recognition.
- **evaluation_rule:** Must match all 12 monthly values to two decimal places using `SUM(order_items.price)`, valid orders only, and `order_purchase_timestamp` for monthly attribution.
- **disallowed_claims:** Must not use `COUNT(product_id)` as merchandise sales, substitute `SUM(payment_value)`, attribute by `order_approved_at`, or describe the result as accounting revenue.
- **notes:** Tests the combined application of metric semantics, valid-order population, time attribution, and the correct table join.

## Q24

- **question:** Which product categories generated the highest merchandise sales?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** Highest-ranked category: `beleza_saude` (`1255695.13` merchandise sales).
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** The highest-ranked category must be correct and results must be ordered by merchandise sales descending. If Top N rows are returned, they must match the first N rows of the reference ranking; no fixed N is required. The sales value is desirable but not required. Must use `SUM(order_items.price)`, the valid-order population, and the product-to-category join.
- **disallowed_claims:** Must not include all order statuses merely because the question does not explicitly say “valid orders,” and must not substitute payment value, freight value, or item count for merchandise sales.
- **notes:** Portuguese-to-English category translation is a presentation improvement, not a pass/fail requirement.

## Q25

- **question:** Which sellers generated the highest merchandise sales?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** Highest-ranked seller: `4869f7a5dfa277a7dca6462dcf3b52b2` (`229237.63` merchandise sales).
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** The highest-ranked seller must be correct and results must be ordered by merchandise sales descending. If Top N rows are returned, they must match the first N rows of the reference ranking; no fixed N is required. The sales value is desirable but not required. Must use `SUM(order_items.price)`, the valid-order population, and seller grain.
- **disallowed_claims:** Must not include all order statuses merely because the question does not explicitly say “valid orders,” and must not substitute payment value, freight value, or item count for merchandise sales.
- **notes:** Uses the same general ranking rule as Q24.

## Q26

- **question:** How many orders contained more than one item?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** `9761`
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must return exactly `9761`. Use the valid-order population, group item records by `order_id`, identify orders with `COUNT(order_item_id) > 1`, then count those orders.
- **disallowed_claims:** Must not include canceled, unavailable, or created orders. Must not use `COUNT(product_id)` as the definition of item-record count.
- **notes:** Tests item grain, the default order population, and grouping at order level. `order_item_id` directly represents item-line identity; `product_id` is a potentially nullable attribute.

## Q27

- **question:** How many orders had more than one payment record?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** `2920`
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must return exactly `2920`. Use the valid-order population, group payment rows by `order_id`, identify orders with `COUNT(*) > 1`, then count those orders.
- **disallowed_claims:** Must not include canceled, unavailable, or created orders; use `COUNT(payment_type)` or `COUNT(DISTINCT payment_type)` to define payment-record count; or infer the record count from `MAX(payment_sequential)`.
- **notes:** Tests payment grain, the default order population, and direct counting of payment records. `payment_type` is an attribute, while non-standard payment sequence values make `MAX(payment_sequential)` unreliable for this purpose.

## Q28

- **question:** How did the number of valid orders change from 2017 to 2018?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** 2017 valid orders: `44375`; 2018 valid orders: `53531`; absolute change: `+9156`; percentage change: `+20.63%`.
- **expected_clarification:**
- **required_caveat:** If either year has incomplete time coverage, explicitly state that the raw annual totals are not a like-for-like full-year comparison. The numerical difference may be reported, but it must not be interpreted as genuine full-year YoY growth or decline without qualification.
- **evaluation_rule:** Must use the valid-order population and `order_purchase_timestamp` for year attribution; correctly report the verified 2017 and 2018 totals, absolute change, percentage change, direction, and magnitude; and surface any coverage limitation. Equivalent SQL is acceptable.
- **disallowed_claims:** Must not interpret incomplete-year totals as a comparable full-year YoY trend.
- **notes:** The reference uses `GROUP BY` year plus `LAG()` because it scales to additional years. Conditional aggregation is also valid for a fixed two-period comparison. Time coverage is validated separately.

## Q29

- **question:** What percentage of valid orders have no customer review?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** Total valid orders: `98202`; valid orders without a review: `732`; percentage without a review: `0.75%`.
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** The denominator must be all valid orders and the numerator must be valid orders for which no review record exists. Review absence must be evaluated at `order_id` grain, with protection against multiple review rows per order. Must return the verified percentage; `LEFT JOIN`, `NOT EXISTS`, or another logically equivalent approach is acceptable.
- **disallowed_claims:** Must not use an inner join that drops orders without reviews or allow multiple review records to inflate the denominator or reviewed-order count.
- **notes:** Tests valid-order population, missing-record detection, denominator control, and one-to-many join protection.

## Q30

- **question:** Which marketing channels generated the most valid orders?
- **expected_behavior:** `insufficient_data`
- **reference_sql:** N/A
- **expected_result:** N/A — the available dataset does not contain marketing-channel attribution data.
- **expected_clarification:**
- **required_caveat:** Explain that answering this question would require a reliable order/customer mapping to acquisition source, campaign, referral source, ad platform, or another documented marketing touchpoint.
- **evaluation_rule:** Pass if the response explicitly identifies that marketing-channel attribution is unavailable, names relevant missing acquisition/marketing inputs, and avoids unsupported proxies or hallucinated fields. Fail if it produces a channel ranking or numerical answer without sufficient evidence.
- **disallowed_claims:** Must not invent acquisition or campaign fields, or substitute customer state, seller, product category, payment type, customer location, or another unrelated dimension as a marketing-channel proxy without an explicit documented mapping.
- **notes:** Tests schema-boundary recognition, insufficient-data recognition, identification of missing inputs, and avoidance of unsupported proxy substitution. The response may optionally describe related analyses that remain possible with the available data.

## Q31

- **question:** For valid orders in 2017 that contained more than one item, what was the average amount paid per order?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** Total target orders: `4426`; orders with payment: `4426`; orders without payment: `0`; average amount paid: `246.93`.
- **expected_clarification:**
- **required_caveat:** `SUM(order_items.price) + SUM(order_items.freight_value)` is a reconstructed order value, not the same business measure as recorded customer payment. A numerically close result does not make the two definitions interchangeable.
- **evaluation_rule:** Must use valid orders purchased in 2017 according to `order_purchase_timestamp`; identify multi-item orders at order-item grain; aggregate `order_payments.payment_value` to one row per order before averaging across target orders; and return approximately `246.93`.
- **disallowed_claims:** Must not define amount paid as `price + freight`, directly join item and payment rows in a way that amplifies values, average individual payment rows instead of order-level payment totals, ignore the valid-order filter, or use the wrong timestamp for 2017 attribution.
- **notes:** Tests valid-order population, time attribution, multi-item order grain, payment semantics, order-level pre-aggregation, join-amplification avoidance, and payment-data completeness. All `4426` target orders have a payment record.

## Q32

- **question:** Among repeat customers, what was the average number of days between their first and second valid orders?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** Average days between first and second valid orders: `80.79`.
- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** Must use `customer_unique_id`, restrict the population to valid orders, identify customers with at least two valid orders, order purchases chronologically, calculate the calendar-day difference from each customer's first to second valid order, average one interval per repeat customer, and return approximately `80.79` days.
- **disallowed_claims:** Must not use `customer_id` as real customer identity; include canceled, unavailable, or created orders; average every consecutive-order interval; use first-to-last duration; omit chronological ordering; or calculate at order-row rather than customer grain.
- **notes:** The benchmark defines days using `DATEDIFF('day', first_order_timestamp, second_order_timestamp)`. When timestamps tie, `order_id` is a deterministic tie-breaker only and is not treated as the true business sequence. Of 2,887 repeat customers, 869 have their first and second valid orders on the same calendar date, including 269 with identical timestamps. The overall mean is 80.79 days, the median is 28 days, and excluding same-date repeats raises the mean to 115.58 days. These are interpretation notes rather than alternate benchmark definitions: the metric is calculated correctly, but same-date repeats make its business meaning worth qualifying. Tests customer identity, repeat-customer semantics, valid-order population, window logic, event sequencing, and customer-level averaging.

## Q33

- **question:** How many orders have payment records but no order items, and how many have order items but no payment records?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:** Payment records but no order items: `775` orders; order items but no payment records: `1` order.
- **expected_clarification:**
- **required_caveat:** This is a raw-table reconciliation question, so the normal valid-order filter must not be applied. The observed status distribution is descriptive and does not establish the root cause of the mismatches.
- **evaluation_rule:** Must compare `order_items` and `order_payments` at `order_id` grain, detect missing-side records in both directions with outer-join or equivalent logic, protect against one-to-many row multiplication, and return exactly `775` payment-side orders without items and `1` item-side order without payments.
- **disallowed_claims:** Must not apply a valid-order-only filter, count item/payment rows rather than unique orders, use an inner join that removes unmatched records, report only one direction, treat multiple rows as multiple orders, automatically classify every mismatch as a data error, or claim a root cause from the status distribution.
- **notes:** Tests raw-table reconciliation, order-level grain, missing-side detection, outer joins, join-amplification protection, and the distinction between commercial filtering and data-quality reconciliation. Optional diagnostic: the `775` payment-without-item orders comprise `603 unavailable`, `164 canceled`, `5 created`, `2 invoiced`, and `1 shipped`; most are associated with non-completed states, but this is not causal evidence. The v3 semantics file no longer states these counts, so Version B cannot answer this question by reading the semantics.

## Q34

- **question:** Which customer states have the longest average delivery times?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:**

  | State | Delivered Orders | Average Delivery Days |
  | --- | ---: | ---: |
  | RR | 41 | 29.39 |
  | AP | 67 | 27.18 |
  | AM | 145 | 26.43 |
  | AL | 397 | 24.54 |
  | PA | 946 | 23.77 |
  | MA | 717 | 21.57 |
  | SE | 335 | 21.52 |
  | CE | 1,279 | 21.27 |
  | AC | 80 | 21.03 |
  | PB | 517 | 20.43 |
  | PI | 476 | 19.46 |
  | RO | 243 | 19.37 |
  | BA | 3,256 | 19.33 |
  | RN | 474 | 19.28 |
  | PE | 1,593 | 18.45 |
  | MT | 886 | 18.06 |
  | TO | 274 | 17.66 |
  | ES | 1,995 | 15.79 |
  | MS | 701 | 15.62 |
  | GO | 1,957 | 15.61 |
  | RJ | 12,350 | 15.31 |
  | RS | 5,344 | 15.30 |
  | SC | 3,546 | 14.95 |
  | DF | 2,080 | 12.97 |
  | MG | 11,354 | 12.01 |
  | PR | 4,923 | 11.99 |
  | SP | 40,494 | 8.76 |

- **expected_clarification:**
- **required_caveat:** Sample sizes differ substantially across states and should be considered before using the ranking for operational decisions. This context is useful but not required for benchmark pass/fail.
- **evaluation_rule:** Must include delivered orders only; calculate order-level elapsed customer delivery time from `order_purchase_timestamp` to `order_delivered_customer_date`; group by `customers.customer_state`; and rank average delivery days descending. Apply the global elapsed-duration evaluation rule: state averages may differ from the canonical values by up to ±0.1 day, while every returned row must preserve the reference ordering. A calendar-boundary result is not rejected from SQL text alone, but fails if its returned ordering differs; in the current dataset the full calendar-boundary ranking reverses RJ and RS.
- **disallowed_claims:** Must not aggregate at `customer_unique_id` grain, include undelivered orders, substitute carrier transit time beginning at `order_delivered_carrier_date`, silently redefine delivery time, or introduce an unsupported minimum-order threshold.
- **notes:** The established semantic definition resolves “delivery time” as customer delivery lead time, so clarification is not required. Top five: RR `29.39`, AP `27.18`, AM `26.43`, AL `24.54`, PA `23.77` days. Unlike Q17 and Q18, no minimum-sample threshold is needed here: every state has at least 41 delivered orders, and a threshold would remove RR from the ranking without analytical justification.

## Q35

- **question:** What percentage of all order records were cancelled each month in 2017?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:**

  | Month | All Order Records | Canceled Orders | Cancellation Rate |
  | ---: | ---: | ---: | ---: |
  | 1 | 800 | 3 | 0.38% |
  | 2 | 1,780 | 17 | 0.96% |
  | 3 | 2,682 | 33 | 1.23% |
  | 4 | 2,404 | 18 | 0.75% |
  | 5 | 3,700 | 29 | 0.78% |
  | 6 | 3,245 | 16 | 0.49% |
  | 7 | 4,026 | 28 | 0.70% |
  | 8 | 4,331 | 27 | 0.62% |
  | 9 | 4,285 | 20 | 0.47% |
  | 10 | 4,631 | 26 | 0.56% |
  | 11 | 7,544 | 37 | 0.49% |
  | 12 | 5,673 | 11 | 0.19% |

- **expected_clarification:**
- **required_caveat:**
- **evaluation_rule:** For each 2017 purchase month, the denominator must be all order records regardless of status and the numerator must be records with `order_status = 'canceled'`. Must use `order_purchase_timestamp`, calculate monthly percentages, and reproduce all verified results.
- **disallowed_claims:** Must not apply the valid-order filter, use canceled orders as both numerator and denominator, attribute months using another timestamp, or return one annual rate instead of monthly percentages.
- **notes:** Tests explicit denominator interpretation, monthly and conditional aggregation, all-record population, time attribution, and percentage calculation. The wording “all order records” overrides the normal valid-order default.

## Q36

- **question:** How did the average review score across submitted reviews change year over year?
- **expected_behavior:** `execute_sql`
- **reference_sql:** see `reference-queries.sql`
- **expected_result:**

  | Review Year | Average Review Score | Previous Year | YoY Change |
  | ---: | ---: | ---: | ---: |
  | 2016 | 3.525974026 | N/A | N/A |
  | 2017 | 4.114333774 | 3.525974026 | +16.69% |
  | 2018 | 4.073061058 | 4.114333774 | -1.00% |

- **expected_clarification:**
- **required_caveat:** The averages are valid for available submitted reviews, but the periods are not directly comparable full calendar years: 2016 covers approximately 3 months, 2017 covers 12 months, and 2018 covers approximately 10 months. Partial-year averages may differ because of seasonality or mix, so the changes must not be presented as unqualified full-year YoY trends.
- **evaluation_rule:** Use submitted review records regardless of current order status. Must treat `review_id` as review grain, count each review once despite repeated order mappings, use `review_answer_timestamp` for year attribution, calculate the verified yearly averages and YoY changes, validate time coverage, and qualify the interpretation accordingly. Unlike Q17 and Q18, this review-year calculation does not require review-to-order attribution and therefore does not need to exclude `review_id` values that map to multiple orders.
- **disallowed_claims:** Must not apply a valid-order filter unless the question explicitly requests one; average at order grain; weight repeated mappings of the same `review_id` multiple times; use `order_purchase_timestamp`; treat missing reviews as zero scores; claim all three years are complete and directly comparable; or describe `+16.69%` and `-1.00%` as unqualified full-year changes.
- **notes:** Rounded interpretation: 2016 `3.526`; 2017 `4.114` (`+16.69%`); 2018 `4.073` (`-1.00%`). Tests review grain, duplicate-mapping handling, submitted-review attribution, yearly averaging, window-function YoY logic, coverage validation, and the difference between a valid calculation and a valid business interpretation. Purchase-year attribution remains disallowed because the question asks about submitted reviews. As a failure signature, purchase-year attribution gives 2017 `4.0891` and 2018 `4.0919`, or approximately `+0.07%`, reversing the direction of the benchmark result.

## Q37

- **question:** Who are our best-performing sellers?
- **expected_behavior:** `clarify`
- **ambiguity_handling:** `clarify`
- **reference_sql:** N/A
- **expected_result:** N/A
- **expected_clarification:** Ask which dimension defines performance, offering options supported by the data (merchandise sales, order or unit volume, delivery performance, review score, cancellation rate), or ask what decision the ranking supports (for example rewards, featuring sellers, or intervention).
- **required_caveat:**
- **evaluation_rule:** Same standard as Q06: one focused clarification before any final ranking; a clearly labelled provisional multi-metric view is acceptable. Fail if the response silently equates performance with sales (or any single metric) and presents a final ranking.
- **disallowed_claims:** Must not present a single metric as "the" measure of seller performance; must not include profitability as an option without noting it cannot be calculated from this data.
- **notes:** Pairs with Q25 (explicit merchandise sales ranking). Section 6 of the semantics file lists "best-performing seller" as ambiguous, so under Version B this also tests whether the model uses that flag. Materiality: the top seller by merchandise sales differs from the top seller by units in both 2017 and 2018, and delivery or review rankings diverge further.

## Q38

- **question:** Which product categories are underperforming?
- **expected_behavior:** `clarify`
- **ambiguity_handling:** `clarify`
- **reference_sql:** N/A
- **expected_result:** N/A
- **expected_clarification:** Ask what "underperforming" is measured against: decline versus a prior period, low results relative to other categories, weak service quality (reviews, delivery, cancellations), or a target or plan.
- **required_caveat:** If the stakeholder means performance against targets, the response should note that targets are not in the data.
- **evaluation_rule:** Pass if the response asks one focused clarification about the comparison baseline before any final list. Fail if it silently picks one baseline, most commonly "lowest total sales", and presents a final list.
- **disallowed_claims:** Must not label categories as underperforming against a target or plan that does not exist in the data.
- **notes:** Pairs with Q24. Tests a different ambiguity type from Q06: the metric may be clear, but the comparison baseline is missing. A category can be small but growing, or large but declining, so the lists under different baselines differ materially.

## Q39

- **question:** Which customer states should we prioritise?
- **expected_behavior:** `clarify`
- **ambiguity_handling:** `clarify`
- **reference_sql:** N/A
- **expected_result:** N/A
- **expected_clarification:** Ask what the prioritisation is for: growing sales or orders, improving delivery or service quality, or another objective.
- **required_caveat:**
- **evaluation_rule:** Pass if the response asks one focused clarification about the goal before any final ranking. A brief note that different goals lead to opposite rankings is desirable. Fail if it silently assumes one goal and presents a final prioritised list.
- **disallowed_claims:** Must not recommend states for growth based on market size or potential, because population and market-size data are not in the dataset.
- **notes:** Pairs with Q34. Tests decision-purpose ambiguity. Materiality: SP has by far the most delivered orders (40,494) and the fastest average delivery (8.76 days), while RR has the slowest delivery (29.39 days) on 41 orders, so a growth goal and a service goal point to opposite ends of the ranking.
