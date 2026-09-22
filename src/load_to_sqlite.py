"""
load_to_sqlite.py
-----------------
Beginner-friendly ETL pipeline:

    CSV  ->  Python (Pandas)  ->  Clean/Transform  ->  SQLite database

ETL means:
    E = Extract   (read the data)
    T = Transform (clean / prepare the data)
    L = Load      (save the data into a database)

This script:
    1. Reads data/sales.csv
    2. Cleans and validates the data
    3. Creates data/sales.db with a table named sales
    4. Verifies the load with simple SQL queries

How to run (from the sales-data-analysis folder):
    ..\\venv\\Scripts\\python.exe src\\load_to_sqlite.py
    or, if your virtual environment is already activated:
    python src/load_to_sqlite.py
"""

from pathlib import Path
import sqlite3
import sys

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# This script lives in:  sales-data-analysis/src/
# Project root is one folder up from src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "sales.csv"
DB_PATH = PROJECT_ROOT / "data" / "sales.db"
TABLE_NAME = "sales"


def extract_data(csv_path: Path) -> pd.DataFrame:
    """
    EXTRACT step
    ------------
    Read the CSV file into a Pandas DataFrame.

    A DataFrame is like a spreadsheet table inside Python.
    """
    print("Loading sales data...")

    # Simple error handling: stop clearly if the CSV is missing
    if not csv_path.exists():
        print(f"ERROR: CSV file not found at: {csv_path}")
        print("Make sure data/sales.csv exists before running this script.")
        sys.exit(1)

    try:
        df = pd.read_csv(csv_path)
    except Exception as error:
        print(f"ERROR: Could not read the CSV file. Details: {error}")
        sys.exit(1)

    print(f"Rows extracted: {len(df)}")
    print(f"Column names: {list(df.columns)}")
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    TRANSFORM step
    --------------
    Clean and prepare the data before loading it into SQLite.

    Why transform before loading?
    - databases work better with correct data types
    - duplicates can inflate totals
    - invalid numbers can break reports
    - cleaning once here helps every later SQL query
    """
    # Work on a copy so we do not accidentally change the original extract
    clean_df = df.copy()

    # 1) Convert OrderDate from text to real dates
    clean_df["OrderDate"] = pd.to_datetime(clean_df["OrderDate"], errors="coerce")

    # 2) Remove exact duplicate rows (only if any exist)
    duplicate_count = clean_df.duplicated().sum()
    if duplicate_count > 0:
        print(f"Found {duplicate_count} duplicate rows. Removing exact duplicates...")
        clean_df = clean_df.drop_duplicates()
    else:
        print("No exact duplicate rows found.")

    # 3) Make sure numeric columns are numeric
    # errors="coerce" turns bad values into NaN (missing) instead of crashing
    clean_df["Quantity"] = pd.to_numeric(clean_df["Quantity"], errors="coerce")
    clean_df["UnitPrice"] = pd.to_numeric(clean_df["UnitPrice"], errors="coerce")
    clean_df["Sales"] = pd.to_numeric(clean_df["Sales"], errors="coerce")

    # 4) Recalculate Sales from Quantity * UnitPrice when needed
    # If Sales is missing but Quantity and UnitPrice are valid, fill it in.
    missing_sales_mask = clean_df["Sales"].isna()
    can_calculate_mask = (
        missing_sales_mask
        & clean_df["Quantity"].notna()
        & clean_df["UnitPrice"].notna()
    )
    calculated_count = can_calculate_mask.sum()
    if calculated_count > 0:
        print(f"Calculating Sales for {calculated_count} row(s) using Quantity * UnitPrice...")
        clean_df.loc[can_calculate_mask, "Sales"] = (
            clean_df.loc[can_calculate_mask, "Quantity"]
            * clean_df.loc[can_calculate_mask, "UnitPrice"]
        )

    # 5) Identify invalid rows (we only remove them if necessary)
    # Invalid means: missing important values, or non-positive Quantity/UnitPrice/Sales
    invalid_mask = (
        clean_df["OrderDate"].isna()
        | clean_df["Quantity"].isna()
        | clean_df["UnitPrice"].isna()
        | clean_df["Sales"].isna()
        | (clean_df["Quantity"] <= 0)
        | (clean_df["UnitPrice"] <= 0)
        | (clean_df["Sales"] <= 0)
    )
    invalid_count = invalid_mask.sum()

    if invalid_count > 0:
        print(f"Found {invalid_count} invalid row(s). Removing only those invalid rows...")
        print("Invalid rows are rows with missing dates/numbers or non-positive Quantity/UnitPrice/Sales.")
        clean_df = clean_df.loc[~invalid_mask].copy()
    else:
        print("No invalid rows found. No rows were deleted.")

    # Keep a stable column order for the database table
    expected_columns = [
        "OrderID",
        "OrderDate",
        "CustomerName",
        "Product",
        "Category",
        "Region",
        "Quantity",
        "UnitPrice",
        "Sales",
    ]
    clean_df = clean_df[expected_columns]

    print("Data cleaned successfully.")
    print(f"Rows after transform: {len(clean_df)}")
    return clean_df


def load_data(clean_df: pd.DataFrame, db_path: Path, table_name: str) -> None:
    """
    LOAD step
    ---------
    Save the cleaned DataFrame into a SQLite database table.

    What to_sql() does:
    - takes a Pandas DataFrame
    - creates (or replaces) a SQL table
    - inserts the DataFrame rows into that table
    """
    # Make sure the data folder exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # sqlite3.connect opens (or creates) the .db file
        with sqlite3.connect(db_path) as connection:
            # if_exists="replace" means:
            # if the sales table already exists, replace it with fresh data
            clean_df.to_sql(
                name=table_name,
                con=connection,
                if_exists="replace",
                index=False,  # do not save the Pandas row numbers as a column
            )
    except sqlite3.Error as error:
        print(f"ERROR: Database connection/load problem. Details: {error}")
        sys.exit(1)
    except Exception as error:
        print(f"ERROR: Could not load data into SQLite. Details: {error}")
        sys.exit(1)

    print("Data loaded into SQLite.")
    print(f"Database file: {db_path}")


def verify_database(db_path: Path, table_name: str) -> None:
    """
    Verify that the data was loaded correctly by running simple SQL queries.
    """
    try:
        with sqlite3.connect(db_path) as connection:
            # Query 1: count rows
            row_count = pd.read_sql_query(
                f"SELECT COUNT(*) AS row_count FROM {table_name};",
                connection,
            )
            rows_in_db = int(row_count.loc[0, "row_count"])
            print(f"Rows in database: {rows_in_db}")

            # Query 2: preview first 5 rows
            preview = pd.read_sql_query(
                f"SELECT * FROM {table_name} LIMIT 5;",
                connection,
            )
            print("\nFirst 5 rows from SQLite:")
            print(preview)

            # Query 3: sales by category
            category_sales = pd.read_sql_query(
                f"""
                SELECT
                    Category,
                    SUM(Sales) AS TotalSales
                FROM {table_name}
                GROUP BY Category
                ORDER BY TotalSales DESC;
                """,
                connection,
            )
            print("\nSales by Category from SQLite:")
            print(category_sales)

    except sqlite3.Error as error:
        print(f"ERROR: Could not verify the database. Details: {error}")
        sys.exit(1)

    print("\nDatabase verification successful.")


def main() -> None:
    """
    Run the full beginner ETL pipeline:

    EXTRACT   -> CSV to DataFrame
    TRANSFORM -> clean and validate DataFrame
    LOAD      -> DataFrame to SQLite sales table
    VERIFY    -> run simple SQL checks
    """
    # EXTRACT
    df = extract_data(CSV_PATH)

    # TRANSFORM
    clean_df = transform_data(df)

    # LOAD
    load_data(clean_df, DB_PATH, TABLE_NAME)

    # VERIFY
    verify_database(DB_PATH, TABLE_NAME)


if __name__ == "__main__":
    main()
