---
type: note
status: active
created: 2026-10-02
updated: 2026-10-02
project: job-search
tags: [type/note, status/active, topic/ai]
---

# Olist Data Dictionary — Model Context

> Purpose: data dictionary supplied to Version B and Version C. It describes schema, grain, relationships, and analytical risks without dataset-derived counts or benchmark answers. The evidence-bearing internal profile remains in `02-tables.md` and must not be supplied to evaluated models.

## `orders`

- Grain: one row per order.
- Primary key: `order_id`.
- Foreign key: `customer_id` → `customers.customer_id`.
- Important fields: `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`.
- Join risk: joining to items, payments, or reviews can duplicate order-level rows because those relationships may be one-to-many.
- Business note: date fields represent different events. Choose the event that matches the question rather than treating the dates as interchangeable.

## `customers`

- Grain: one row per order-specific `customer_id`.
- Primary key: `customer_id`.
- `customer_unique_id` identifies the same customer across multiple orders and is the appropriate identity for customer-level repeat behavior.
- Important fields: customer ZIP prefix, city, and state.
- Join risk: joining orders on `customer_id` preserves order mapping; grouping or joining on `customer_unique_id` can combine multiple orders and must respect customer grain.
- Business note: the recorded location belongs to the order-specific customer record and should not automatically be treated as a permanent customer attribute.

## `geolocation`

- Grain: location observations by ZIP-code prefix; a ZIP prefix may appear in multiple rows.
- No reliable single-column primary key.
- Important fields: ZIP-code prefix, latitude, longitude, city, and state.
- Join risk: directly joining raw geolocation rows to customers or sellers can multiply records. Deduplicate or aggregate to the intended ZIP-level representation before joining.

## `order_items`

- Grain: one item row within an order.
- Primary key: (`order_id`, `order_item_id`).
- Foreign keys: `order_id` → `orders`; `product_id` → `products`; `seller_id` → `sellers`.
- Important fields: `shipping_limit_date`, `price`, and `freight_value`.
- Join risk: joining items to orders changes the grain to item level. Joining items directly to payments on `order_id` can create many-to-many multiplication.
- Business notes: `order_item_id` identifies the item row within an order; it is not a product identifier. The same `product_id` can appear more than once in an order, and observed price or seller can vary across transactions.

## `order_payments`

- Grain: one payment record associated with an order.
- Primary key: (`order_id`, `payment_sequential`).
- Foreign key: `order_id` → `orders.order_id`.
- Important fields: `payment_type`, `payment_installments`, and `payment_value`.
- Join risk: aggregate payment records to order grain before joining them to another one-to-many order table such as `order_items`.
- Business notes: order payment value is the sum of its payment records. `payment_sequential` distinguishes records but should not be used as the payment-record count because source sequences are not guaranteed to be consecutive.

## `order_reviews`

- Grain: one review–order association.
- Key: (`review_id`, `order_id`); neither field is guaranteed unique alone.
- Foreign key: `order_id` → `orders.order_id`.
- Important fields: `review_score`, comment fields, `review_creation_date`, and `review_answer_timestamp`.
- `review_creation_date`: date on which the satisfaction survey was sent to the customer.
- `review_answer_timestamp`: timestamp at which the customer answered the satisfaction survey.
- Join risk: reviews are recorded at order level. Joining them to item, product, or seller rows can repeat a review; define and preserve the intended attribution grain.
- Business note: a `review_id` associated with more than one distinct order has ambiguous order attribution and must not be assigned arbitrarily.

## `products`

- Grain: one row per product.
- Primary key: `product_id`.
- Important fields: category name, text-length metadata, photo count, weight, length, height, and width.
- Join risk: connect products through `order_items.product_id`. Physical attributes may be missing.
- Business note: category values are in Portuguese and may be translated through the category translation table.

## `product_category_name_translation`

- Grain: one translation row per Portuguese product-category value.
- Join field: `product_category_name` → `products.product_category_name`.
- Important field: `product_category_name_english`.
- Join risk: use a left join from products when the analysis should retain categories without a translation.

## `sellers`

- Grain: one row per seller.
- Primary key: `seller_id`.
- Important fields: seller ZIP prefix, city, and state.
- Join path: `orders` → `order_items` → `sellers`.
- Join risk: an order can contain item rows from more than one seller. Order-level outcomes such as delivery time or reviews require an explicit attribution rule before seller-level analysis.

## Cross-table rules

1. Aggregate each one-to-many source to the intended grain before joining it to another one-to-many source.
2. Do not infer row counts, status distributions, benchmark results, or data-quality exception counts from this dictionary; calculate them from the database when the question requires them.
3. Use `03-olist-business-semantics.md` for metric definitions and population rules.
