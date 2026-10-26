"""
Retail Sales Analytics - Star Schema Dimensional Model Exporter
Deconstructs the cleaned retail sales dataset into normalized Dimensional and Fact tables
optimized for Power BI, Tableau, and enterprise data warehousing.
"""

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pandas as pd
from src.utils import get_project_root, setup_logger

logger = setup_logger("star_schema")

def export_star_schema():
    root = get_project_root()
    cleaned_csv = root / "data" / "processed" / "retail_sales_cleaned.csv"
    output_dir = root / "data" / "processed" / "star_schema"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading cleaned dataset: {cleaned_csv}")
    df = pd.read_csv(cleaned_csv)

    # 1. Dim_Customer
    dim_customer = df[[
        "customer_id", "customer_gender", "customer_age", "age_group", "customer_region", "customer_type"
    ]].drop_duplicates(subset=["customer_id"]).sort_values("customer_id").reset_index(drop=True)
    dim_customer.to_csv(output_dir / "Dim_Customer.csv", index=False)
    logger.info(f"Dim_Customer exported: {len(dim_customer)} records")

    # 2. Dim_Product
    dim_product = df[[
        "product_id", "product_name", "product_category", "unit_price"
    ]].drop_duplicates(subset=["product_id"]).sort_values("product_id").reset_index(drop=True)
    dim_product.to_csv(output_dir / "Dim_Product.csv", index=False)
    logger.info(f"Dim_Product exported: {len(dim_product)} records")

    # 3. Dim_Date
    dim_date = df[[
        "date", "year", "month", "month_name", "year_month", "day", "day_name", "day_of_week", "quarter", "is_weekend"
    ]].drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
    dim_date.to_csv(output_dir / "Dim_Date.csv", index=False)
    logger.info(f"Dim_Date exported: {len(dim_date)} records")

    # 4. Dim_Store
    dim_store = df[[
        "store_location", "sales_channel"
    ]].drop_duplicates().sort_values(["sales_channel", "store_location"]).reset_index(drop=True)
    dim_store["store_id"] = [f"LOC-{i+1:02d}" for i in range(len(dim_store))]
    dim_store = dim_store[["store_id", "store_location", "sales_channel"]]
    dim_store.to_csv(output_dir / "Dim_Store.csv", index=False)
    logger.info(f"Dim_Store exported: {len(dim_store)} records")

    # 5. Fact_Sales
    fact_sales = df.merge(dim_store, on=["store_location", "sales_channel"], how="left")
    fact_sales = fact_sales[[
        "transaction_id", "date", "customer_id", "product_id", "store_id",
        "quantity", "unit_price", "discount_percent", "discount_amount",
        "gross_amount", "net_amount", "tax_amount", "total_amount",
        "payment_method", "sales_channel", "store_location", "order_status",
        "is_outlier"
    ]]
    fact_sales.to_csv(output_dir / "Fact_Sales.csv", index=False)
    logger.info(f"Fact_Sales exported: {len(fact_sales)} records")

    print(f"\n[STAR SCHEMA EXPORT COMPLETE]: {output_dir}")
    print(f"  * Dim_Customer : {len(dim_customer)} unique customers")
    print(f"  * Dim_Product  : {len(dim_product)} unique SKUs")
    print(f"  * Dim_Date     : {len(dim_date)} calendar dates (2024)")
    print(f"  * Dim_Store    : {len(dim_store)} sales channels / locations")
    print(f"  * Fact_Sales   : {len(fact_sales)} transactional sales facts")

if __name__ == "__main__":
    export_star_schema()
