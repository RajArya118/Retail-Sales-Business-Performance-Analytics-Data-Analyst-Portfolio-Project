# Retail Sales Analytics

[![Status](https://img.shields.io/badge/Project%20Status-Phases%201--5%20Complete-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue)]()
[![Database](https://img.shields.io/badge/Database-SQLite%203.51-blue)]()
[![Validation](https://img.shields.io/badge/Data%20Validation-22%2F22%20Passed-success)]()
[![Tests](https://img.shields.io/badge/Pytest-16%2F16%20Passed-success)]()

A modular, production-grade analytics, business intelligence, and modeling platform for multi-channel retail operations. This project provides end-to-end capabilities spanning deterministic data synthesis, automated data quality auditing, exploratory data analysis with Seaborn/Matplotlib, relational SQLite data modeling with window functions, executive multi-tab Excel dashboarding with openpyxl, Star Schema dimensional modeling for Power BI, and complete DAX measure libraries.

---

## Project Structure

```text
retail-sales-analytics/
├── charts/                           # High-resolution (300 DPI) EDA visualizations
│   ├── 01_monthly_sales_trend.png
│   ├── 02_revenue_by_category.png
│   ├── 03_sales_channel_distribution.png
│   ├── 04_customer_age_distribution.png
│   ├── 05_discount_vs_order_value.png
│   ├── 06_regional_performance.png
│   ├── 07_order_status_breakdown.png
│   └── 08_correlation_heatmap.png
├── data/
│   ├── raw/
│   │   └── retail_sales.csv         # 2,500 raw transactions ($307.8k revenue)
│   ├── processed/
│   │   ├── retail_sales_cleaned.csv # Enriched dataset (34 features, 0 nulls)
│   │   └── star_schema/             # Normalized dimensional tables
│   │       ├── Dim_Customer.csv     # 494 unique customer profiles
│   │       ├── Dim_Product.csv      # 44 catalog SKUs across 6 departments
│   │       ├── Dim_Date.csv         # 366 calendar dates in 2024
│   │       ├── Dim_Store.csv        # 7 channel / store locations
│   │       └── Fact_Sales.csv       # 2,500 transactional fact rows
│   └── retail_sales.db              # SQLite database (tables, indices, 4 views)
├── docs/
│   ├── project_plan.md              # 6-Phase implementation roadmap
│   ├── data_dictionary.md           # Schema definitions, types, and business rules
│   ├── environment_setup.md         # Environment setup instructions (Conda & venv)
│   ├── excel_pivottables_guide.md   # Step-by-step manual Excel PivotTable instructions
│   ├── powerbi_dashboard_guide.md   # Power BI Star Schema & 4-page dashboard blueprint
│   └── powerbi_dax_measures.dax     # 25+ copy-paste-ready DAX measure formulas
├── notebooks/
│   └── 01_data_cleaning_and_eda.ipynb # Interactive exploration and storytelling notebook
├── reports/
│   ├── Retail_Sales_Analytics_Dashboard.xlsx # Multi-tab styled Excel workbook
│   ├── powerbi_theme.json           # Corporate color & typography theme
│   └── figures/                     # Mirrored high-resolution figures
├── scripts/
│   ├── export_star_schema.py        # Dimensional table export pipeline
│   └── generate_notebook.py         # Automated Jupyter notebook builder
├── sql/
│   ├── schema.sql                   # DDL: tables, check constraints, indices, views
│   └── analysis_queries.sql         # 12 core business queries (MoM, CLV, leakage)
├── src/
│   ├── __init__.py                  # Source package namespace
│   ├── utils.py                     # Logging, paths, and formatting helpers
│   ├── data_generator.py            # Reproducible retail transactions generator
│   ├── validator.py                 # 22-point data quality enforcement engine
│   ├── eda_cleaning.py              # Data cleaning, feature engineering, and EDA charts
│   ├── database.py                  # SQLite initialization and SQL execution runner
│   └── excel_generator.py           # Automated openpyxl dashboard generator
├── tests/
│   ├── __init__.py                  # Test package namespace
│   ├── test_validation.py           # 11 validation unit & integration tests
│   └── test_sql_queries.py          # 5 database & SQL parity tests
├── environment.yml                  # Conda environment definition
├── requirements.txt                 # Pip dependencies
└── README.md                        # Master project documentation
```

---

## Phase Status Overview

| Phase | Description | Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Foundations & Architecture** | Project Plan, Directory Layout, Environment Specs | **COMPLETED** |
| **Phase 2** | **Data Acquisition & Validation** | 2,500-Row Dataset, Data Dictionary, Validation Engine, Test Suite | **COMPLETED** |
| **Phase 3** | **Exploratory Data Analysis** | Data Cleaning, 8 High-Res Charts, Cleaned CSV, EDA Notebook | **COMPLETED** |
| **Phase 4** | **Database & SQL Analytics** | SQLite Database, 12 SQL Business Queries, Test Suite | **COMPLETED** |
| **Phase 5** | **Executive Dashboards (Excel & Power BI)**| Excel Dashboard, Power BI Star Schema, DAX Library, Theme & Guide | **COMPLETED** |
| **Phase 6** | **Pipeline Automation** | Automated ETL Batch Jobs, CI/CD Integration | *Planned* |

---

## Quick Start Guide

### 1. Set Up Environment
See [environment_setup.md](file:///c:/Users/chand/OneDrive/Desktop/data/docs/environment_setup.md) for full details.
```bash
# Using venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # (Windows) or source .venv/bin/activate (macOS/Linux)
pip install -r requirements.txt

# Or using Conda
conda env create -f environment.yml
conda activate retail-sales-analytics
```

### 2. Generate or Refresh the Dataset
```bash
python -m src.data_generator
```

### 3. Run Data Validation
```bash
python -m src.validator
```

### 4. Run Data Cleaning & Generate EDA Charts
```bash
python -m src.eda_cleaning
```

### 5. Setup Database & Execute SQL Analysis Queries
```bash
python -m src.database
```

### 6. Generate Executive Excel Dashboard
```bash
python -m src.excel_generator
```

### 7. Execute the Complete Test Suite
```bash
pytest -v
```

---

## Dataset Profile (Phase 2 Baseline)

- **Source File**: [`data/raw/retail_sales.csv`](file:///c:/Users/chand/OneDrive/Desktop/data/data/raw/retail_sales.csv)
- **Total Records**: 2,500 transactions
- **Total Columns**: 20 attributes
- **Date Range**: `2024-01-01` to `2024-12-31`
- **Total Gross Revenue**: $307,881.56
- **Average Order Value (AOV)**: $123.15
- **Unique Customers**: 494 distinct customers
- **Unique Products**: 44 SKUs across 6 categories
- **Top Category by Revenue**: Electronics ($85,557.29)
- **Order Completion Rate**: 91.48% (Completed), 5.24% (Returned), 2.48% (Cancelled), 0.80% (Pending)

For field-by-field definitions and mathematical formulas, see the [Data Dictionary](file:///c:/Users/chand/OneDrive/Desktop/data/docs/data_dictionary.md).
