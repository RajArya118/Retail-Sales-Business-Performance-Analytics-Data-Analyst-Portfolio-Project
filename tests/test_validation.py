"""
Unit and Integration Tests for Retail Sales Dataset Validation
Executes automated assertions on data integrity, schema consistency,
business arithmetic, and validator functionality.
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.utils import get_project_root
from src.validator import (
    validate_retail_sales_csv,
    EXPECTED_SCHEMA,
    ALLOWED_ENUMS,
)


@pytest.fixture(scope="module")
def dataset_path() -> Path:
    root = get_project_root()
    path = root / "data" / "raw" / "retail_sales.csv"
    assert path.exists(), f"Target dataset does not exist at: {path}"
    return path


@pytest.fixture(scope="module")
def df(dataset_path: Path) -> pd.DataFrame:
    data = pd.read_csv(dataset_path)
    return data


def test_file_existence_and_size(dataset_path: Path):
    """Verifies that the CSV exists and has a healthy file size (> 100 KB)."""
    assert dataset_path.exists()
    file_size_kb = dataset_path.stat().st_size / 1024
    assert file_size_kb > 100, f"File size too small: {file_size_kb} KB"


def test_row_and_column_counts(df: pd.DataFrame):
    """Verifies expected record count (2,500) and column count (20)."""
    assert len(df) == 2500, f"Expected 2,500 rows, found {len(df)}"
    assert df.shape[1] == 20, f"Expected 20 columns, found {df.shape[1]}"


def test_schema_column_names(df: pd.DataFrame):
    """Verifies all expected schema columns are present with no missing keys."""
    expected_cols = set(EXPECTED_SCHEMA.keys())
    actual_cols = set(df.columns)
    missing = expected_cols - actual_cols
    assert len(missing) == 0, f"Missing schema columns: {missing}"


def test_no_missing_or_null_values(df: pd.DataFrame):
    """Ensures 100% data completeness with zero null or NaN values."""
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    assert total_nulls == 0, f"Found {total_nulls} null values: {null_counts[null_counts > 0].to_dict()}"


def test_primary_key_uniqueness(df: pd.DataFrame):
    """Ensures every transaction_id is globally unique."""
    total_records = len(df)
    unique_txns = df["transaction_id"].nunique()
    assert total_records == unique_txns, f"Duplicate transaction IDs detected: {total_records - unique_txns}"


def test_date_range_and_formats(df: pd.DataFrame):
    """Validates date format (YYYY-MM-DD) and ensures dates fall within 2024."""
    parsed_dates = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    assert parsed_dates.notnull().all(), "Some date entries failed YYYY-MM-DD parsing"
    assert parsed_dates.min() >= pd.Timestamp("2024-01-01")
    assert parsed_dates.max() <= pd.Timestamp("2024-12-31")


def test_numerical_positive_constraints(df: pd.DataFrame):
    """Verifies positive values for quantities, unit prices, and totals."""
    assert (df["quantity"] > 0).all(), "Found non-positive quantities"
    assert (df["unit_price"] > 0.0).all(), "Found non-positive unit prices"
    assert (df["total_amount"] > 0.0).all(), "Found non-positive total amounts"
    assert df["discount_percent"].between(0.0, 1.0).all(), "Discount percent outside [0, 1]"
    assert (df["discount_amount"] >= 0.0).all(), "Negative discount amounts found"
    assert (df["tax_amount"] >= 0.0).all(), "Negative tax amounts found"
    assert df["customer_age"].between(18, 100).all(), "Customer ages outside [18, 100]"


def test_arithmetic_consistency(df: pd.DataFrame):
    """
    Validates arithmetic integrity:
    1. gross = quantity * unit_price
    2. discount_amount == round(gross * discount_percent, 2)
    3. tax_amount == round((gross - discount_amount) * 0.08, 2)
    4. total_amount == round((gross - discount_amount) + tax_amount, 2)
    """
    gross = df["quantity"] * df["unit_price"]
    expected_disc = (gross * df["discount_percent"]).round(2)
    disc_diff = (df["discount_amount"] - expected_disc).abs()
    assert (disc_diff <= 0.02).all(), "Discount amount calculation mismatch"

    taxable = (gross - df["discount_amount"]).round(2)
    expected_tax = (taxable * 0.08).round(2)
    tax_diff = (df["tax_amount"] - expected_tax).abs()
    assert (tax_diff <= 0.02).all(), "Tax amount calculation mismatch"

    expected_total = (taxable + df["tax_amount"]).round(2)
    total_diff = (df["total_amount"] - expected_total).abs()
    assert (total_diff <= 0.02).all(), "Total amount calculation mismatch"


def test_categorical_enums(df: pd.DataFrame):
    """Validates that categorical fields conform strictly to defined enum sets."""
    for col_name, allowed_values in ALLOWED_ENUMS.items():
        unique_vals = set(df[col_name].dropna().unique())
        disallowed = unique_vals - allowed_values
        assert len(disallowed) == 0, f"Disallowed values in '{col_name}': {disallowed}"


def test_channel_and_store_alignment(df: pd.DataFrame):
    """Ensures In-Store purchases correspond to brick-and-mortar stores and digital to Online Store."""
    in_store_online_loc = df[(df["sales_channel"] == "In-Store") & (df["store_location"] == "Online Store")]
    assert len(in_store_online_loc) == 0, "In-Store transactions mapped to Online Store location"

    digital_sales = df[df["sales_channel"].isin(["Online", "Mobile App"])]
    assert (digital_sales["store_location"] == "Online Store").all(), "Digital channels must map to Online Store"


def test_validator_module_end_to_end(dataset_path: Path):
    """Executes the validator module and asserts clean pass with 0 errors."""
    result = validate_retail_sales_csv(dataset_path)
    assert result.is_valid, f"Validator failed with errors: {result.errors}"
    assert result.checks_failed == 0
    assert result.checks_passed >= 20
    assert result.summary_stats["total_records"] == 2500
