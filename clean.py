# 1. Dropping missing essential identifiers (like order_id or order_date) is the most ambiguous because throwing away rows discards potentially valuable revenue records. Before making that call on real data, I would want to know if those missing values can be recovered from secondary logs or payment systems.
# 2. Yes, comments should explain the analytical or business rationale rather than just describing the code. For example, instead of writing # Drop rows where order_date is null, a better comment is # Drop rows missing order_date because un-timestamped sales cannot be used for time-series forecasting.
# 3. Discovering unexpected anomalies like negative values (product returns) and extreme outliers (such as a quantity of 9,999) highlights how messy real-world data can be and how quickly it would distort key metrics like total revenue if left unhandled.
import pandas as pd

# Load the dataset
df = pd.read_csv("messy_sales.csv")

# Inspect basic information and missing values
print(df.info())
print(df.isnull().sum())

# --- Data Quality Issues (Comment Block) ---
# 1. Column 'order_date' has missing values and is stored as an object (string) rather than datetime due to mixed date formats or invalid strings (e.g., 'TBD').
# 2. Column 'unit_price' is stored as an object (string) because values contain currency symbols ('$') and commas (e.g., '$1,299.00').
# 3. Column 'quantity_sold' has missing values or formatting inconsistencies causing it to parse incorrectly.


# Convert all column names to lowercase and replace spaces with underscores
df.columns = df.columns.str.lower().str.replace(' ', '_')

# Print the updated column list to confirm
print(df.columns.tolist())
# Expected output: ['order_id', 'order_date', 'product_category', 'region', 'unit_price', 'quantity_sold', 'customer_id']


# Print shape before dropping essential rows
print(f"Shape before dropping essential rows: {df.shape}")

# Drop rows missing essential identifiers (order_id, order_date)
# Reason: Without an order ID or order date, the record cannot be uniquely tracked or reconciled.
df = df.dropna(subset=['order_id', 'order_date'])

# Fill numeric columns with few missing values using the column mean
# Reason: For numerical features with minimal missingness, mean imputation preserves dataset size without heavily distorting the distribution.
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
for col in numeric_cols:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].mean())

# Print shape after dropping essential rows and check missing values
print(f"Shape after dropping essential rows: {df.shape}")
print(df.isnull().sum())

# Convert order_date to datetime, coercing unparseable strings (like 'TBD') to NaT
initial_nat = df['order_date'].isnull().sum()
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
new_nat = df['order_date'].isnull().sum()
print(f"Number of dates that became NaT: {new_nat - initial_nat}")

# Clean and convert unit_price to float (strip '$' and ',')
df['unit_price'] = (
    df['unit_price']
    .astype(str)
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
    .astype(float)
)

# Convert quantity_sold to int
df['quantity_sold'] = df['quantity_sold'].astype(int)

# Add revenue column
df['revenue'] = (df['unit_price'] * df['quantity_sold']).round(2)

# Print dtypes to confirm
print(df.dtypes)


# Count duplicate rows
duplicates_count = df.duplicated().sum()
print(f"Number of duplicate rows: {duplicates_count}")

# Remove duplicates if they exist
if duplicates_count > 0:
    df = df.drop_duplicates()

# Print shape again to confirm
print(f"Shape after removing duplicates: {df.shape}")

# Run describe on the cleaned data
print(df.describe())

# --- Comments & Analytical Thinking ---
# 1. Suspicious Statistic: Negative minimum values in 'revenue' or 'quantity_sold'.
#    Business Explanation: These represent product returns or refunds where money and items flowed back to the customer. We keep them because they reflect real financial transactions.
# 2. Suspicious Statistic: Absurdly high maximum value in 'quantity_sold' (e.g., 9,999).
#    Business Explanation: This is a data entry placeholder or test transaction rather than a genuine customer order, so we drop these rows.

# Drop placeholder rows with quantity_sold == 9999
df = df[df['quantity_sold'] != 9999]
print(f"Shape after removing placeholder rows: {df.shape}")


import os

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Export cleaned data to CSV with index=False
df.to_csv('data/clean_sales.csv', index=False)

# Reload without parse_dates to check dtypes
df_reloaded = pd.read_csv('data/clean_sales.csv')
print("--- Reloaded without parse_dates ---")
print(df_reloaded.info())

# Reload with parse_dates for order_date (use this for Lab 15)
df_parsed = pd.read_csv('data/clean_sales.csv', parse_dates=['order_date'])
print("\n--- Reloaded with parse_dates ---")
print(df_parsed.info())
