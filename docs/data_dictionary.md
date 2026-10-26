# Retail Sales Analytics — Data Dictionary

## 1. Overview
This document defines the schema, data types, validation constraints, and business logic for the **Retail Sales** dataset (`data/raw/retail_sales.csv`).

- **Total Records**: 2,500 rows
- **Total Columns**: 20 attributes
- **Time Coverage**: 2024-01-01 to 2024-12-31
- **File Format**: Standard CSV (UTF-8 encoding, comma-delimited)
- **Primary Key**: `transaction_id`

---

## 2. Entity Schema & Field Specifications

| Column Name | Data Type | Nullable | Domain / Allowed Values | Example Value | Description & Business Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | String (`object`) | **No** | Unique pattern: `TXN-10001` to `TXN-99999` | `TXN-10042` | Primary Key. Globally unique identifier for each retail checkout transaction. Must never contain duplicates or nulls. |
| `date` | Date (`YYYY-MM-DD`) | **No** | Valid ISO 8601 calendar date (`2024-01-01` to `2024-12-31`) | `2024-06-15` | The date on which the purchase occurred. Used for temporal aggregation, trend identification, and seasonality modeling. |
| `customer_id` | String (`object`) | **No** | Pattern: `CUST-1001` to `CUST-1500` | `CUST-1120` | Foreign Key representing the purchasing customer. Allows tracking repeat purchases, frequency, and customer lifetime value (CLV). |
| `customer_gender` | Categorical (`object`) | **No** | `Male`, `Female`, `Non-Binary`, `Prefer not to say` | `Female` | Self-reported customer gender identity for demographic cohort analysis. |
| `customer_age` | Integer (`int64`) | **No** | $18 \le \text{age} \le 100$ | `36` | Age of customer in full years at transaction time. Used for generational segmentation (Gen Z, Millennial, Gen X, Boomer). |
| `customer_region` | Categorical (`object`) | **No** | `North`, `South`, `East`, `West`, `Midwest` | `East` | Geographic territory where customer resides. Enables regional sales volume and penetration analysis. |
| `customer_type` | Categorical (`object`) | **No** | `Regular`, `Member`, `VIP` | `VIP` | Loyalty tier of the customer. Influences default discount eligibility (VIP: 10–25%, Member: 0–15%, Regular: 0–10%). |
| `product_id` | String (`object`) | **No** | Pattern: `PROD-XX-01` to `PROD-XX-08` | `PROD-EL-01` | Foreign Key representing unique SKU/product item in the catalog. |
| `product_category` | Categorical (`object`) | **No** | `Electronics`, `Apparel`, `Home & Kitchen`, `Beauty & Personal Care`, `Sports & Outdoors`, `Books & Media` | `Electronics` | High-level product department for category performance and gross margin reporting. |
| `product_name` | String (`object`) | **No** | Catalog product names (text) | `Wireless Noise-Canceling Headphones` | Descriptive name of the retail merchandise item. |
| `quantity` | Integer (`int64`) | **No** | Integer $\ge 1$ (typically $1 \le q \le 8$) | `2` | Number of product units purchased in the order line. |
| `unit_price` | Float (`float64`) | **No** | Positive currency float $> 0.0$ | `149.99` | List retail price per unit in USD ($) prior to discounts. |
| `discount_percent`| Float (`float64`) | **No** | $0.00 \le \text{rate} \le 0.25$ | `0.15` | Promotional or loyalty discount percentage applied (e.g., 0.15 = 15% discount). |
| `discount_amount` | Float (`float64`) | **No** | Currency float $\ge 0.0$ | `44.99` | Monetary value deducted: $\text{round}(\text{quantity} \times \text{unit\_price} \times \text{discount\_percent}, 2)$. |
| `tax_amount` | Float (`float64`) | **No** | Currency float $\ge 0.0$ | `20.40` | Sales tax calculated at 8% on net taxable amount: $\text{round}((\text{gross} - \text{discount\_amount}) \times 0.08, 2)$. |
| `total_amount` | Float (`float64`) | **No** | Currency float $> 0.0$ | `275.39` | Final transaction gross billed amount: $\text{round}((\text{gross} - \text{discount\_amount}) + \text{tax\_amount}, 2)$. |
| `payment_method` | Categorical (`object`) | **No** | `Credit Card`, `Debit Card`, `PayPal`, `Cash`, `Digital Wallet` | `Credit Card` | Tender method used for order settlement. Cash is restricted to In-Store transactions. |
| `sales_channel` | Categorical (`object`) | **No** | `Online`, `In-Store`, `Mobile App` | `Online` | Distribution touchpoint where order was placed. |
| `store_location` | Categorical (`object`) | **No** | `New York`, `Los Angeles`, `Chicago`, `Houston`, `Phoenix`, `Online Store` | `New York` | Physical retail branch city or 'Online Store' for eCommerce/app orders. |
| `order_status` | Categorical (`object`) | **No** | `Completed`, `Returned`, `Cancelled`, `Pending` | `Completed` | Terminal fulfillment state of order. Completed orders represent realized revenue. |

---

## 3. Mathematical Consistency & Business Rules

All financial figures in the dataset adhere strictly to the following 4-step arithmetic pipeline:

$$
\text{gross\_amount} = \text{quantity} \times \text{unit\_price}
$$

$$
\text{discount\_amount} = \text{round}(\text{gross\_amount} \times \text{discount\_percent}, 2)
$$

$$
\text{taxable\_amount} = \text{round}(\text{gross\_amount} - \text{discount\_amount}, 2)
$$

$$
\text{tax\_amount} = \text{round}(\text{taxable\_amount} \times 0.08, 2)
$$

$$
\text{total\_amount} = \text{round}(\text{taxable\_amount} + \text{tax\_amount}, 2)
$$

### Integrity Constraints:
1. **Zero-Null Policy**: All 20 fields are strictly mandatory. Missing or NaN values violate validation standards.
2. **Channel-Location Consistency**: Any transaction with `sales_channel == 'In-Store'` must have a physical store location (`New York`, `Los Angeles`, `Chicago`, `Houston`, or `Phoenix`). Digital channels (`Online`, `Mobile App`) map exclusively to `Online Store`.
3. **Cash Tender Restriction**: `payment_method == 'Cash'` is only permitted when `sales_channel == 'In-Store'`.
4. **Rounding Precision**: All dollar calculations maintain 2 decimal places to avoid standard floating point drift.

---

## 4. Current Dataset Summary Statistics (Baseline Profile)

- **Total Transaction Count**: 2,500
- **Total Gross Revenue**: $307,881.56
- **Mean Order Value (AOV)**: $123.15
- **Standard Deviation of Order Value**: $124.62
- **Minimum Order Value**: $14.18
- **Maximum Order Value**: $1,619.97
- **Unique Customers**: 494 distinct shoppers
- **Unique Catalog SKUs**: 44 active products
- **Top Product Category**: Electronics ($85,557.29 total revenue)
- **Fulfillment Completion Rate**: 91.48% (Completed), 5.24% (Returned), 2.48% (Cancelled), 0.80% (Pending)
