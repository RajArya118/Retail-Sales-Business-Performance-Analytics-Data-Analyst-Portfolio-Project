# Retail Sales Analytics — Excel PivotTable Guide & Manual Instructions

This guide provides accurate, step-by-step instructions for building the core business PivotTables and PivotCharts in **Microsoft Excel** (or Google Sheets) using [`data/processed/retail_sales_cleaned.csv`](file:///c:/Users/chand/OneDrive/Desktop/data/data/processed/retail_sales_cleaned.csv) or the pre-generated [`reports/Retail_Sales_Analytics_Dashboard.xlsx`](file:///c:/Users/chand/OneDrive/Desktop/data/reports/Retail_Sales_Analytics_Dashboard.xlsx).

---

## 1. Data Source Preparation

1. Open Excel and load `retail_sales_cleaned.csv` or navigate to the `Cleaned_Sales_Data` tab in `Retail_Sales_Analytics_Dashboard.xlsx`.
2. Confirm the range: **Rows 1 to 2501**, **Columns A to AH** (2,500 data rows, 34 columns).
3. Convert to an official Excel Table by pressing `Ctrl + T` (ensure "My table has headers" is checked). Name the table `SalesTable`.

---

## 2. PivotTable 1: Monthly Sales & Seasonality Trend

**Goal**: Analyze monthly revenue trajectory, transaction count, and average order value.

### Step-by-Step Configuration:
1. Select any cell inside `SalesTable` > go to **Insert > PivotTable** > choose **New Worksheet**.
2. Rename the new sheet to `PT_Monthly_Trend`.
3. In the **PivotTable Fields** pane, drag and drop the fields into the corresponding areas:
   - **Rows**: `year_month` (Chronological ordering: `2024-01` to `2024-12`)
   - **Values**:
     1. Drag `total_amount` > click arrow > **Value Field Settings** > Summarize by **Sum** > set Number Format to **Currency ($)** (`$#,##0.00`). Rename Custom Name to **Total Revenue**.
     2. Drag `transaction_id` > Summarize by **Count**. Rename to **Order Count**.
     3. Drag `quantity` > Summarize by **Sum**. Rename to **Units Sold**.
     4. Drag `total_amount` again > Summarize by **Average** > set Number Format to **Currency ($)**. Rename to **AOV**.
4. **Calculated Field (MoM Growth Rate)**:
   - Select PivotTable > go to **PivotTable Analyze > Fields, Items, & Sets > Calculated Field**.
   - Or alternatively, right-click any cell in the Total Revenue column > **Show Values As > % Difference From** > Base Field: `year_month`, Base Item: `(previous)`.

---

## 3. PivotTable 2: Product Category & SKU Drilldown

**Goal**: Evaluate category gross margin drivers, top-performing SKUs, and volume.

### Step-by-Step Configuration:
1. Insert a new PivotTable from `SalesTable` > rename sheet to `PT_Category_Performance`.
2. Configure Fields:
   - **Rows**: 
     - 1st level: `product_category`
     - 2nd level (Drilldown): `product_name`
   - **Values**:
     1. `total_amount` (Sum) > Format: **Currency ($)**. Custom Name: **Category Revenue**.
     2. `quantity` (Sum) > Format: **Number (0 decimal places)**. Custom Name: **Units Sold**.
     3. `total_amount` (Average) > Format: **Currency ($)**. Custom Name: **Average Order Value**.
     4. `total_amount` (Sum) > right-click > **Show Values As > % of Column Total**. Custom Name: **Revenue Share %**.
3. **Sorting**: Right-click any category revenue cell > **Sort > Sort Largest to Smallest**.

---

## 4. PivotTable 3: Multi-Channel by Customer Region Matrix

**Goal**: Cross-tabulate geographic demand with distribution channel adoption.

### Step-by-Step Configuration:
1. Insert a new PivotTable > rename sheet to `PT_Channel_Region_Matrix`.
2. Configure Fields:
   - **Rows**: `customer_region` (`East`, `Midwest`, `North`, `South`, `West`)
   - **Columns**: `sales_channel` (`In-Store`, `Mobile App`, `Online`)
   - **Values**: `total_amount` (Sum) > Format as **Currency ($)**.
3. **Totals**: Ensure **Row Grand Totals** and **Column Grand Totals** are enabled via **Design > Grand Totals > On for Rows and Columns**.

---

## 5. PivotTable 4: Customer Demographics & Loyalty Tiers

**Goal**: Identify spending patterns across age cohorts and membership tiers.

### Step-by-Step Configuration:
1. Insert a new PivotTable > rename sheet to `PT_Customer_Demographics`.
2. Configure Fields:
   - **Rows**: `age_group` (`18-25 (Gen Z)`, `26-35 (Millennial)`, `36-50 (Gen X)`, `51-65 (Boomer)`, `65+ (Senior)`)
   - **Columns**: `customer_type` (`Member`, `Regular`, `VIP`)
   - **Values**:
     1. `total_amount` (Sum) > Currency ($).
     2. `transaction_id` (Count) > Number (#,##0).
3. **Filter Area**: Drag `customer_gender` to the **Filters** box to allow segmenting by gender.

---

## 6. PivotTable 5: Fulfillment Quality & Refund Leakage

**Goal**: Monitor order fulfillment completion, returns, and cancellation rates.

### Step-by-Step Configuration:
1. Insert a new PivotTable > rename sheet to `PT_Fulfillment_Audit`.
2. Configure Fields:
   - **Rows**: `order_status` (`Completed`, `Returned`, `Cancelled`, `Pending`)
   - **Values**:
     1. `transaction_id` (Count) > Rename to **Orders**.
     2. `transaction_id` (Count) > right-click > **Show Values As > % of Column Total** > Rename to **Order Share %**.
     3. `total_amount` (Sum) > Currency ($) > Rename to **Monetary Volume**.
     4. `total_amount` (Sum) > right-click > **Show Values As > % of Column Total** > Rename to **Revenue Share %**.

---

## 7. Interactive Slicers & Timeline

To make the workbook an interactive executive dashboard:
1. Select any PivotTable > **PivotTable Analyze > Insert Slicer**.
2. Check the following 4 slicers:
   - `sales_channel`
   - `product_category`
   - `customer_region`
   - `customer_type`
3. Right-click each slicer > **Report Connections...** > check all 5 PivotTables so that clicking a slicer dynamically filters every view simultaneously.
4. Go to **PivotTable Analyze > Insert Timeline** > select `date` to enable dynamic date-range filtering (e.g. filter by Quarter or Month).
