/*
============================================================
Sales Data Analysis - SQL Queries
============================================================

IMPORTANT BEGINNER NOTE
-----------------------
SQL (Structured Query Language) is normally used with data
stored inside a DATABASE, not directly with a CSV file.

Common databases include:
- PostgreSQL
- MySQL
- SQL Server
- SQLite

In this project, our data currently lives in:
  data/sales.csv

For these practice queries, we ASSUME the CSV has already
been loaded into a SQL table named:

  sales

Assumed columns in the sales table:
  OrderID
  OrderDate
  CustomerName
  Product
  Category
  Region
  Quantity
  UnitPrice
  Sales

These queries are written for learning.
They do not invent results. You will see real results only
after you load the data into a database and run the queries.

Optional later step (PostgreSQL example idea):
  1. Create a database
  2. Create a table named sales
  3. Import data/sales.csv into that table
  4. Run the queries below

This Step 7 file is for SQL practice only.
============================================================
*/


/* =========================================================
   QUERY 1 - VIEW SAMPLE DATA
   Purpose: Look at the first 10 rows so we understand the table.

   SELECT = choose which columns to return
            (* means "all columns")
   FROM   = choose which table to read from
   LIMIT  = stop after a certain number of rows
   ========================================================= */
SELECT *
FROM sales
LIMIT 10;


/* =========================================================
   QUERY 2 - TOTAL REVENUE
   Purpose: Add up every Sales value to get total revenue.

   SUM(Sales) = add all numbers in the Sales column
   ========================================================= */
SELECT SUM(Sales) AS total_revenue
FROM sales;


/* =========================================================
   QUERY 3 - NUMBER OF ORDERS
   Purpose: Count how many unique orders exist.

   COUNT(DISTINCT OrderID) means:
   - look at OrderID values
   - ignore duplicates
   - count each unique OrderID only once

   Why DISTINCT is useful:
   If the same OrderID appeared more than once, a plain COUNT(*)
   could over-count orders. DISTINCT protects against that.
   ========================================================= */
SELECT COUNT(DISTINCT OrderID) AS number_of_orders
FROM sales;


/* =========================================================
   QUERY 4 - TOTAL UNITS SOLD
   Purpose: Add all Quantity values to get total units sold.
   ========================================================= */
SELECT SUM(Quantity) AS total_units_sold
FROM sales;


/* =========================================================
   QUERY 5 - AVERAGE ORDER VALUE
   Purpose: Estimate average revenue per order.

   Simple approach:
   Total Revenue / Number of Unique Orders

   This is:
   SUM(Sales) / COUNT(DISTINCT OrderID)
   ========================================================= */
SELECT
    SUM(Sales) / COUNT(DISTINCT OrderID) AS average_order_value
FROM sales;


/* =========================================================
   QUERY 6 - SALES BY PRODUCT
   Purpose: Find total revenue for each product.

   GROUP BY Product:
   - put all rows with the same Product into one group
   - then calculate SUM(Sales) for each group

   ORDER BY total_sales DESC:
   - sort so the highest sales appear first
   - DESC means descending (high to low)
   ========================================================= */
SELECT
    Product,
    SUM(Sales) AS total_sales
FROM sales
GROUP BY Product
ORDER BY total_sales DESC;


/* =========================================================
   QUERY 7 - SALES BY CATEGORY
   Purpose: Find total revenue for each category.
   Sorted from highest to lowest.
   ========================================================= */
SELECT
    Category,
    SUM(Sales) AS total_sales
FROM sales
GROUP BY Category
ORDER BY total_sales DESC;


/* =========================================================
   QUERY 8 - SALES BY REGION
   Purpose: Find total revenue for each region.
   Sorted from highest to lowest.
   ========================================================= */
SELECT
    Region,
    SUM(Sales) AS total_sales
FROM sales
GROUP BY Region
ORDER BY total_sales DESC;


/* =========================================================
   QUERY 9 - TOP 10 PRODUCTS
   Purpose: Show only the 10 products with the highest revenue.

   Parts of this query:
   - GROUP BY Product     -> one row per product
   - SUM(Sales)           -> total revenue for that product
   - ORDER BY ... DESC    -> highest revenue first
   - LIMIT 10             -> keep only the top 10 rows
   ========================================================= */
SELECT
    Product,
    SUM(Sales) AS total_sales
FROM sales
GROUP BY Product
ORDER BY total_sales DESC
LIMIT 10;


/* =========================================================
   QUERY 10 - TOP 10 CUSTOMERS
   Purpose: Show the 10 customers with the highest total revenue.
   ========================================================= */
SELECT
    CustomerName,
    SUM(Sales) AS total_sales
FROM sales
GROUP BY CustomerName
ORDER BY total_sales DESC
LIMIT 10;


/* =========================================================
   QUERY 11 - PRODUCTS BY UNITS SOLD
   Purpose: Rank products by how many units were sold
   (Quantity), not by revenue (Sales).
   ========================================================= */
SELECT
    Product,
    SUM(Quantity) AS total_units_sold
FROM sales
GROUP BY Product
ORDER BY total_units_sold DESC;


/* =========================================================
   QUERY 12 - MONTHLY SALES (PostgreSQL)
   Purpose: Total sales for each month, in calendar order.

   DATE_TRUNC('month', OrderDate):
   - takes a date/time value
   - "cuts it down" to the start of that month
   - example idea: 2024-03-15 becomes 2024-03-01

   This helps group all days from the same month together.

   ORDER BY month_start ASC keeps months chronological
   (January, February, March, ...), not alphabetical.
   ========================================================= */
SELECT
    DATE_TRUNC('month', OrderDate) AS month_start,
    SUM(Sales) AS total_sales
FROM sales
GROUP BY DATE_TRUNC('month', OrderDate)
ORDER BY month_start ASC;


/* =========================================================
   QUERY 13 - CATEGORY REVENUE PERCENTAGE
   Purpose: What percent of total revenue comes from each category?

   We use a WINDOW FUNCTION:
     SUM(Sales) OVER ()

   Beginner meaning of this window function:
   - SUM(Sales) alone with GROUP BY gives category totals
   - SUM(Sales) OVER () calculates the grand total across
     all rows/groups without collapsing the result into one row
   - So each category row can still show:
       category sales / overall sales * 100

   Formula:
   category_sales / total_sales_all_categories * 100
   ========================================================= */
SELECT
    Category,
    SUM(Sales) AS category_sales,
    ROUND(
        100.0 * SUM(Sales) / SUM(SUM(Sales)) OVER (),
        2
    ) AS revenue_percentage
FROM sales
GROUP BY Category
ORDER BY category_sales DESC;


/* =========================================================
   QUERY 14 - REGION PERFORMANCE
   Purpose: One summary table for each region with several metrics.

   This query combines multiple metrics in one grouped result:
   - Total Orders   = COUNT(DISTINCT OrderID)
   - Total Units    = SUM(Quantity)
   - Total Revenue  = SUM(Sales)
   - Average Order Value = Total Revenue / Total Orders

   GROUP BY Region means we calculate those metrics separately
   for East, West, North, and South.
   ========================================================= */
SELECT
    Region,
    COUNT(DISTINCT OrderID) AS total_orders,
    SUM(Quantity) AS total_units,
    SUM(Sales) AS total_revenue,
    SUM(Sales) / COUNT(DISTINCT OrderID) AS average_order_value
FROM sales
GROUP BY Region
ORDER BY total_revenue DESC;


/* =========================================================
   QUERY 15 - HIGH-VALUE ORDERS
   Purpose: Find orders where Sales is greater than the
   average Sales value across all orders.

   What is a SUBQUERY?
   A subquery is a query nested inside another query.

   In this example:
   1. The inner query calculates AVG(Sales)
   2. The outer query compares each row's Sales to that average
   3. Only rows above the average are returned
   ========================================================= */
SELECT
    OrderID,
    OrderDate,
    CustomerName,
    Product,
    Category,
    Region,
    Quantity,
    UnitPrice,
    Sales
FROM sales
WHERE Sales > (
    SELECT AVG(Sales)
    FROM sales
)
ORDER BY Sales DESC;


/*
============================================================
SQL CONCEPTS (BEGINNER GLOSSARY)
============================================================

1. SELECT
   Chooses which columns (or calculations) to return.

2. FROM
   Chooses which table the data comes from.

3. WHERE
   Filters rows. Only rows that match the condition are kept.
   Example idea: WHERE Region = 'East'

4. GROUP BY
   Groups rows that share the same value (for example, same Product),
   so you can calculate totals per group.

5. ORDER BY
   Sorts the final result.
   ASC  = ascending (low to high / A to Z)
   DESC = descending (high to low / Z to A)

6. LIMIT
   Restricts how many rows are returned.
   Example: LIMIT 10 returns only 10 rows.

7. COUNT
   Counts rows (or non-null values in a column).

8. COUNT(DISTINCT ...)
   Counts unique values only.
   Useful for counting unique OrderIDs.

9. SUM
   Adds numeric values together.
   Example: SUM(Sales) = total revenue.

10. AVG
    Calculates the average (mean) of numeric values.
    Example: AVG(Sales)

11. DISTINCT
    Removes duplicate values from consideration.
    Often used with COUNT to avoid double-counting.

12. Subquery
    A query written inside another query.
    Often used to calculate a value first (like an average),
    then use that value in a filter or comparison.

13. DATE_TRUNC
    A PostgreSQL function that shortens a timestamp/date
    to a chosen level such as month.
    Helpful for monthly reports.

14. Window function
    A calculation that can look across related rows while
    still keeping detailed result rows.
    Example used above:
      SUM(Sales) OVER ()
    which gives the overall total while still listing each category.

============================================================
END OF FILE
============================================================
*/
