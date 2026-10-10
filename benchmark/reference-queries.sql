-- Olist Benchmark Reference Queries
-- Internal evaluation artifact. Do not provide this file to the model being evaluated.
--
-- Put only verified reference SQL here.
-- After running each query, record the verified result in 04-2-benchmark-answer-key.md.
--
-- v4 (2026-10-02) -- frozen: finalised elapsed-duration evaluation,
-- submitted-review population, parameterised Q17/Q18 minimum-review thresholds,
-- Q12 NULL-band handling and verified results, and connected contrast-group rules.
-- Held-out results must not be used to revise this reference after freeze.
--
-- 2026-10-10: completed the missing executable reference and verified expected
-- result for the already-accepted Q11 Interpretation B. No benchmark scope,
-- split, grading rule, accepted interpretation, or held-out content changed.
--
-- v3 (2026-09-29): added Q01-Q03 (verified) and placeholders for questions moved
-- from clarify to execute_sql with a disclosed assumption. For disclosed-assumption
-- questions, write one query per accepted interpretation listed in the answer key.

-- ============================================================
-- Q01
-- ============================================================
-- Handling: disclosed_assumption (revenue has no canonical definition in
-- 03-olist-business-semantics.md, sections 2 and 6).
-- Reference interpretation A: revenue = customer payment value.
-- Accepted interpretation B: revenue = merchandise value (see variant below).
-- Valid orders only; attribution by order_purchase_timestamp.
-- A calendar spine is used so LAG() compares true consecutive months
-- (there are no orders in 2016-11; LAG over existing rows would compare
-- 2016-12 with 2016-10 and label it month-over-month).

-- Reference SQL (A, monthly series with MoM):
WITH months AS (
    SELECT CAST(range AS DATE) AS month_start
    FROM range(DATE '2016-09-01', DATE '2018-11-01', INTERVAL 1 MONTH)
),

monthly_payment AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month_start,
        SUM(p.payment_value) AS payment_value
    FROM order_payments p
    JOIN orders o
        ON p.order_id = o.order_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
    GROUP BY 1
),

series AS (
    SELECT
        m.month_start,
        COALESCE(mp.payment_value, 0) AS payment_value,
        LAG(COALESCE(mp.payment_value, 0)) OVER (
            ORDER BY m.month_start
        ) AS previous_payment_value
    FROM months m
    LEFT JOIN monthly_payment mp
        ON m.month_start = mp.month_start
)

SELECT
    STRFTIME(month_start, '%Y-%m') AS order_month,
    ROUND(payment_value, 2) AS payment_value,
    ROUND(previous_payment_value, 2) AS previous_payment_value,
    ROUND(
        (payment_value - previous_payment_value) * 100.0
        / NULLIF(previous_payment_value, 0),
        2
    ) AS mom_change_pct
FROM series
ORDER BY month_start;

-- Reference SQL (A, like-for-like growth: Jan-Aug 2017 vs Jan-Aug 2018,
-- plus full-year 2017 for context):
SELECT
    ROUND(SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2017
                   THEN p.payment_value END), 2) AS payment_2017_full_year,
    ROUND(SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2017
                    AND MONTH(o.order_purchase_timestamp) <= 8
                   THEN p.payment_value END), 2) AS payment_2017_jan_aug,
    ROUND(SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2018
                    AND MONTH(o.order_purchase_timestamp) <= 8
                   THEN p.payment_value END), 2) AS payment_2018_jan_aug,
    ROUND(
        (SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2018
                   AND MONTH(o.order_purchase_timestamp) <= 8
                  THEN p.payment_value END)
         / SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2017
                     AND MONTH(o.order_purchase_timestamp) <= 8
                    THEN p.payment_value END) - 1) * 100,
        2
    ) AS like_for_like_growth_pct
FROM order_payments p
JOIN orders o
    ON p.order_id = o.order_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
);

-- Variant B (merchandise value): replace order_payments / payment_value
-- with order_items / price in both queries above. The 2017 monthly values
-- must equal the verified Q23 results.
SELECT
    ROUND(SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2017
                   THEN i.price END), 2) AS merchandise_2017_full_year,
    ROUND(SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2017
                    AND MONTH(o.order_purchase_timestamp) <= 8
                   THEN i.price END), 2) AS merchandise_2017_jan_aug,
    ROUND(SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2018
                    AND MONTH(o.order_purchase_timestamp) <= 8
                   THEN i.price END), 2) AS merchandise_2018_jan_aug,
    ROUND(
        (SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2018
                   AND MONTH(o.order_purchase_timestamp) <= 8
                  THEN i.price END)
         / SUM(CASE WHEN YEAR(o.order_purchase_timestamp) = 2017
                     AND MONTH(o.order_purchase_timestamp) <= 8
                    THEN i.price END) - 1) * 100,
        2
    ) AS like_for_like_growth_pct
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
);

-- Time-coverage validation query (all statuses, so the tail is visible):
SELECT
    STRFTIME(order_purchase_timestamp, '%Y-%m') AS order_month,
    COUNT(*) AS all_order_records,
    SUM(CASE WHEN order_status IN (
        'approved', 'invoiced', 'processing', 'shipped', 'delivered'
    ) THEN 1 ELSE 0 END) AS valid_orders
FROM orders
GROUP BY 1
ORDER BY 1;


-- ============================================================
-- Q02
-- ============================================================
-- Handling: disclosed_assumption.
-- Reference interpretation A: product = product category;
-- freight expense = total freight_value. Valid orders only.
-- freight_value is item-level (split across items in multi-item orders),
-- so category attribution is safe, unlike payment_value.
-- The same query returns the volume x per-item decomposition used to
-- grade the "why" part of the question.

-- Reference SQL (A, with decomposition):
WITH item_freight AS (
    SELECT
        p.product_category_name,
        i.freight_value,
        p.product_weight_g
    FROM order_items i
    JOIN orders o
        ON i.order_id = o.order_id
    LEFT JOIN products p
        ON i.product_id = p.product_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
)

SELECT
    product_category_name,
    COUNT(*) AS item_rows,
    ROUND(SUM(freight_value), 2) AS total_freight,
    ROUND(AVG(freight_value), 2) AS avg_freight_per_item,
    ROUND(MEDIAN(product_weight_g), 0) AS median_weight_g,
    RANK() OVER (ORDER BY SUM(freight_value) DESC) AS rank_total_freight,
    RANK() OVER (ORDER BY AVG(freight_value) DESC) AS rank_avg_freight
FROM item_freight
GROUP BY 1
ORDER BY total_freight DESC;

-- Overall benchmark for the decomposition:
SELECT
    COUNT(*) AS item_rows,
    ROUND(SUM(i.freight_value), 2) AS total_freight,
    ROUND(AVG(i.freight_value), 2) AS avg_freight_per_item
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
);

-- Highest per-item freight categories (minimum 100 item rows, so the
-- average is not driven by a handful of items):
SELECT
    p.product_category_name,
    COUNT(*) AS item_rows,
    ROUND(AVG(i.freight_value), 2) AS avg_freight_per_item
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
LEFT JOIN products p
    ON i.product_id = p.product_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
GROUP BY 1
HAVING COUNT(*) >= 100
ORDER BY avg_freight_per_item DESC;

-- Variant B (product = individual product_id, total freight):
SELECT
    i.product_id,
    p.product_category_name,
    COUNT(*) AS item_rows,
    ROUND(SUM(i.freight_value), 2) AS total_freight
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
LEFT JOIN products p
    ON i.product_id = p.product_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
GROUP BY 1, 2
ORDER BY total_freight DESC;


-- ============================================================
-- Q03
-- ============================================================
-- Handling: disclosed_assumption.
-- "Stopped or cancelled" = order_status IN ('canceled', 'unavailable').
-- Denominator = all order records in the purchase month.
-- Month = purchase month (purchase-month cohort). The dataset has no
-- cancellation timestamp, so this is not the month the cancellation happened.
-- Spike rule used for the reference: stopped rate >= 2x the median monthly
-- rate across complete months (2017-01 to 2018-08). Mean + 2 SD and the
-- 1.5 x IQR upper fence flag the same month (see answer key).

-- Reference SQL:
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_purchase_timestamp) AS month_start,
        COUNT(*) AS all_order_records,
        SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) AS canceled_orders,
        SUM(CASE WHEN order_status = 'unavailable' THEN 1 ELSE 0 END) AS unavailable_orders,
        SUM(CASE WHEN order_status IN ('canceled', 'unavailable') THEN 1 ELSE 0 END) AS stopped_orders
    FROM orders
    WHERE order_purchase_timestamp >= TIMESTAMP '2017-01-01'
    GROUP BY 1
),

rates AS (
    SELECT
        *,
        stopped_orders * 100.0 / all_order_records AS stopped_rate_pct
    FROM monthly
),

baseline AS (
    SELECT MEDIAN(stopped_rate_pct) AS median_rate_pct
    FROM rates
    WHERE month_start < DATE '2018-09-01'
)

SELECT
    STRFTIME(r.month_start, '%Y-%m') AS order_month,
    r.all_order_records,
    r.canceled_orders,
    r.unavailable_orders,
    r.stopped_orders,
    ROUND(r.stopped_rate_pct, 2) AS stopped_rate_pct,
    ROUND(r.stopped_rate_pct / b.median_rate_pct, 2) AS rate_vs_median,
    CASE
        WHEN r.month_start >= DATE '2018-09-01' THEN 'coverage_artifact'
        WHEN r.stopped_rate_pct >= 2 * b.median_rate_pct THEN 'spike'
        ELSE ''
    END AS flag
FROM rates r
CROSS JOIN baseline b
ORDER BY r.month_start;


-- ============================================================
-- Q04
-- ============================================================

-- Reference SQL:
WITH order_counts AS (
    SELECT
        c.customer_unique_id,
        COUNT(o.order_id) AS order_count
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
    GROUP BY 1
)

SELECT
    CASE
        WHEN order_count >= 3 THEN '>= 3 orders'
        ELSE CAST(order_count AS STRING)
    END AS order_count,
    COUNT(customer_unique_id) AS customer_count
FROM order_counts
GROUP BY 1
ORDER BY 1;


-- ============================================================
-- Q05
-- ============================================================
-- Handling: disclosed_assumption. Reference: units sold = order_items rows per
-- seller per purchase year, valid orders. Rank within each year.
-- Reference SQL:
WITH a AS (
    SELECT
        YEAR(o.order_purchase_timestamp) AS order_year,
        i.seller_id,
        COUNT(*) AS product_count,
        RANK() OVER (
            PARTITION BY YEAR(o.order_purchase_timestamp)
            ORDER BY COUNT(*) DESC
        ) AS rk
    FROM order_items i
    JOIN orders o
        ON i.order_id = o.order_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
    GROUP BY 1, 2
)
SELECT
    order_year,
    seller_id,
    product_count
FROM a
WHERE rk = 1
ORDER BY order_year, seller_id;


-- ============================================================
-- Q07
-- ============================================================

-- Reference SQL:
SELECT
    SUM(
        CASE
            WHEN DATEDIFF(
                'day',
                order_estimated_delivery_date,
                order_delivered_customer_date
            ) <= 0
            THEN 1
            ELSE 0
        END
    ) AS on_time_orders_count,
    COUNT(order_id) AS order_count,
    SUM(
        CASE
            WHEN DATEDIFF(
                'day',
                order_estimated_delivery_date,
                order_delivered_customer_date
            ) <= 0
            THEN 1
            ELSE 0
        END
    ) / COUNT(order_id) AS on_time_rate
FROM orders
WHERE order_estimated_delivery_date IS NOT NULL
    AND order_delivered_customer_date IS NOT NULL
    AND order_status = 'delivered';


-- ============================================================
-- Q08
-- ============================================================

-- Reference SQL:
SELECT
    ROUND(
        AVG(
            DATEDIFF(
                'minute',
                order_purchase_timestamp,
                order_delivered_carrier_date
            ) / 1440.0
        ),
        2
    ) AS avg_days
FROM orders
WHERE order_purchase_timestamp IS NOT NULL
    AND order_delivered_carrier_date IS NOT NULL;


-- ============================================================
-- Q09
-- ============================================================

-- Reference SQL:
SELECT
    ROUND(
        AVG(
            DATEDIFF(
                'minute',
                order_purchase_timestamp,
                order_delivered_customer_date
            ) / 1440.0
        ),
        2
    ) AS avg_days
FROM orders
WHERE order_status = 'delivered'
    AND order_purchase_timestamp IS NOT NULL
    AND order_delivered_customer_date IS NOT NULL;


-- ============================================================
-- Q10
-- ============================================================

-- Reference SQL:
SELECT
    c.customer_city,
    COUNT(o.order_id) AS valid_order_count
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
GROUP BY 1
ORDER BY 2 DESC;


-- ============================================================
-- Q11
-- ============================================================
-- Handling: disclosed_assumption. Primary/reference interpretation A:
-- product_id by item rows per purchase year, valid orders. Interpretation B
-- (product category by item rows per year) remains acceptable if disclosed.
-- Reference SQL (A, product_id by units sold):
WITH a AS (
    SELECT
        YEAR(o.order_purchase_timestamp) AS order_year,
        i.product_id,
        COUNT(*) AS product_count,
        RANK() OVER (
            PARTITION BY YEAR(o.order_purchase_timestamp)
            ORDER BY COUNT(*) DESC
        ) AS rk
    FROM order_items i
    JOIN orders o
        ON i.order_id = o.order_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
    GROUP BY 1, 2
)
SELECT
    order_year,
    product_id,
    product_count
FROM a
WHERE rk = 1
ORDER BY order_year, product_id;

-- Reference SQL (B, product category by units sold):
WITH a AS (
    SELECT
        YEAR(o.order_purchase_timestamp) AS order_year,
        p.product_category_name,
        COUNT(*) AS product_count,
        RANK() OVER (
            PARTITION BY YEAR(o.order_purchase_timestamp)
            ORDER BY COUNT(*) DESC
        ) AS rk
    FROM order_items i
    JOIN orders o
        ON i.order_id = o.order_id
    JOIN products p
        ON i.product_id = p.product_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
    GROUP BY 1, 2
)
SELECT
    order_year,
    product_category_name,
    product_count
FROM a
WHERE rk = 1
ORDER BY order_year, product_category_name;


-- ============================================================
-- Q12
-- ============================================================
-- Handling: disclosed_assumption (analysis scope). Delivered orders only;
-- delivery time per semantics. For comparable decomposition, all reference
-- queries require non-null purchase, carrier-handoff and customer-delivery
-- timestamps and use minute-level elapsed durations as the canonical reference.
-- Equivalent second-, hour-, or interval-based elapsed-time calculations are valid.
-- Rubric-graded.

-- Factor 1: customer geography.
WITH data AS (
    SELECT
        o.order_id,
        c.customer_state,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_carrier_date
        ) / 1440.0 AS pre_carrier_handoff_time,
        DATEDIFF(
            'minute',
            o.order_delivered_carrier_date,
            o.order_delivered_customer_date
        ) / 1440.0 AS post_handoff_transit_time,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_customer_date
        ) / 1440.0 AS overall_delivery_time
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
        AND o.order_purchase_timestamp IS NOT NULL
        AND o.order_delivered_carrier_date IS NOT NULL
        AND o.order_delivered_customer_date IS NOT NULL
)

SELECT
    customer_state,
    COUNT(*) AS total_orders,
    ROUND(AVG(pre_carrier_handoff_time), 2) AS avg_pre_carrier_days,
    ROUND(AVG(post_handoff_transit_time), 2) AS avg_post_handoff_days,
    ROUND(AVG(overall_delivery_time), 2) AS avg_delivery_days
FROM data
GROUP BY 1
ORDER BY avg_delivery_days DESC;

-- Factor 2: seller-to-customer geography. Restrict to single-seller orders
-- because delivery timestamps are at order grain.
WITH customer_data AS (
    SELECT
        o.order_id,
        c.customer_state,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_carrier_date
        ) / 1440.0 AS pre_carrier_handoff_time,
        DATEDIFF(
            'minute',
            o.order_delivered_carrier_date,
            o.order_delivered_customer_date
        ) / 1440.0 AS post_handoff_transit_time,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_customer_date
        ) / 1440.0 AS overall_delivery_time
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
        AND o.order_purchase_timestamp IS NOT NULL
        AND o.order_delivered_carrier_date IS NOT NULL
        AND o.order_delivered_customer_date IS NOT NULL
),

seller_data AS (
    SELECT
        i.order_id,
        COUNT(DISTINCT i.seller_id) AS seller_count,
        MAX(s.seller_state) AS seller_state
    FROM order_items i
    JOIN sellers s
        ON i.seller_id = s.seller_id
    GROUP BY 1
)

SELECT
    CASE
        WHEN c.customer_state = s.seller_state
            THEN 'same state'
        ELSE 'different state'
    END AS state_flag,
    COUNT(*) AS total_orders,
    ROUND(AVG(c.pre_carrier_handoff_time), 2) AS avg_pre_carrier_days,
    ROUND(AVG(c.post_handoff_transit_time), 2) AS avg_post_handoff_days,
    ROUND(AVG(c.overall_delivery_time), 2) AS avg_delivery_days
FROM customer_data c
JOIN seller_data s
    ON c.order_id = s.order_id
WHERE s.seller_count = 1
GROUP BY 1;

-- Factor 3: order size / item count.
WITH customer_data AS (
    SELECT
        o.order_id,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_carrier_date
        ) / 1440.0 AS pre_carrier_handoff_time,
        DATEDIFF(
            'minute',
            o.order_delivered_carrier_date,
            o.order_delivered_customer_date
        ) / 1440.0 AS post_handoff_transit_time,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_customer_date
        ) / 1440.0 AS overall_delivery_time
    FROM orders o
    WHERE o.order_status = 'delivered'
        AND o.order_purchase_timestamp IS NOT NULL
        AND o.order_delivered_carrier_date IS NOT NULL
        AND o.order_delivered_customer_date IS NOT NULL
),

order_counts AS (
    SELECT
        order_id,
        COUNT(product_id) AS item_count
    FROM order_items
    GROUP BY 1
)

SELECT
    CASE
        WHEN item_count > 5 THEN '> 5'
        ELSE CAST(item_count AS STRING)
    END AS item_count,
    COUNT(*) AS total_orders,
    ROUND(AVG(c.pre_carrier_handoff_time), 2) AS avg_pre_carrier_days,
    ROUND(AVG(c.post_handoff_transit_time), 2) AS avg_post_handoff_days,
    ROUND(AVG(c.overall_delivery_time), 2) AS avg_delivery_days
FROM order_counts o
JOIN customer_data c
    ON c.order_id = o.order_id
GROUP BY 1
ORDER BY 1;

-- Factor 4A: total observed order weight.
WITH customer_data AS (
    SELECT
        o.order_id,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_carrier_date
        ) / 1440.0 AS pre_carrier_handoff_time,
        DATEDIFF(
            'minute',
            o.order_delivered_carrier_date,
            o.order_delivered_customer_date
        ) / 1440.0 AS post_handoff_transit_time,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_customer_date
        ) / 1440.0 AS overall_delivery_time
    FROM orders o
    WHERE o.order_status = 'delivered'
        AND o.order_purchase_timestamp IS NOT NULL
        AND o.order_delivered_carrier_date IS NOT NULL
        AND o.order_delivered_customer_date IS NOT NULL
),

order_physical AS (
    SELECT
        i.order_id,
        SUM(p.product_weight_g) AS weight
    FROM order_items i
    JOIN products p
        ON i.product_id = p.product_id
    GROUP BY 1
)

SELECT
    CASE
        WHEN weight IS NULL THEN '0. unknown'
        WHEN weight <= 200 THEN '1. <=200g'
        WHEN weight <= 500 THEN '2. <=500g'
        WHEN weight <= 1000 THEN '3. <=1000g'
        WHEN weight <= 2000 THEN '4. <=2000g'
        WHEN weight <= 3000 THEN '5. <=3000g'
        WHEN weight <= 5000 THEN '6. <=5000g'
        ELSE '7. >5000g'
    END AS weight_band,
    COUNT(*) AS total_orders,
    ROUND(AVG(c.pre_carrier_handoff_time), 2) AS avg_pre_carrier_days,
    ROUND(AVG(c.post_handoff_transit_time), 2) AS avg_post_handoff_days,
    ROUND(AVG(c.overall_delivery_time), 2) AS avg_delivery_days
FROM customer_data c
JOIN order_physical p
    ON c.order_id = p.order_id
GROUP BY 1
ORDER BY 1;

-- Factor 4B: cubic-volume supporting check.
WITH customer_data AS (
    SELECT
        o.order_id,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_carrier_date
        ) / 1440.0 AS pre_carrier_handoff_time,
        DATEDIFF(
            'minute',
            o.order_delivered_carrier_date,
            o.order_delivered_customer_date
        ) / 1440.0 AS post_handoff_transit_time,
        DATEDIFF(
            'minute',
            o.order_purchase_timestamp,
            o.order_delivered_customer_date
        ) / 1440.0 AS overall_delivery_time
    FROM orders o
    WHERE o.order_status = 'delivered'
        AND o.order_purchase_timestamp IS NOT NULL
        AND o.order_delivered_carrier_date IS NOT NULL
        AND o.order_delivered_customer_date IS NOT NULL
),

order_physical AS (
    SELECT
        i.order_id,
        SUM(
            p.product_length_cm
            * p.product_height_cm
            * p.product_width_cm
        ) AS cubic
    FROM order_items i
    JOIN products p
        ON i.product_id = p.product_id
    GROUP BY 1
)

SELECT
    CASE
        WHEN cubic IS NULL THEN '0. unknown'
        WHEN cubic <= 2000 THEN '1. <=2000'
        WHEN cubic <= 5000 THEN '2. <=5000'
        WHEN cubic <= 10000 THEN '3. <=10000'
        WHEN cubic <= 30000 THEN '4. <=30000'
        WHEN cubic <= 50000 THEN '5. <=50000'
        ELSE '6. >50000'
    END AS cubic_band,
    COUNT(*) AS total_orders,
    ROUND(AVG(c.pre_carrier_handoff_time), 2) AS avg_pre_carrier_days,
    ROUND(AVG(c.post_handoff_transit_time), 2) AS avg_post_handoff_days,
    ROUND(AVG(c.overall_delivery_time), 2) AS avg_delivery_days
FROM customer_data c
JOIN order_physical p
    ON c.order_id = p.order_id
GROUP BY 1
ORDER BY 1;


-- ============================================================
-- Q13
-- ============================================================
-- Handling: disclosed_assumption. Write A (product_id by AVG(price)) and
-- B (product_id by MAX(price)). Valid orders.
-- Reference SQL (A, average selling price):
SELECT
    i.product_id,
    COUNT(*) AS units_sold,
    AVG(i.price) AS avg_price
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
GROUP BY 1
ORDER BY avg_price DESC, product_id;

-- Reference SQL (B, maximum observed selling price):
SELECT
    i.product_id,
    COUNT(*) AS units_sold,
    MAX(i.price) AS max_price
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
GROUP BY 1
ORDER BY max_price DESC, product_id;


-- ============================================================
-- Q14
-- ============================================================

-- Reference SQL:
SELECT
    i.product_id,
    COUNT(*) AS units_sold
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
GROUP BY 1
ORDER BY 2 DESC;


-- ============================================================
-- Q16
-- ============================================================
-- Handling: disclosed_assumption.
-- A (reference): order-level cancellation rate
--   = canceled orders / all order records (all statuses).
-- B: customer-level cancellation incidence
--   = customers (customer_unique_id) with >= 1 canceled order
--     / all customers with >= 1 order record (all statuses).
-- canceled + unavailable is a failed/stopped-order rate, not cancellation
-- rate; it is included only as a labelled supplementary check.

-- Reference SQL (A):
SELECT
    COUNT(*) AS all_order_records,
    SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) AS canceled_orders,
    ROUND(
        SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) * 100.0
        / COUNT(*),
        2
    ) AS order_cancellation_rate_pct
FROM orders;

-- Reference SQL (B):
WITH customer_flags AS (
    SELECT
        c.customer_unique_id,
        MAX(CASE WHEN o.order_status = 'canceled' THEN 1 ELSE 0 END) AS has_canceled_order
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    GROUP BY 1
)

SELECT
    COUNT(*) AS customers_with_any_order,
    SUM(has_canceled_order) AS customers_with_canceled_order,
    ROUND(SUM(has_canceled_order) * 100.0 / COUNT(*), 2) AS customer_cancellation_incidence_pct
FROM customer_flags;

-- Supplementary (label as failed/stopped-order rate, not cancellation rate):
SELECT
    ROUND(
        SUM(CASE WHEN order_status IN ('canceled', 'unavailable') THEN 1 ELSE 0 END) * 100.0
        / COUNT(*),
        2
    ) AS failed_or_stopped_order_rate_pct
FROM orders;


-- ============================================================
-- Q17
-- ============================================================
-- Handling: disclosed_assumption. Product_id grain; exclude review IDs that
-- map to multiple orders; each clean review contributes once per distinct
-- product in its order. Submitted reviews are used regardless of current order
-- status; no valid-order filter is applied. Set min_review_count to the model's
-- declared integer threshold (accepted range: 20-100). The canonical example is 30.
-- Reference SQL:
WITH parameters AS (
    SELECT 30 AS min_review_count
),

clean_reviews AS (
    SELECT
        review_id,
        MAX(order_id) AS order_id,
        MAX(review_score) AS review_score
    FROM order_reviews
    GROUP BY 1
    HAVING COUNT(DISTINCT order_id) = 1
),

order_products AS (
    SELECT DISTINCT
        order_id,
        product_id
    FROM order_items
)

SELECT
    p.product_id,
    COUNT(*) AS review_count,
    AVG(r.review_score) AS avg_review_score
FROM clean_reviews r
JOIN order_products p
    ON r.order_id = p.order_id
GROUP BY 1
HAVING COUNT(*) >= (SELECT min_review_count FROM parameters)
ORDER BY 3 DESC, 2 DESC;


-- ============================================================
-- Q18
-- ============================================================
-- Handling: disclosed_assumption. Seller_id grain; exclude review IDs that
-- map to multiple orders; each clean review contributes once per distinct
-- seller in its order. Submitted reviews are used regardless of current order
-- status; no valid-order filter is applied. Set min_review_count to the model's
-- declared integer threshold (accepted range: 20-100). The canonical example is 30.
-- Reference SQL:
WITH parameters AS (
    SELECT 30 AS min_review_count
),

clean_reviews AS (
    SELECT
        review_id,
        MAX(order_id) AS order_id,
        MAX(review_score) AS review_score
    FROM order_reviews
    GROUP BY 1
    HAVING COUNT(DISTINCT order_id) = 1
),

order_sellers AS (
    SELECT DISTINCT
        order_id,
        seller_id
    FROM order_items
)

SELECT
    s.seller_id,
    COUNT(*) AS review_count,
    AVG(r.review_score) AS avg_review_score
FROM clean_reviews r
JOIN order_sellers s
    ON r.order_id = s.order_id
GROUP BY 1
HAVING COUNT(*) >= (SELECT min_review_count FROM parameters)
ORDER BY 3, 2 DESC;


-- ============================================================
-- Q19
-- ============================================================

-- Reference SQL:
SELECT
    COUNT(*) AS order_count
FROM orders;


-- ============================================================
-- Q20
-- ============================================================

-- Reference SQL:
SELECT
    COUNT(*) AS valid_order_count
FROM orders
WHERE order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
);


-- ============================================================
-- Q21
-- ============================================================

-- Reference SQL:
SELECT
    COUNT(DISTINCT c.customer_unique_id) AS unique_customer_count
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
);


-- ============================================================
-- Q22
-- ============================================================

-- Reference SQL:
SELECT
    MONTH(order_purchase_timestamp) AS order_month,
    COUNT(*) AS order_count
FROM orders
WHERE order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
    AND YEAR(order_purchase_timestamp) = 2017
GROUP BY 1
ORDER BY 1;


-- ============================================================
-- Q23
-- ============================================================

-- Reference SQL:
SELECT
    MONTH(o.order_purchase_timestamp) AS order_month,
    ROUND(SUM(i.price), 2) AS merchandise_sales
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
    AND YEAR(o.order_purchase_timestamp) = 2017
GROUP BY 1
ORDER BY 1;


-- ============================================================
-- Q24
-- ============================================================

-- Reference SQL:
SELECT
    p.product_category_name,
    ROUND(SUM(i.price), 2) AS merchandise_sales
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
JOIN products p
    ON i.product_id = p.product_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
GROUP BY 1
ORDER BY 2 DESC;


-- ============================================================
-- Q25
-- ============================================================

-- Reference SQL:
SELECT
    i.seller_id,
    ROUND(SUM(i.price), 2) AS merchandise_sales
FROM order_items i
JOIN orders o
    ON i.order_id = o.order_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
GROUP BY 1
ORDER BY 2 DESC;


-- ============================================================
-- Q26
-- ============================================================

-- Reference SQL:
SELECT
    COUNT(*) AS multi_item_order_count
FROM (
    SELECT
        i.order_id
    FROM order_items i
    JOIN orders o
        ON i.order_id = o.order_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
    GROUP BY i.order_id
    HAVING COUNT(i.order_item_id) > 1
) a;


-- ============================================================
-- Q27
-- ============================================================

-- Reference SQL:
SELECT
    COUNT(*) AS multi_payment_order_count
FROM (
    SELECT
        p.order_id
    FROM order_payments p
    JOIN orders o
        ON p.order_id = o.order_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
    GROUP BY p.order_id
    HAVING COUNT(*) > 1
) a;


-- ============================================================
-- Q28
-- ============================================================

-- Reference SQL:
WITH yearly_orders AS (
    SELECT
        YEAR(order_purchase_timestamp) AS order_year,
        COUNT(*) AS valid_order_count
    FROM orders
    WHERE order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
    GROUP BY 1
),

yoy AS (
    SELECT
        order_year,
        valid_order_count,
        LAG(valid_order_count) OVER (
            ORDER BY order_year
        ) AS previous_year_count
    FROM yearly_orders
)

SELECT
    order_year,
    valid_order_count,
    previous_year_count,
    valid_order_count - previous_year_count AS absolute_change,
    ROUND(
        (valid_order_count - previous_year_count)
        * 100.0 / previous_year_count,
        2
    ) AS yoy_change_pct
FROM yoy
WHERE order_year IN (2017, 2018)
ORDER BY order_year;

-- Time-coverage validation query:
SELECT
    YEAR(order_purchase_timestamp) AS order_year,
    MIN(order_purchase_timestamp) AS first_order_date,
    MAX(order_purchase_timestamp) AS last_order_date,
    COUNT(DISTINCT MONTH(order_purchase_timestamp)) AS months_present
FROM orders
WHERE order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
)
    AND YEAR(order_purchase_timestamp) IN (2017, 2018)
GROUP BY 1
ORDER BY 1;


-- ============================================================
-- Q29
-- ============================================================

-- Reference SQL:
SELECT
    COUNT(DISTINCT o.order_id) AS total_valid_orders,
    COUNT(DISTINCT o.order_id)
        - COUNT(DISTINCT r.order_id) AS no_review_orders,
    ROUND(
        (
            COUNT(DISTINCT o.order_id)
            - COUNT(DISTINCT r.order_id)
        )
        * 100.0
        / COUNT(DISTINCT o.order_id),
        2
    ) AS no_review_percentage
FROM orders o
LEFT JOIN order_reviews r
    ON o.order_id = r.order_id
WHERE o.order_status IN (
    'approved',
    'invoiced',
    'processing',
    'shipped',
    'delivered'
);


-- ============================================================
-- Q31
-- ============================================================

-- Reference SQL:
WITH multi_item_orders AS (
    SELECT
        order_id
    FROM order_items
    GROUP BY order_id
    HAVING COUNT(order_item_id) > 1
),

target_orders AS (
    SELECT
        o.order_id
    FROM orders o
    JOIN multi_item_orders m
        ON o.order_id = m.order_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
        AND YEAR(o.order_purchase_timestamp) = 2017
),

payment_by_order AS (
    SELECT
        order_id,
        SUM(payment_value) AS amount_paid
    FROM order_payments
    GROUP BY order_id
)

SELECT
    COUNT(*) AS total_target_orders,
    COUNT(p.order_id) AS orders_with_payment,
    COUNT(*) - COUNT(p.order_id) AS orders_without_payment,
    ROUND(AVG(p.amount_paid), 2) AS avg_amount_paid
FROM target_orders t
LEFT JOIN payment_by_order p
    ON t.order_id = p.order_id;


-- ============================================================
-- Q32
-- ============================================================

-- Reference SQL:
WITH repeat_customers AS (
    SELECT
        c.customer_unique_id
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
    GROUP BY 1
    HAVING COUNT(*) > 1
),

multiple_orders AS (
    SELECT
        r.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY r.customer_unique_id
            ORDER BY o.order_purchase_timestamp, o.order_id
        ) AS order_rank,
        LEAD(o.order_purchase_timestamp) OVER (
            PARTITION BY r.customer_unique_id
            ORDER BY o.order_purchase_timestamp, o.order_id
        ) AS next_order_purchase
    FROM repeat_customers r
    JOIN customers c
        ON r.customer_unique_id = c.customer_unique_id
    JOIN orders o
        ON o.customer_id = c.customer_id
    WHERE o.order_status IN (
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered'
    )
)

SELECT
    ROUND(
        AVG(
            DATEDIFF(
                'day',
                order_purchase_timestamp,
                next_order_purchase
            )
        ),
        2
    ) AS avg_days
FROM multiple_orders
WHERE order_rank = 1;


-- ============================================================
-- Q33
-- ============================================================

-- Reference SQL:
-- Part 1: orders with order items but no payment records.
SELECT
    COUNT(DISTINCT i.order_id) AS item_orders_without_payment
FROM order_items i
LEFT JOIN order_payments p
    ON i.order_id = p.order_id
WHERE p.order_id IS NULL;

-- Part 2: orders with payment records but no order items.
SELECT
    COUNT(DISTINCT p.order_id) AS payment_orders_without_items
FROM order_payments p
LEFT JOIN order_items i
    ON p.order_id = i.order_id
WHERE i.order_id IS NULL;

-- Optional diagnostic: status distribution for payment-side orders
-- with no order items. This is descriptive, not causal.
WITH payment_orders_without_items AS (
    SELECT DISTINCT
        p.order_id
    FROM order_payments p
    LEFT JOIN order_items i
        ON p.order_id = i.order_id
    WHERE i.order_id IS NULL
)

SELECT
    o.order_status,
    COUNT(*) AS order_count
FROM payment_orders_without_items p
JOIN orders o
    ON p.order_id = o.order_id
GROUP BY 1
ORDER BY 2 DESC;


-- ============================================================
-- Q34
-- ============================================================

-- Hour precision is an acceptable elapsed-duration implementation.

-- Reference SQL:
SELECT
    c.customer_state,
    COUNT(*) AS delivered_orders,
    ROUND(
        AVG(
            DATEDIFF(
                'hour',
                o.order_purchase_timestamp,
                o.order_delivered_customer_date
            )
        ) / 24.0,
        2
    ) AS avg_delivery_days
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
    AND o.order_purchase_timestamp IS NOT NULL
    AND o.order_delivered_customer_date IS NOT NULL
GROUP BY 1
ORDER BY 3 DESC;


-- ============================================================
-- Q35
-- ============================================================

-- Reference SQL:
WITH requested_orders AS (
    SELECT
        MONTH(order_purchase_timestamp) AS order_month,
        COUNT(*) AS all_monthly_orders,
        SUM(
            CASE
                WHEN order_status = 'canceled' THEN 1
                ELSE 0
            END
        ) AS canceled_orders
    FROM orders
    WHERE YEAR(order_purchase_timestamp) = 2017
    GROUP BY 1
)

SELECT
    order_month,
    all_monthly_orders,
    canceled_orders,
    ROUND(
        canceled_orders * 100.0 / all_monthly_orders,
        2
    ) AS canceled_percentage
FROM requested_orders
ORDER BY order_month;


-- ============================================================
-- Q36
-- ============================================================

-- Submitted reviews are analysed at review_id grain regardless of current
-- order status. Order attribution is not required for this review-year metric.

-- Reference SQL:
WITH reviews AS (
    SELECT DISTINCT
        review_id,
        review_score,
        YEAR(review_answer_timestamp) AS review_year
    FROM order_reviews
    WHERE review_answer_timestamp IS NOT NULL
),

yearly_reviews AS (
    SELECT
        review_year,
        AVG(review_score) AS avg_review
    FROM reviews
    GROUP BY 1
),

with_previous AS (
    SELECT
        review_year,
        avg_review,
        LAG(avg_review) OVER (
            ORDER BY review_year
        ) AS previous_review
    FROM yearly_reviews
)

SELECT
    review_year,
    avg_review,
    previous_review,
    ROUND(
        (avg_review - previous_review)
        * 100.0 / previous_review,
        2
    ) AS yoy_change_percentage
FROM with_previous
ORDER BY review_year;

-- Time-coverage validation query. Use the same review grain as the
-- benchmark calculation so duplicate order mappings do not add weight.
WITH reviews AS (
    SELECT DISTINCT
        review_id,
        review_answer_timestamp
    FROM order_reviews
    WHERE review_answer_timestamp IS NOT NULL
)

SELECT
    YEAR(review_answer_timestamp) AS review_year,
    MIN(review_answer_timestamp) AS first_review,
    MAX(review_answer_timestamp) AS last_review,
    COUNT(DISTINCT MONTH(review_answer_timestamp)) AS months_present
FROM reviews
GROUP BY 1
ORDER BY 1;
