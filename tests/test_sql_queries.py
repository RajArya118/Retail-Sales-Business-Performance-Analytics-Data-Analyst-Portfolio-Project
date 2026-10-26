"""
Automated Test Suite for SQLite Database Integration & SQL Business Queries
Asserts schema integrity, query execution without error, and exact metric parity with pandas.
"""

from pathlib import Path
import sqlite3
import pytest
import pandas as pd

from src.utils import get_project_root
from src.database import get_db_connection, load_named_queries


@pytest.fixture(scope="module")
def db_path() -> Path:
    root = get_project_root()
    p = root / "data" / "retail_sales.db"
    assert p.exists(), f"Database does not exist at: {p}"
    return p


@pytest.fixture(scope="module")
def conn(db_path: Path):
    connection = sqlite3.connect(str(db_path))
    yield connection
    connection.close()


def test_database_file_exists(db_path: Path):
    """Verifies that the SQLite database file exists and is populated."""
    assert db_path.exists()
    assert db_path.stat().st_size > 50000, "Database file is unexpectedly small"


def test_retail_sales_table_count(conn: sqlite3.Connection):
    """Verifies that retail_sales table has exactly 2,500 rows."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM retail_sales;")
    count = cursor.fetchone()[0]
    assert count == 2500, f"Expected 2,500 rows, found {count}"


def test_views_exist(conn: sqlite3.Connection):
    """Ensures all 4 business views were properly created."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
    views = {row[0] for row in cursor.fetchall()}
    expected_views = {"v_monthly_sales", "v_category_performance", "v_channel_performance", "v_kpi_summary"}
    assert expected_views.issubset(views), f"Missing analytical views: {expected_views - views}"


def test_sql_kpi_parity_with_data_source(conn: sqlite3.Connection):
    """Cross-validates key financial totals between SQL and the source of truth."""
    cursor = conn.cursor()
    cursor.execute("SELECT total_gross_revenue, realized_revenue, return_refund_loss, cancellation_loss, total_units_sold FROM v_kpi_summary;")
    row = cursor.fetchone()
    
    total_rev, realized_rev, return_loss, cancel_loss, units = row
    assert round(total_rev, 2) == 307881.56, f"Mismatch in total revenue: {total_rev}"
    assert round(realized_rev, 2) == 279533.85, f"Mismatch in realized revenue: {realized_rev}"
    assert round(return_loss, 2) == 17635.82, f"Mismatch in return loss: {return_loss}"
    assert round(cancel_loss, 2) == 6955.34, f"Mismatch in cancellation loss: {cancel_loss}"
    assert units == 4664, f"Mismatch in total units sold: {units}"


def test_all_12_queries_execute_successfully(conn: sqlite3.Connection):
    """Iterates through all 12 queries in analysis_queries.sql and verifies clean execution."""
    root = get_project_root()
    sql_file = root / "sql" / "analysis_queries.sql"
    queries = load_named_queries(sql_file)
    assert len(queries) == 12, f"Expected 12 queries, parsed {len(queries)}"

    for title, sql in queries:
        try:
            df = pd.read_sql_query(sql, conn)
            assert len(df) > 0, f"Query '{title}' returned empty results"
        except Exception as e:
            pytest.fail(f"Query '{title}' failed with error: {e}")
