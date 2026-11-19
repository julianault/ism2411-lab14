# 1. Filling missing values feels the most ambiguous because using the mean could change the accuracy of the data. I would want to know why the values are missing and whether the average is a reasonable replacement.
# 2. Some comments explain what I did, but they could explain why better. I would make sure each comment explains the reason for dropping, filling, or changing values so someone else can understand my decisions.
# 3. The most surprising thing I noticed was that some revenue values were negative. I learned that these could represent customer returns rather than errors, so they should be kept in the dataset.


# Exercise 1
import pandas as pd
df = pd.read_csv("data/messy_sales.csv")
df.info()
print(df.isnull().sum())
# 1. The customer_name column contains missing values.
# 2. The sales column is stored as an object instead of a numeric data type.
# 3. The order_date column contains inconsistent date formatting.

# Exercise 2
df.columns = df.columns.str.lower().str.replace(" ", "_")
print(df.columns.tolist())


# Exercise 3
print(df.shape)

df = df.dropna(subset=["order_id", "order_date"])

df["unit_price"] = df["unit_price"].fillna(df["unit_price"].mean())
df["quantity_sold"] = df["quantity_sold"].fillna(df["quantity_sold"].mean())

print(df.shape)
print(df.isnull().sum())


# Exercise 4
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
print(df["order_date"].isna().sum())

df["unit_price"] = df["unit_price"].str.replace("$", "", regex=False).str.replace(",", "", regex=False).astype(float)

df["quantity_sold"] = df["quantity_sold"].astype(int)

df["revenue"] = (df["unit_price"] * df["quantity_sold"]).round(2)

print(df.dtypes)

# Exercise 5
print(df.duplicated().sum())
df = df.drop_duplicates()
print(df.shape)


# Exercise 6
print(df.describe())

# Negative revenue may represent customer returns.
# A very high maximum revenue may represent a bulk order.
# The mean and median may differ because of unusually large orders.

# Remove rows where quantity_sold is 9,999 because this is a placeholder, not a real order.
df = df[df["quantity_sold"] != 9999]

print(df.shape)


# Exercise 7
df.to_csv("data/clean_sales.csv", index=False)

df_check = pd.read_csv("data/clean_sales.csv")
df_check.info()

df_check = pd.read_csv("data/clean_sales.csv", parse_dates=["order_date"])
df_check.info()