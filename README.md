# Sales Data Analysis & Beginner ETL Pipeline

A beginner-friendly portfolio project that analyzes **synthetic sales transaction data** and demonstrates a simple end-to-end workflow: data generation, cleaning, exploratory analysis, business insights, visualization, SQL practice, and a basic ETL pipeline into SQLite.

This project is intended for learners preparing for roles such as:

- Data Analyst
- Junior Data Engineer
- Entry-Level AI/ML Engineer

The dataset is **synthetic** and was generated for learning and portfolio purposes. It does not come from a real company.

---

## 1. Project Overview

This project walks through a realistic beginner analytics and data engineering workflow using Python and SQL.

It demonstrates:

- Synthetic sales data generation
- Data cleaning and validation
- Exploratory data analysis (EDA)
- Business analysis with Pandas
- Data visualization with Matplotlib
- SQL analysis practice
- A simple ETL pipeline
- Loading cleaned data into a SQLite database

The focus is on clear, readable, beginner-friendly work rather than advanced production systems.

---

## 2. Business Objective

The goal is to analyze sales transactions to understand:

- Overall revenue performance
- Product and category contribution
- Regional performance
- Customer concentration
- Monthly sales trends

The project also shows how raw CSV data can be cleaned, transformed, and loaded into a database for SQL-based analysis.

---

## 3. Project Workflow

```text
CSV Dataset
    ↓
Python / Pandas
    ↓
Data Cleaning
    ↓
Business Analysis
    ↓
Visualization
    ↓
SQLite ETL Pipeline
    ↓
SQL Analysis
```

**Stage summary**

| Stage | What happens |
|---|---|
| CSV Dataset | Synthetic sales records are stored in `data/sales.csv` |
| Python / Pandas | Data is loaded into a DataFrame for analysis |
| Data Cleaning | Missing values, duplicates, types, and invalid values are checked |
| Business Analysis | Revenue, products, regions, customers, and trends are calculated |
| Visualization | Charts are created to communicate findings |
| SQLite ETL Pipeline | Cleaned data is loaded into `data/sales.db` |
| SQL Analysis | Practice queries analyze the `sales` table |

---

## 4. Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- SQL
- SQLite
- Jupyter Notebook
- Git / GitHub

---

## 5. Dataset

The dataset contains approximately **2,000 synthetic sales records**.

| Column | Description |
|---|---|
| `OrderID` | Unique order identifier |
| `OrderDate` | Date the order was placed |
| `CustomerName` | Name of the customer |
| `Product` | Product purchased |
| `Category` | Product category (for example, Electronics or Furniture) |
| `Region` | Sales region (East, West, North, South) |
| `Quantity` | Number of units sold in the order |
| `UnitPrice` | Price per unit |
| `Sales` | Revenue for the row (`Quantity * UnitPrice`) |

---

## 6. Data Cleaning

Before trusting the analysis, the project checks data quality, including:

- Missing values
- Duplicate rows
- Data types
- Invalid quantities
- Invalid prices
- Invalid sales values
- Sales calculation validation (`Sales` vs `Quantity * UnitPrice`)
- Date range validation

The original source file `data/sales.csv` is preserved. Cleaning and preparation are performed in the notebook and ETL script rather than overwriting the raw CSV.

---

## 7. Business Analysis

The analysis answers practical sales questions such as:

- What is total revenue?
- How many orders were placed?
- How many units were sold?
- What is the average order value?
- Which products generate the most revenue?
- Which categories generate the most revenue?
- Which regions generate the most revenue?
- What are monthly sales trends?
- Which customers generate the most revenue?
- Which products sell the most units?
- What percentage of revenue comes from each category?

Detailed calculations live in:

`notebooks/sales_analysis.ipynb`

---

## 8. Visualizations

The project includes six Matplotlib charts saved in `output/charts/`:

1. Monthly Sales Trend
2. Sales by Category
3. Sales by Region
4. Top 10 Products by Revenue
5. Top 10 Customers by Revenue
6. Units Sold by Category

![Monthly Sales](output/charts/monthly_sales.png)

![Sales by Category](output/charts/sales_by_category.png)

![Sales by Region](output/charts/sales_by_region.png)

![Top Products](output/charts/top_products.png)

![Top Customers](output/charts/top_customers.png)

![Units by Category](output/charts/units_by_category.png)

---

## 9. SQL Analysis

The file:

`sql/sales_queries.sql`

contains **15 beginner-friendly SQL queries** written against a table named `sales`.

Concepts practiced include:

- `SELECT`
- `WHERE`
- `GROUP BY`
- `ORDER BY`
- `LIMIT`
- `SUM`
- `AVG`
- `COUNT`
- `COUNT(DISTINCT ...)`
- Subqueries
- `DATE_TRUNC` (PostgreSQL-style monthly grouping)
- Window functions

These queries represent analysis that can be run once sales data is available in a database table.

---

## 10. ETL Pipeline

A simple ETL pipeline is implemented in:

`src/load_to_sqlite.py`

**Extract**

- Read `data/sales.csv` into a Pandas DataFrame

**Transform**

- Convert dates
- Validate numeric fields
- Check duplicates
- Validate/recalculate sales when needed
- Remove only clearly invalid rows when necessary

**Load**

- Write the cleaned DataFrame into a SQLite table named `sales`

This is intentionally a beginner ETL example (CSV → Python → SQLite), not a production orchestration platform.

---

## 11. Database

`data/sales.db` is a SQLite database file containing a `sales` table.

SQLite was chosen because:

- It is beginner-friendly
- It stores the database as a single local file
- It does not require installing or managing a separate database server

---

## 12. Project Structure

```text
sales-data-analysis/
│
├── data/
│   ├── sales.csv
│   └── sales.db
│
├── notebooks/
│   └── sales_analysis.ipynb
│
├── src/
│   ├── generate_sales_data.py
│   └── load_to_sqlite.py
│
├── sql/
│   └── sales_queries.sql
│
├── output/
│   └── charts/
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 13. How to Run the Project

These instructions use **Windows PowerShell**.

### 1) Clone the repository

```powershell
git clone <your-repo-url>
cd sales-data-analysis
```

`git clone` downloads the project. `cd` moves you into the project folder.

### 2) Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

A virtual environment keeps this project's packages separate from other Python projects.

### 3) Install requirements

```powershell
pip install -r requirements.txt
```

This installs Pandas, NumPy, Matplotlib, Jupyter, and openpyxl.

### 4) Generate the dataset (only if needed)

```powershell
python src/generate_sales_data.py
```

Use this if `data/sales.csv` is missing. If the CSV already exists, you can skip this step.

### 5) Run the ETL script

```powershell
python src/load_to_sqlite.py
```

### 6) Open the Jupyter notebook

```powershell
jupyter notebook notebooks/sales_analysis.ipynb
```

Then run the notebook cells from top to bottom.

---

## 14. Run ETL

```powershell
python src/load_to_sqlite.py
```

This command:

1. Extracts data from `data/sales.csv`
2. Transforms and validates the data
3. Loads it into `data/sales.db` as the `sales` table
4. Prints verification queries (row count, sample rows, sales by category)

---

## 15. Future Improvements

Possible next steps (not implemented yet):

- Move from SQLite to PostgreSQL
- Build a Power BI dashboard
- Schedule the ETL job automatically
- Add automated data quality tests
- Expand to a larger dataset
- Store raw/processed files in cloud storage
- Load into a cloud data warehouse
- Add a basic machine learning sales prediction model

---

## 16. Learning Outcomes

This project provides hands-on practice with:

- Python
- Pandas
- SQL
- Data cleaning
- Exploratory data analysis
- Visualization
- ETL fundamentals
- SQLite
- Basic data engineering concepts (extract, transform, load)

---

## Resume Project Description

- Built a beginner sales analytics project in Python using Pandas to clean synthetic transaction data and answer business questions on revenue, products, regions, customers, and monthly trends.
- Created 15 SQL practice queries covering aggregation, grouping, filtering, subqueries, and window-function concepts for sales performance analysis.
- Designed a simple ETL pipeline that extracts CSV data, validates and transforms it with Pandas, and loads it into a SQLite `sales` table for database querying.
