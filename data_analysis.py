import mysql.connector
import pandas as pd

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="retail_sales"
)

query = "SELECT * FROM retail_sales"

df = pd.read_sql(query, connection)

print(df)
print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nData Types:")
print(df.dtypes)

print("\nBasic Statistics:")
print(df.describe())

# Calculate total sales
df["total_sales"] = df["quantity"] * df["price"]

print("\nSales Data with Total Sales:")
print(df)

# Calculate overall total sales
total_sales = df["total_sales"].sum()

print("\nOverall Total Sales:")
print(total_sales)

# Product-wise sales
product_sales = df.groupby("product_name")["total_sales"].sum()

print("\nProduct-wise Sales:")
print(product_sales)

# Category-wise sales
category_sales = df.groupby("category")["total_sales"].sum()

print("\nCategory-wise Sales:")
print(category_sales)

# Region-wise sales
region_sales = df.groupby("region")["total_sales"].sum()

print("\nRegion-wise Sales:")
print(region_sales)

# Monthly sales
df["sale_date"] = pd.to_datetime(df["sale_date"])

monthly_sales = df.groupby(df["sale_date"].dt.month)["total_sales"].sum()

print("\nMonthly Sales:")
print(monthly_sales)

import matplotlib.pyplot as plt

# Product-wise Sales Chart
product_sales.plot(kind="bar")

plt.title("Product-wise Sales")
plt.xlabel("Product")
plt.ylabel("Total Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Category-wise Sales

category_sales = df.groupby("category")["total_sales"].sum()

print("\nCategory-wise Sales:")
print(category_sales)

plt.figure(figsize=(8, 5))
category_sales.plot(kind="bar")
plt.title("Category-wise Sales")
plt.xlabel("Category")
plt.ylabel("Total Sales")
plt.xticks(rotation=0)
plt.show()

# Region-wise Sales

region_sales = df.groupby("region")["total_sales"].sum()

print("\nRegion-wise Sales:")
print(region_sales)

plt.figure(figsize=(8, 5))
region_sales.plot(kind="bar")
plt.title("Region-wise Sales")
plt.xlabel("Region")
plt.ylabel("Total Sales")
plt.xticks(rotation=45)
plt.show()

# Monthly Sales

df["sale_date"] = pd.to_datetime(df["sale_date"])

monthly_sales = df.groupby(
    df["sale_date"].dt.month
)["total_sales"].sum()

print("\nMonthly Sales:")
print(monthly_sales)

plt.figure(figsize=(8, 5))
monthly_sales.plot(kind="bar")

plt.title("Monthly Sales")
plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.xticks(rotation=0)

plt.show()