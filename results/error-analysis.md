# Error Analysis · Version A (Development)

> Day 8, v1 (2026-10-14). Source run `A-dev-20261011T123502Z`; grades from `results/baseline/dev_evaluation.csv` after the 2026-10-14 grader corrections. Numbers and populations in this file were re-checked against `data/olist.duckdb`. This is a working draft; presentation polish is deferred to Day 14.

## Conclusion

> **The main bottleneck is not SQL syntax; it is business semantics, above all knowing which orders count and applying that default when the question does not say so.**

Version A answered 4 of 26 development questions fully correctly. Of the 22 failures, only one involved an SQL execution error (Q37, an alias typo, which occurred after the model had already skipped the required clarification). No response used a non-existent column, and no response produced join amplification. Eighteen failures trace back to missing business knowledge. Population definition was the dominant issue: it was the primary error in 15 questions and also appeared as a secondary defect in Q02. The remaining four failures were primarily behavioural: the model did not ask when the question was ambiguous, did not apply a minimum-sample check, or omitted a required caveat. Apart from Q37's alias error, every failure came from understanding the question, choosing business definitions, writing the analytical SQL logic, or interpreting the result (Q33), not from SQL that the database could not execute.

## Case 1 — Q20: the model invents what a "valid order" is

**Question.** How many valid orders do we have?

**AI SQL.**

```sql
SELECT order_status, COUNT(*) AS order_count
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;
```

The model then answered: "There are **98,207 valid orders**, defined as orders not marked canceled or unavailable." The figure 98,207 never appears in any query result. The model computed it itself while writing the answer (99,441 − 625 − 609).

**Correct SQL.**

```sql
SELECT COUNT(*) AS valid_order_count
FROM orders
WHERE order_status IN ('approved', 'invoiced', 'processing', 'shipped', 'delivered');
```

Result: **98,202**.

**Difference.** The model's definition keeps the 5 `created` orders, which the business definition excludes. The numerical gap is small, but the definition is wrong, and it is not even consistently wrong. In the earlier, non-scored run, the same question was answered with **96,478** ("valid = delivered"). Across the two runs, the inferred population changed on seven questions. The same guessing affects every question that says "valid": Q04 and Q32 used "not canceled/unavailable", while Q22 and Q31 used delivered-only. In Q22 the delivered-only guess undercounted every month of 2017 (43,428 against 44,375 for the year).

**Root cause.** The schema shows that `order_status` exists, and a single query reveals its eight values. What neither tells the model is which values the business counts as a real order. That is business information, not schema information, so the model fills the gap with a plausible guess that varies between runs. A second, smaller issue is that the final number came from the model's own arithmetic, not from the database.

- **Stage:** writing SQL (population rule); secondary issue at answer synthesis (model-side arithmetic).
- **Missing:** business information.
- **Fix layer:** B. "Valid Order" and "Default Order Population" are already defined in `03-olist-business-semantics.md` §1.

## Case 2 — Q07: SQL that runs, looks right, and is wrong

**Question.** What percentage of delivered orders arrived on time?

**AI SQL.**

```sql
SELECT
  COUNT(*) AS delivered_orders,
  SUM(CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1 ELSE 0 END) AS on_time_delivered_orders,
  ROUND(100.0 * SUM(CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2) AS on_time_percentage
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL;
```

AI answer: **91.89%** (88,644 of 96,470).

**Correct SQL.**

```sql
SELECT
  SUM(CASE WHEN DATEDIFF('day', order_estimated_delivery_date, order_delivered_customer_date) <= 0 THEN 1 ELSE 0 END) AS on_time_orders_count,
  COUNT(order_id) AS order_count,
  SUM(CASE WHEN DATEDIFF('day', order_estimated_delivery_date, order_delivered_customer_date) <= 0 THEN 1 ELSE 0 END) / COUNT(order_id) AS on_time_rate
FROM orders
WHERE order_estimated_delivery_date IS NOT NULL
  AND order_delivered_customer_date IS NOT NULL
  AND order_status = 'delivered';
```

Result: **93.23%** (89,936 of 96,470).

**Difference.** The population is identical, with the same 96,470 delivered orders, and so is the structure of the query. The only difference is how the two dates are compared. `order_estimated_delivery_date` is stored as a TIMESTAMP, but all 99,441 values sit at exactly 00:00:00. A literal timestamp comparison therefore treats an order delivered at 14:00 on its estimated date as late. That is 1,292 orders, or 1.3 percentage points of on-time rate.

**Root cause.** The schema says TIMESTAMP, and the literal comparison is the natural reading of that type. What the schema cannot express is that this field has no meaningful time of day, so the comparison has to be made by calendar date. Nothing in the output signals the error. The query executes, the number is plausible, and a stakeholder would accept it. This is the clearest example in the benchmark that **executable SQL is not the same as a correct answer**.

- **Stage:** writing SQL (field semantics).
- **Missing:** business information about field meaning (precision), which the schema type hides.
- **Fix layer:** B. "On-time Delivery" in `03-olist-business-semantics.md` §1 and §4 already specifies the date-level comparison.

## Case 3 — Q38: the model answers instead of asking

**Question.** Which product categories are underperforming?

**AI SQL (8 queries; representative excerpt).**

```sql
-- "weak demand" baseline: categories below the median on both orders and revenue
WITH x AS (
  SELECT COALESCE(pct.product_category_name_english, p.product_category_name, 'unknown') AS category,
         COUNT(DISTINCT oi.order_id) AS orders, SUM(oi.price) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  LEFT JOIN product_category_translation pct ON pct.product_category_name = p.product_category_name
  JOIN orders o ON o.order_id = oi.order_id
  WHERE o.order_status NOT IN ('canceled', 'unavailable')
  GROUP BY 1
)
SELECT category, orders, ROUND(revenue, 2) AS revenue
FROM x WHERE orders >= 100 ORDER BY revenue ASC LIMIT 20;

-- "delivery" baseline (excerpt): late = timestamp comparison, delivery days = calendar-boundary count
CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1.0 ELSE 0.0 END AS late,
DATE_DIFF('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days
```

The model opened with "Underperforming can mean weak demand, poor customer experience, or both". It then went straight on to three final lists: poor experience at scale, weak demand, and a delivery watch list. It closed with recommendations such as "Fix office-furniture fulfillment first". It never asked a question.

**Correct behaviour.** Ask one focused clarification about the comparison baseline before giving any list. Underperforming could be measured as decline against a prior period, as low results relative to other categories, as weak service quality (reviews, delivery, cancellations), or against a target or plan, and targets are not in the data. There is no reference SQL, because the expected output is the question itself.

**Difference.** The model did notice the ambiguity; its first sentence names it. It still resolved the ambiguity on its own, chose three baselines, and turned them into actionable recommendations. The numbers behind those recommendations also carry other Version A errors. The demand list uses the guessed "not canceled/unavailable" population. The delivery list repeats Case 2's timestamp comparison and measures delivery time with a calendar-boundary `DATE_DIFF`, which the semantics file says is not an elapsed duration. A stakeholder would receive confident priorities built on a baseline they never chose and on two known definition errors.

**Root cause.** The model had no rule telling it when to stop and ask. Recognising ambiguity and acting on it are separate abilities, and Version A shows the first without the second. Q37 ("best-performing sellers") failed the same way: the model went straight to a ranking query, which then hit an alias error.

- **Stage:** understanding the question.
- **Missing:** behaviour, not schema or business information.
- **Fix layer:** C (clarification rule). One useful contrast for Day 9: "best-performing seller" (Q37) is already listed as ambiguous in `03-olist-business-semantics.md` §6, but "underperforming" (Q38) is not. If Version B fixes Q37 but not Q38, the semantics flag is doing the work; if B fixes neither, flagging ambiguity as knowledge is not enough, and the rule belongs in C.

## All 22 failures by stage and fix layer

"In B context" records whether the knowledge needed for the fix is already present in the frozen-for-development Version B files (`03-olist-business-semantics.md`, `02-tables-model-context.md`) as they stood before Version A ran.

| Q | Primary (secondary) | Stage | Missing | Fix layer | In B context |
| --- | --- | --- | --- | --- | --- |
| Q01 | population_filter (wrong_interpretation) | SQL; interpretation | business; behaviour | B; C (coverage check, comparable-basis growth) | Population yes; coverage handling no |
| Q02 | metric_definition (population_filter) | Understanding | business; behaviour | B; C (disclose metric, association not cause) | Freight Value defined; "total, not max single item" implicit |
| Q04 | population_filter | SQL | business | B | Yes |
| Q05 | population_filter | SQL | business; behaviour | B; C (disclose units, population and year basis) | Yes |
| Q07 | date_boundary | SQL | business (field meaning) | B | Yes |
| Q11 | population_filter | SQL | business; behaviour | B; C (disclose popularity metric, product grain and population) | Yes |
| Q13 | population_filter (wrong_grain) | SQL | business; behaviour | B; C (state average vs maximum; check grain before ranking) | Population yes |
| Q14 | population_filter | SQL | business | B | Yes |
| Q17 | wrong_grain (wrong_interpretation) | SQL | business; behaviour | B; C (caveat) | Ambiguous `review_id` and review attribution risk yes |
| Q18 | metric_definition (wrong_grain) | SQL | behaviour | C (minimum sample for average-based rankings) | No |
| Q20 | population_filter | SQL; synthesis | business | B | Yes |
| Q22 | population_filter | SQL | business | B | Yes |
| Q23 | population_filter (wrong_interpretation) | SQL; interpretation | business; behaviour | B; C (caveat) | Population yes |
| Q24 | population_filter | SQL | business | B | Yes |
| Q25 | population_filter | SQL | business | B | Yes |
| Q26 | population_filter | SQL | business | B | Yes |
| Q27 | population_filter | SQL | business | B | Yes |
| Q31 | population_filter | SQL | business | B | Yes |
| Q32 | population_filter | SQL | business | B | Yes |
| Q33 | wrong_interpretation | Interpretation | behaviour | C (state reconciliation caveat) | Population rule yes |
| Q37 | missed_clarification (sql_execution) | Understanding | behaviour | C (clarify) | Flagged ambiguous in §6 |
| Q38 | missed_clarification | Understanding | behaviour | C (clarify) | No |

By primary fix layer, **18 failures need B (knowledge) and 4 need C (behaviour)**: Q18, Q33, Q37 and Q38. Seven more items (Q01, Q02, Q05, Q11, Q13, Q17, Q23) also need a C behaviour on top of the B fix, mostly stating assumptions or caveats; assumption transparency was 0/7. Measured against the Day 8 checklist, one failure involved an SQL syntax or execution error (Q37), none involved join duplication, four involved a metric or grain choice as primary or secondary label (Q02, Q13, Q17, Q18), and two should have been clarifications (Q37, Q38). Customer grain itself was handled correctly wherever it mattered: Q04 and Q32 both used `customer_unique_id`.

## What this means for Day 9

The knowledge needed for most B-layer fixes was written before Version A ran: the semantics and data dictionary were locked on 2026-10-02, and Version A ran on 2026-10-11. Version B should therefore first be run with those files **unchanged**. Any A→B gain then cannot be explained as context tuned to A's failures, which is a strong point to be able to make in an interview. Only failures that remain after that first B run should drive edits to the B context, each logged under methodology §7.

Three questions to watch in Version B are listed below. Do the 5 explicit-"valid" questions pass? That tests the definition itself. Do the 10 questions where "valid" is unstated pass (Q01, Q05, Q11, Q13, Q14, Q23–Q27)? That tests whether the default population is applied without being asked, and it is the harder test. Do Q37 and Q38 separate, as described in Case 3?

On the Version C side, development evidence points to four general behaviours: asking one focused clarification when a term has no defined baseline or metric; stating the metric, population and grain assumptions in the answer text; applying a minimum sample before ranking by an average; and checking data coverage before comparing periods. These should be checked against the pre-registered Version C rules in methodology §7 before any new rule is added.
