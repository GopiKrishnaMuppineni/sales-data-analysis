"""
generate_sales_data.py
----------------------
Purpose:
    Create a beginner-friendly, SYNTHETIC sales dataset as a CSV file.

Why this file exists:
    Real company data is private. For learning and portfolio work, we generate
    fake-but-realistic sales rows so we can practice cleaning, analysis, SQL,
    and charts without using anyone's private information.

How to run (from the sales-data-analysis folder):
    ..\\venv\\Scripts\\python.exe src\\generate_sales_data.py

Output:
    data/sales.csv  (~2,000 rows)
"""

from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd

# ---------------------------------------------------------------------------
# 1. Paths
# ---------------------------------------------------------------------------
# Path(__file__) = this script's location (src/generate_sales_data.py)
# .parent        = the src folder
# .parent.parent = the project root (sales-data-analysis/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_ROOT / "data"
OUTPUT_FILE = DATA_FOLDER / "sales.csv"

# ---------------------------------------------------------------------------
# 2. Settings for the synthetic dataset
# ---------------------------------------------------------------------------
NUM_ROWS = 2000
RANDOM_SEED = 42  # same seed => same "random" data every time (reproducible)

# Realistic product catalog: product name, category, and typical unit price
PRODUCTS = [
    ("Laptop", "Electronics", 899.99),
    ("Monitor", "Electronics", 249.99),
    ("Keyboard", "Accessories", 49.99),
    ("Mouse", "Accessories", 24.99),
    ("Headphones", "Accessories", 79.99),
    ("Desk", "Furniture", 199.99),
    ("Chair", "Furniture", 149.99),
    ("Printer", "Office Supplies", 129.99),
    ("Notebook Pack", "Office Supplies", 12.99),
    ("Desk Lamp", "Office Supplies", 34.99),
]

REGIONS = ["East", "West", "North", "South"]

# Simple list of fake customer names (clearly not real people)
CUSTOMERS = [
    "Alex Rivera",
    "Jordan Lee",
    "Sam Patel",
    "Taylor Brooks",
    "Casey Nguyen",
    "Morgan Ellis",
    "Riley Quinn",
    "Avery Chen",
    "Jamie Torres",
    "Cameron Blake",
    "Drew Santos",
    "Parker Kim",
    "Reese Morgan",
    "Quinn Harper",
    "Skyler Adams",
    "Hayden Cole",
    "Emerson Walsh",
    "Finley Grant",
    "Rowan Pierce",
    "Blake Foster",
]


def random_date_within_year(start_date: datetime, rng: random.Random) -> datetime:
    """
    Pick a random calendar day within about one year from start_date.

    Why: sales analysis often looks at trends over months, so we need dates
    spread across a full year instead of all on the same day.
    """
    day_offset = rng.randint(0, 364)  # 0 to 364 days = about one year
    return start_date + timedelta(days=day_offset)


def generate_sales_rows(num_rows: int, seed: int) -> list[dict]:
    """
    Build a list of dictionaries. Each dictionary = one sales order row.

    Sales is calculated as: Quantity * UnitPrice
    """
    rng = random.Random(seed)
    start_date = datetime(2024, 1, 1)

    rows = []
    for i in range(1, num_rows + 1):
        product_name, category, base_price = rng.choice(PRODUCTS)

        # Slight price variation so the data feels more realistic
        # Example: a $50 keyboard might be sold at $47.50 to $52.50
        price_noise = rng.uniform(-0.05, 0.05)  # -5% to +5%
        unit_price = round(base_price * (1 + price_noise), 2)

        quantity = rng.randint(1, 5)
        sales = round(quantity * unit_price, 2)

        row = {
            "OrderID": f"ORD-{10000 + i}",
            "OrderDate": random_date_within_year(start_date, rng).strftime("%Y-%m-%d"),
            "CustomerName": rng.choice(CUSTOMERS),
            "Product": product_name,
            "Category": category,
            "Region": rng.choice(REGIONS),
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "Sales": sales,
        }
        rows.append(row)

    return rows


def main() -> None:
    """
    Main steps:
      1. Make sure the data/ folder exists
      2. Generate ~2,000 synthetic sales rows
      3. Save them as a CSV file
      4. Print a short summary so you can confirm it worked
    """
    print("Creating synthetic sales dataset...")
    print(f"Target file: {OUTPUT_FILE}")

    # Ensure the data folder exists before we try to save a file there
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    rows = generate_sales_rows(NUM_ROWS, RANDOM_SEED)

    # A DataFrame is Pandas' table (rows + columns), like a spreadsheet in Python
    df = pd.DataFrame(rows)

    # index=False means: do not write the Pandas row numbers as an extra column
    df.to_csv(OUTPUT_FILE, index=False)

    print("Done!")
    print(f"Rows created: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 5 rows preview:")
    print(df.head())
    print("\nNote: This data is SYNTHETIC (made-up for learning).")
    print("It does not come from a real company.")


if __name__ == "__main__":
    # This runs only when you execute this file directly with Python
    main()
