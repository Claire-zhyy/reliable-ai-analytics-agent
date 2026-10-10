# Olist Business Semantics

> Purpose: concise semantic definitions used by Version B of the AI analytics workflow.  
> These are analyst-authored definitions for this controlled case study, not universal business rules.

## 1. Core Definitions

| Area     | Business Concept                  | Definition / Calculation                                                     | Key Notes                                                                                       |
| -------- | --------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Money    | **Merchandise Value**             | `SUM(order_items.price)`                                                     | Product value only; excludes freight                                                            |
| Money    | **Freight Value**                 | `SUM(order_items.freight_value)`                                             | Customer-paid freight amount                                                                    |
| Money    | **Order Value incl. Freight**     | `SUM(price) + SUM(freight_value)`                                            | Reconstructed from `order_items`                                                                |
| Money    | **Payment Value**                 | `SUM(order_payments.payment_value)`                                          | Payment-level amount; aggregate to order level before comparison                                |
| Orders   | **Valid Order**                   | `order_status IN ('approved','invoiced','processing','shipped','delivered')` | Excludes `created`, `canceled`, `unavailable`                                                   |
| Customer | **Customer Identity**             | `customer_unique_id`                                                         | Use across multiple orders; do not use `customer_id` to identify the same real customer         |
| Customer | **Repeat Customer**               | Customer with `>= 2` valid orders                                            | Lifetime definition                                                                              |
| Customer | **Time to Repeat Purchase**       | `second valid order date - first valid order date`                           | Do not use minimum interval across all order pairs                                              |
| Time     | **Monthly Orders / Revenue Date** | `order_purchase_timestamp`                                                   | Default time attribution for monthly reporting                                                  |
| Delivery | **Delivery Time**                 | `order_delivered_customer_date - order_purchase_timestamp`                   | Calculate only for `delivered` orders                                                           |
| Delivery | **On-time Delivery**              | `CAST(order_delivered_customer_date AS DATE) <= CAST(order_estimated_delivery_date AS DATE)` | Compare calendar dates because the estimated field has no time-of-day precision; delivery on the estimated date counts as on-time; denominator = delivered orders with both dates available |
| Product  | **Category Merchandise Sales**    | `SUM(order_items.price)` grouped by category                                 | Valid orders only; excludes freight                                                             |
| Seller   | **Seller Merchandise Sales**      | `SUM(order_items.price)` grouped by `seller_id`                              | Valid orders only; excludes freight                                                             |

### Default Order Population

In normal commercial-analysis questions, an unqualified reference to **orders** defaults to valid commercial orders:

```text
approved
invoiced
processing
shipped
delivered
```

`created`, `canceled`, and `unavailable` are excluded from this default population.

**All order records** explicitly refers to raw order records regardless of status. Questions explicitly concerning canceled, unavailable, created, or other excluded statuses should use the population required by that question.

**Raw-table data-quality and reconciliation analyses use all available records**, not the valid-order population, unless the question explicitly requests a commercial-order filter. This rule applies when the purpose is to identify missing-side records, orphaned relationships, or coverage differences between source tables.

**Review analyses default to submitted review records regardless of the current order status.** Apply a valid-order filter to reviews only when the question explicitly requests reviews for valid orders. A submitted review represents observed customer feedback even when its associated order is canceled, unavailable, or otherwise outside the valid commercial-order population.

## 2. Monetary Semantics

`price`, `freight_value`, and `payment_value` are related but not interchangeable.

The dataset does not provide one canonical field called `revenue`, `sales`, or `GMV`. These terms may refer to different monetary bases depending on the business question.

## 3. Repeat Purchase Semantics

Use `customer_unique_id` to identify the same customer across orders.

**Repeat customer** means:

```text
same customer_unique_id
+ at least 2 valid orders
```

A time-windowed definition such as “repeat within 180 days” is a separate derived metric, not the base definition of repeat customer. If used later, the interval should be measured from the **first valid order to the second valid order**.

## 4. Time & Delivery Semantics

For monthly order or revenue reporting, use `order_purchase_timestamp` by default.

For delivery analysis:

```text
delivery_time =
order_delivered_customer_date
- order_purchase_timestamp
```

Only `delivered` orders enter delivery-time metrics.

Delivery time is an **elapsed-time metric**, not a calendar-boundary count. Equivalent timestamp-difference implementations at second, minute, or hour precision, or a direct timestamp interval, are valid ways to calculate it. `DATEDIFF('day', start_timestamp, end_timestamp)` counts crossed calendar-day boundaries in DuckDB and is not numerically equivalent to elapsed duration.

For on-time delivery:

```text
on_time =
CAST(order_delivered_customer_date AS DATE)
<= CAST(order_estimated_delivery_date AS DATE)
```

`order_estimated_delivery_date` does not contain meaningful time-of-day precision. Compare calendar dates so that an order delivered at any time on the estimated date is classified as on-time.

Orders that are not delivered are not included in the denominator because final delivery performance cannot yet be determined.

## 5. Product / Seller Attribution

For product-category or seller sales analysis, use:

```text
SUM(order_items.price)
```

Do not include `freight_value` in merchandise sales. Do not directly allocate `payment_value` to category or seller because payment is at order/payment grain and an order may contain multiple products or sellers.

`freight_value` is a customer-paid shipping amount, not evidence of logistics profit.

The dataset does not provide enough information to calculate:

- seller or category profitability
- platform commission / take rate
- logistics profit
- advertising revenue
- contribution margin

These should not be inferred.

## 6. Ambiguous Business Questions

Terms such as **best-performing seller**, **best product**, **revenue**, or **GMV** may not have one unique definition.

For example, seller performance could mean:

```text
sales
order volume
delivery performance
review score
cancellation rate
profitability
```


## 7. Scope / Stop Line

This semantic layer intentionally stops at five areas:

1. Money / Revenue
2. Order Status
3. Customer & Repeat Purchase
4. Time & Delivery
5. Product / Seller Attribution

The review-population rule above is a cross-cutting population convention for the existing benchmark questions; it does not introduce additional review metrics or expand the semantic layer's analytical scope.

Do not expand the semantic layer further unless development-benchmark failures reveal a specific missing definition.
