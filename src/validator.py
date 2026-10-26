"""
Retail Sales Analytics - Comprehensive Data Validator
Validates dataset schema, nullability, relational integrity, arithmetic precision,
range constraints, categorical enums, and anomaly boundaries.
"""

import sys
from pathlib import Path
from typing import Any
import pandas as pd
import numpy as np

try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.utils import get_project_root, setup_logger, print_section

logger = setup_logger("validator")

EXPECTED_SCHEMA = {
    "transaction_id": "object",
    "date": "object",
    "customer_id": "object",
    "customer_gender": "object",
    "customer_age": "int64",
    "customer_region": "object",
    "customer_type": "object",
    "product_id": "object",
    "product_category": "object",
    "product_name": "object",
    "quantity": "int64",
    "unit_price": "float64",
    "discount_percent": "float64",
    "discount_amount": "float64",
    "tax_amount": "float64",
    "total_amount": "float64",
    "payment_method": "object",
    "sales_channel": "object",
    "store_location": "object",
    "order_status": "object",
}

ALLOWED_ENUMS = {
    "customer_gender": {"Male", "Female", "Non-Binary", "Prefer not to say"},
    "customer_region": {"North", "South", "East", "West", "Midwest"},
    "customer_type": {"Member", "Regular", "VIP"},
    "product_category": {
        "Electronics",
        "Apparel",
        "Home & Kitchen",
        "Beauty & Personal Care",
        "Sports & Outdoors",
        "Books & Media",
    },
    "payment_method": {"Credit Card", "Debit Card", "PayPal", "Cash", "Digital Wallet"},
    "sales_channel": {"Online", "In-Store", "Mobile App"},
    "order_status": {"Completed", "Returned", "Cancelled", "Pending"},
}


class DataValidationResult:
    """Encapsulates validation findings and pass/fail status."""
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks_passed: int = 0
        self.checks_failed: int = 0
        self.summary_stats: dict[str, Any] = {}

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, message: str):
        self.errors.append(message)
        self.checks_failed += 1

    def add_warning(self, message: str):
        self.warnings.append(message)

    def record_pass(self):
        self.checks_passed += 1


def validate_retail_sales_csv(file_path: Path | str) -> DataValidationResult:
    """
    Executes a rigorous suite of data quality checks on the retail sales CSV.
    """
    result = DataValidationResult()
    path = Path(file_path)

    # 1. Existence and File Size Check
    if not path.exists():
        result.add_error(f"File not found at: {path}")
        return result
    
    file_size_kb = path.stat().st_size / 1024
    if file_size_kb == 0:
        result.add_error(f"File is empty (0 bytes): {path}")
        return result
    result.record_pass()

    # Load dataset
    try:
        df = pd.read_csv(path)
    except Exception as e:
        result.add_error(f"Failed to parse CSV file: {e}")
        return result

    # 2. Row and Column Dimension Check
    if len(df) == 0:
        result.add_error("Dataset contains 0 data rows.")
        return result
    result.record_pass()

    # 3. Schema & Column Presence Check
    actual_cols = list(df.columns)
    missing_cols = set(EXPECTED_SCHEMA.keys()) - set(actual_cols)
    unexpected_cols = set(actual_cols) - set(EXPECTED_SCHEMA.keys())

    if missing_cols:
        result.add_error(f"Missing required columns: {sorted(list(missing_cols))}")
    else:
        result.record_pass()

    if unexpected_cols:
        result.add_warning(f"Unexpected extra columns detected: {sorted(list(unexpected_cols))}")

    # Stop early if schema is broken
    if missing_cols:
        return result

    # 4. Completeness & Null Value Check
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    if total_nulls > 0:
        bad_cols = null_counts[null_counts > 0].to_dict()
        result.add_error(f"Dataset contains {total_nulls} null values in columns: {bad_cols}")
    else:
        result.record_pass()

    # 5. Primary Key Uniqueness Check (transaction_id)
    dup_txns = df["transaction_id"].duplicated().sum()
    if dup_txns > 0:
        result.add_error(f"Duplicate transaction_id values found: {dup_txns} duplicates.")
    else:
        result.record_pass()

    # 6. Relational & Format Constraints
    # Date parsing check
    try:
        parsed_dates = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="raise")
        min_date = parsed_dates.min().strftime("%Y-%m-%d")
        max_date = parsed_dates.max().strftime("%Y-%m-%d")
        result.record_pass()
    except Exception as e:
        result.add_error(f"Invalid date format in 'date' column: {e}")
        min_date, max_date = "N/A", "N/A"

    # Numeric Range Checks
    # Quantity > 0 and integer
    if not (df["quantity"] > 0).all():
        invalid_qty = int((df["quantity"] <= 0).sum())
        result.add_error(f"Non-positive quantities found: {invalid_qty} rows.")
    else:
        result.record_pass()

    # Unit price > 0
    if not (df["unit_price"] > 0.0).all():
        invalid_price = int((df["unit_price"] <= 0.0).sum())
        result.add_error(f"Non-positive unit prices found: {invalid_price} rows.")
    else:
        result.record_pass()

    # Discount percent between 0.0 and 1.0
    if not df["discount_percent"].between(0.0, 1.0).all():
        invalid_disc = int((~df["discount_percent"].between(0.0, 1.0)).sum())
        result.add_error(f"Discount percent out of bounds [0.0, 1.0]: {invalid_disc} rows.")
    else:
        result.record_pass()

    # Total amount > 0
    if not (df["total_amount"] > 0.0).all():
        invalid_totals = int((df["total_amount"] <= 0.0).sum())
        result.add_error(f"Non-positive total amounts found: {invalid_totals} rows.")
    else:
        result.record_pass()

    # Customer age between 18 and 100
    if not df["customer_age"].between(18, 100).all():
        invalid_age = int((~df["customer_age"].between(18, 100)).sum())
        result.add_error(f"Customer age out of realistic bounds [18, 100]: {invalid_age} rows.")
    else:
        result.record_pass()

    # 7. Categorical Domain / Enum Checks
    for col_name, allowed_values in ALLOWED_ENUMS.items():
        unique_vals = set(df[col_name].dropna().unique())
        disallowed = unique_vals - allowed_values
        if disallowed:
            result.add_error(f"Disallowed values in categorical column '{col_name}': {disallowed}")
        else:
            result.record_pass()

    # 8. Business Logic & Mathematical Consistency Checks
    # Calculation 1: Gross = quantity * unit_price
    expected_gross = df["quantity"] * df["unit_price"]
    
    # Calculation 2: discount_amount = round(gross * discount_percent, 2)
    expected_disc_amt = (expected_gross * df["discount_percent"]).round(2)
    disc_diff = (df["discount_amount"] - expected_disc_amt).abs()
    if (disc_diff > 0.02).any():
        bad_rows = int((disc_diff > 0.02).sum())
        result.add_error(f"Discount amount arithmetic mismatch: {bad_rows} rows exceed $0.02 tolerance.")
    else:
        result.record_pass()

    # Calculation 3: taxable_amount = gross - discount_amount
    taxable_amt = (expected_gross - df["discount_amount"]).round(2)
    expected_tax = (taxable_amt * 0.08).round(2)
    tax_diff = (df["tax_amount"] - expected_tax).abs()
    if (tax_diff > 0.02).any():
        bad_rows = int((tax_diff > 0.02).sum())
        result.add_error(f"Tax amount arithmetic mismatch: {bad_rows} rows exceed $0.02 tolerance.")
    else:
        result.record_pass()

    # Calculation 4: total_amount = round(taxable + tax_amount, 2)
    expected_total = (taxable_amt + df["tax_amount"]).round(2)
    total_diff = (df["total_amount"] - expected_total).abs()
    if (total_diff > 0.02).any():
        bad_rows = int((total_diff > 0.02).sum())
        result.add_error(f"Total amount arithmetic mismatch: {bad_rows} rows exceed $0.02 tolerance.")
    else:
        result.record_pass()

    # 9. Channel / Store Consistency
    # In-Store sales must have a physical store location
    instore_missing_loc = df[(df["sales_channel"] == "In-Store") & (df["store_location"] == "Online Store")]
    if len(instore_missing_loc) > 0:
        result.add_error(f"In-Store sales mapped to 'Online Store' location: {len(instore_missing_loc)} rows.")
    else:
        result.record_pass()

    # Calculate summary metrics for report
    result.summary_stats = {
        "file_path": str(path),
        "file_size_kb": round(file_size_kb, 2),
        "total_records": len(df),
        "total_columns": len(df.columns),
        "date_range": f"{min_date} to {max_date}",
        "total_revenue": round(float(df["total_amount"].sum()), 2),
        "average_order_value": round(float(df["total_amount"].mean()), 2),
        "distinct_customers": int(df["customer_id"].nunique()),
        "distinct_products": int(df["product_id"].nunique()),
        "top_category_by_revenue": df.groupby("product_category")["total_amount"].sum().idxmax(),
        "top_category_revenue": round(float(df.groupby("product_category")["total_amount"].sum().max()), 2),
        "completion_rate_pct": round(float((df["order_status"] == "Completed").mean() * 100), 2),
    }

    return result


def print_validation_report(result: DataValidationResult) -> None:
    """Formats and prints the validation findings to console."""
    print_section("Retail Sales Data Validation Report")
    
    status_str = "[PASS] PASSED" if result.is_valid else "[FAIL] FAILED"
    print(f"Overall Status:       {status_str}")
    print(f"Checks Passed:        {result.checks_passed}")
    print(f"Checks Failed:        {result.checks_failed}")
    print(f"Warnings Logged:      {len(result.warnings)}")
    
    if result.summary_stats:
        print("\n--- DATASET PROFILE & SUMMARY STATISTICS ---")
        for key, val in result.summary_stats.items():
            formatted_key = key.replace("_", " ").title()
            if "Revenue" in formatted_key or "Value" in formatted_key:
                print(f"  * {formatted_key:28}: ${val:,.2f}" if isinstance(val, (int, float)) else f"  * {formatted_key:28}: {val}")
            else:
                print(f"  * {formatted_key:28}: {val}")

    if result.errors:
        print("\n--- CRITICAL VALIDATION ERRORS ---")
        for err in result.errors:
            print(f"  [FAIL] {err}")

    if result.warnings:
        print("\n--- WARNINGS & ADVISORIES ---")
        for warn in result.warnings:
            print(f"  [WARN] {warn}")

    print("\n" + "=" * 70 + "\n")


def main():
    root = get_project_root()
    dataset_path = root / "data" / "raw" / "retail_sales.csv"
    
    logger.info(f"Initiating validation on: {dataset_path}")
    result = validate_retail_sales_csv(dataset_path)
    print_validation_report(result)

    if not result.is_valid:
        logger.error("Validation FAILED with errors.")
        sys.exit(1)
    else:
        logger.info("Validation SUCCEEDED. All data quality gates passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
