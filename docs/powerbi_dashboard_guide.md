# Retail Sales Analytics — Power BI Dimensional Modeling & Dashboard Blueprint

> [!IMPORTANT]
> **Environment & Automation Transparency Notice**
> Power BI Desktop does not provide a native headless CLI or terminal automation API for compiling binary `.pbix` files from scratch on Windows without launching the interactive desktop GUI.
> 
> Therefore, in accordance with strict engineering standards, **no fictitious `.pbix` file is claimed to exist**. Instead, this guide provides the complete, production-grade **Star Schema dimensional architecture**, **Theme configuration JSON**, **25+ validated DAX measures**, and **exact visual-by-visual layout blueprints** to construct or import the dashboard into Power BI Desktop in under 10 minutes.

---

## 1. Dimensional Architecture & Data Modeling (Star Schema)

Power BI achieves optimal performance and DAX evaluation speed when structured in a normalized **Star Schema** with one central Fact table and surrounding Dimension tables.

All dimensional tables have already been pre-processed, normalized, and exported to [`data/processed/star_schema/`](file:///c:/Users/chand/OneDrive/Desktop/data/data/processed/star_schema/).

```text
                  +-------------------------+
                  |       Dim_Date          |
                  +-------------------------+
                  | * date (PK)             |
                  |   year, month, quarter  |
                  |   day_name, is_weekend  |
                  +------------+------------+
                               | 1
                               |
                               | * (Many)
+-----------------------+      |      +------------------------+
|     Dim_Customer      |      |      |      Dim_Product       |
+-----------------------+      |      +------------------------+
| * customer_id (PK)    |      |      | * product_id (PK)      |
|   customer_gender     |      |      |   product_name         |
|   customer_age        +---+  |  +---+   product_category     |
|   age_group           | 1 |  |  | 1 |   unit_price           |
|   customer_region     |   |  |  |   +------------------------+
|   customer_type       |   |  |  |
+-----------------------+   |  |  |
                            |  |  |
                  * (Many)  |  |  |  * (Many)
                  +---------+--+--+---------+
                  |       Fact_Sales        |
                  +-------------------------+
                  | * transaction_id (PK)   |
                  |   date (FK)             |
                  |   customer_id (FK)      |
                  |   product_id (FK)       |
                  |   store_id (FK)         |
                  |   quantity              |
                  |   unit_price            |
                  |   discount_percent      |
                  |   discount_amount       |
                  |   gross_amount          |
                  |   net_amount            |
                  |   tax_amount            |
                  |   total_amount          |
                  |   order_status          |
                  +------------+------------+
                               | * (Many)
                               |
                               | 1
                  +------------+------------+
                  |       Dim_Store         |
                  +-------------------------+
                  | * store_id (PK)         |
                  |   store_location        |
                  |   sales_channel         |
                  +-------------------------+
```

### Table Relationships Configuration:
1. `Fact_Sales[date]` $\rightarrow$ `Dim_Date[date]`: **Many-to-One (`* : 1`)**, Single Direction.
2. `Fact_Sales[customer_id]` $\rightarrow$ `Dim_Customer[customer_id]`: **Many-to-One (`* : 1`)**, Single Direction.
3. `Fact_Sales[product_id]` $\rightarrow$ `Dim_Product[product_id]`: **Many-to-One (`* : 1`)**, Single Direction.
4. `Fact_Sales[store_id]` $\rightarrow$ `Dim_Store[store_id]`: **Many-to-One (`* : 1`)**, Single Direction.

---

## 2. Step-by-Step Power BI Desktop Implementation

### Step 1: Ingest Data
1. Launch **Power BI Desktop**.
2. Click **Get Data > Folder** (or **Text/CSV**) and select the directory:
   `c:\Users\chand\OneDrive\Desktop\data\data\processed\star_schema\`
3. Select and load all 5 tables:
   - `Fact_Sales.csv`
   - `Dim_Customer.csv`
   - `Dim_Product.csv`
   - `Dim_Date.csv`
   - `Dim_Store.csv`
4. *(Alternative Quick Method)*: You can also choose **Get Data > Text/CSV** and directly select [`data/processed/retail_sales_cleaned.csv`](file:///c:/Users/chand/OneDrive/Desktop/data/data/processed/retail_sales_cleaned.csv) if you prefer a single unified flat table.

### Step 2: Configure Relationships & Date Table
1. Switch to the **Model View** (left navigation bar, third icon).
2. Connect the primary keys to foreign keys as shown in the diagram above.
3. Select `Dim_Date` in the Fields list > Click **Table Tools > Mark as Date Table** > select `date` as the Date column.

### Step 3: Create Dedicated DAX `_Measures` Table
1. On the **Home** tab, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.
3. Create new measures by clicking **New Measure** and copying from [`docs/powerbi_dax_measures.dax`](file:///c:/Users/chand/OneDrive/Desktop/data/docs/powerbi_dax_measures.dax).
4. Delete the empty default column `Column1`. Notice that the `_Measures` table icon changes to a calculator icon and automatically floats to the top of your Fields pane.

### Step 4: Apply Corporate Visual Theme
1. Go to the **View** tab > expand the **Themes** dropdown.
2. Click **Browse for themes...**
3. Select [`reports/powerbi_theme.json`](file:///c:/Users/chand/OneDrive/Desktop/data/reports/powerbi_theme.json).
4. This instantly configures the corporate color palette (`#1F497D`, `#2B5C8F`, `#FF7F0E`), Segoe UI font typography, card borders, and off-white canvas background (`#F8FAFC`).

---

## 3. Visual-by-Visual Report Page Blueprints

The dashboard is designed as a **4-Page Interactive Suite**:

### PAGE 1: Executive Overview & KPI Cockpit

**Header Banner**: Title: `RETAIL SALES ANALYTICS — EXECUTIVE KPI COCKPIT` (Navy banner `#1F497D`).

#### Visual Layout:
1. **Top KPI Scorecard Band** (6 Card Visuals across top):
   - **Card 1 (Total Revenue)**: Measure = `[Total Revenue]` ($\$307.88\text{K}$).
   - **Card 2 (Realized Sales)**: Measure = `[Realized Revenue]` ($\$279.53\text{K}$). Subtitle: `91.48% Completed`.
   - **Card 3 (AOV)**: Measure = `[Average Order Value (AOV)]` ($\$123.15$).
   - **Card 4 (Orders)**: Measure = `[Total Orders]` ($2,500$).
   - **Card 5 (Customers)**: Measure = `[Distinct Customers]` ($494$).
   - **Card 6 (Refund Leakage)**: Measure = `[Refund Volume $]` ($\$17.64\text{K}$).
2. **Monthly Revenue & Order Volume Trend** (Line and Clustered Column Chart):
   - **X-Axis**: `Dim_Date[year_month]`
   - **Column Y-Axis**: `[Total Revenue]` (Color: Navy `#1F497D`)
   - **Line Y-Axis**: `[Total Orders]` (Color: Orange `#FF7F0E`)
   - *Key Insight*: Highlights November (\$41.5K) and December (\$41.7K) holiday shopping spikes.
3. **Sales Channel Distribution** (Donut Chart):
   - **Legend**: `Fact_Sales[sales_channel]`
   - **Values**: `[Total Revenue]`
   - *Labels*: Show category & percent of total (`Online`: 47.3%, `In-Store`: 31.8%, `Mobile App`: 20.8%).
4. **Product Category Performance** (Clustered Bar Chart):
   - **Y-Axis**: `Dim_Product[product_category]`
   - **X-Axis**: `[Total Revenue]`
   - **Tooltips**: `[Average Order Value (AOV)]`, `[Total Units Sold]`
5. **Interactive Slicers Panel** (Right or Left pane):
   - Date Range Slider (`Dim_Date[date]`)
   - Customer Region dropdown (`Dim_Customer[customer_region]`)
   - Customer Loyalty Tier chips (`Dim_Customer[customer_type]`)

---

### PAGE 2: Product Category & SKU Intelligence

1. **Category Profitability Matrix** (Matrix Visual):
   - **Rows**: `Dim_Product[product_category]` $\rightarrow$ `Dim_Product[product_name]`
   - **Values**: `[Total Revenue]`, `[Category Revenue Share %]`, `[Total Units Sold]`, `[Average Order Value (AOV)]`, `[Return Rate %]`
   - *Conditional Formatting*: Add data bars on `[Total Revenue]` and red background heat on `[Return Rate %]`.
2. **Top 10 Flagship Products** (Horizontal Bar Chart):
   - **Y-Axis**: `Dim_Product[product_name]`
   - **X-Axis**: `[Total Revenue]`
   - **Filter**: Top N = 10 by `[Total Revenue]`.
   - *Visual Leaders*: 4K Smart TV ($39.0K) and Espresso Machine ($26.9K).
3. **Price vs. Demand Elasticity** (Scatter Chart):
   - **X-Axis**: `Dim_Product[unit_price]`
   - **Y-Axis**: `[Total Units Sold]`
   - **Size**: `[Total Revenue]`
   - **Details**: `Dim_Product[product_name]`
   - **Legend**: `Dim_Product[product_category]`

---

### PAGE 3: Customer Demographics & Loyalty Segmentation

1. **Generation Cohort Revenue** (Clustered Column Chart):
   - **X-Axis**: `Dim_Customer[age_group]`
   - **Y-Axis**: `[Total Revenue]`
   - **Legend**: `Dim_Customer[customer_gender]`
   - *Observation*: Gen X (36-50) and Millennials (26-35) account for 76% of total revenue.
2. **Loyalty Tier Spending Matrix** (Treemap Visual):
   - **Category**: `Dim_Customer[customer_type]` (Member, Regular, VIP)
   - **Details**: `Dim_Customer[customer_region]`
   - **Values**: `[Total Revenue]`
3. **Customer Lifetime Value Distribution** (Card & Histogram):
   - `[Customer Lifetime Value (CLV)]`: **$623.24**
   - `[Average Orders per Customer]`: **5.06 visits**
   - Repeat Customer Rate: **100%** (all 494 distinct customers made repeat purchases).

---

### PAGE 4: Fulfillment Audit & Revenue Loss Analysis

1. **Fulfillment Pipeline Status** (Funnel Visual):
   - **Category**: `Fact_Sales[order_status]`
   - **Values**: `[Total Revenue]`
   - *Levels*: Completed ($279.5K) $\rightarrow$ Returned ($17.6K) $\rightarrow$ Cancelled ($7.0K) $\rightarrow$ Pending ($3.8K).
2. **Revenue Leakage Breakdown** (Waterfall Chart):
   - **Category**: Order Status
   - **Y-Axis**: Gross Sales $\rightarrow$ Discounts Granted $\rightarrow$ Refunds Deducted $\rightarrow$ Realized Revenue.
3. **High-Return Risk SKUs** (Table Visual):
   - Filtered for items where `[Returned Orders] > 0` sorted by `[Refund Volume $]` descending.

---

## 4. Key Measure Cross-Validation Checklist

When creating these measures in Power BI Desktop, verify that your cards match the following verified ground-truth values:

| Measure Name | Expected Output | Format |
| :--- | :---: | :---: |
| `[Total Revenue]` | **$307,881.56** | Currency |
| `[Realized Revenue]` | **$279,533.85** | Currency |
| `[Refund Volume $]` | **$17,635.82** | Currency |
| `[Cancellation Loss $]` | **$6,955.34** | Currency |
| `[Average Order Value (AOV)]` | **$123.15** | Currency |
| `[Total Orders]` | **2,500** | Whole Number |
| `[Total Units Sold]` | **4,664** | Whole Number |
| `[Distinct Customers]` | **494** | Whole Number |
| `[Active SKUs]` | **44** | Whole Number |
| `[Fulfillment Rate %]` | **91.48%** | Percentage |
| `[Return Rate %]` | **4.72%** | Percentage |
| `[Cancellation Rate %]` | **2.84%** | Percentage |
