"""
Retail Sales Analytics - Database Integration & Query Engine
Manages SQLite database initialization, CSV ingestion, and automated execution of business SQL queries.
"""

from pathlib import Path
import sqlite3
import sys
import pandas as pd

try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.utils import get_project_root, setup_logger, print_section

logger = setup_logger("database")


def get_db_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled."""
    if db_path is None:
        db_path = get_project_root() / "data" / "retail_sales.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database(db_path: Path, schema_path: Path) -> None:
    """Initializes the database schema using DDL script."""
    logger.info(f"Initializing database at: {db_path} using schema: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db_connection(db_path) as conn:
        conn.executescript(schema_sql)
    logger.info("Database schema initialized successfully.")


def import_cleaned_csv(db_path: Path, csv_path: Path) -> int:
    """Imports cleaned CSV dataset into SQLite retail_sales table."""
    logger.info(f"Importing cleaned data from: {csv_path}")
    if not csv_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)
    
    with get_db_connection(db_path) as conn:
        # Clear existing records
        conn.execute("DELETE FROM retail_sales;")
        df.to_sql("retail_sales", conn, if_exists="append", index=False)
        cursor = conn.execute("SELECT COUNT(*) FROM retail_sales;")
        inserted_rows = cursor.fetchone()[0]

    logger.info(f"Successfully imported {inserted_rows} rows into 'retail_sales' table.")
    return inserted_rows


def load_named_queries(sql_file_path: Path) -> list[tuple[str, str]]:
    """Parses SQL queries with their titles from the analysis_queries.sql file."""
    import re
    with open(sql_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"--\s*(QUERY\s*\d+:[^\n]+)(.*?)(?=(?:--\s*QUERY\s*\d+:)|$)", re.DOTALL)
    matches = pattern.findall(content)
    named_queries = []

    for title, body in matches:
        sql_lines = [line for line in body.split("\n") if not line.strip().startswith("--")]
        sql_clean = "\n".join(sql_lines).strip()
        if sql_clean:
            named_queries.append((title.strip(), sql_clean))

    return named_queries


def execute_and_display_queries(db_path: Path, sql_file_path: Path) -> dict[str, pd.DataFrame]:
    """Executes all business queries and outputs formatted tables."""
    queries = load_named_queries(sql_file_path)
    results = {}

    print_section("Executing SQL Business Analysis Suite")
    with get_db_connection(db_path) as conn:
        for idx, (title, sql) in enumerate(queries, 1):
            df_result = pd.read_sql_query(sql, conn)
            results[title] = df_result
            
            print(f"\n[QUERY {idx}]: {title}")
            print("-" * 70)
            # Display up to 10 rows for clean console presentation
            print(df_result.head(10).to_string(index=False))
            if len(df_result) > 10:
                print(f"... ({len(df_result) - 10} more rows)")
            print("-" * 70)

    return results


def main():
    root = get_project_root()
    db_path = root / "data" / "retail_sales.db"
    schema_path = root / "sql" / "schema.sql"
    cleaned_csv_path = root / "data" / "processed" / "retail_sales_cleaned.csv"
    queries_path = root / "sql" / "analysis_queries.sql"

    # 1. Initialize DB
    init_database(db_path, schema_path)

    # 2. Import CSV
    inserted_rows = import_cleaned_csv(db_path, cleaned_csv_path)

    # 3. Execute Queries
    results = execute_and_display_queries(db_path, queries_path)

    print_section("Database Ingestion & Query Execution Complete")
    print(f"Total Queries Executed: {len(results)}")
    print(f"Database File:          {db_path}")
    print(f"Total Rows Ingested:    {inserted_rows}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
