import mysql.connector
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="retail_sales"
)

print("Database connected successfully!")

query = "SELECT * FROM retail_sales"

df = pd.read_sql(query, connection)

print("\nSales data loaded successfully!")
print(df)


# Calculate total sales
df["total_sales"] = df["quantity"] * df["price"]

print("\nSales data with Total Sales:")
print(df)


# Convert sale_date to datetime
df["sale_date"] = pd.to_datetime(df["sale_date"])

# Create month and day features
df["month"] = df["sale_date"].dt.month
df["day"] = df["sale_date"].dt.day

# Input features
X = df[["month", "day", "quantity", "price"]]

# Target
y = df["total_sales"]

print("\nInput features (X):")
print(X)

print("\nTarget (y):")
print(y)


# Convert sale_date to datetime
df["sale_date"] = pd.to_datetime(df["sale_date"])

# Create month and day features
df["month"] = df["sale_date"].dt.month
df["day"] = df["sale_date"].dt.day

# Input features
X = df[["month", "day", "quantity", "price"]]

# Target
y = df["total_sales"]

print("\nInput features (X):")
print(X)

print("\nTarget (y):")
print(y)

# Create Random Forest model
from sklearn.model_selection import train_test_split

# Split data into training and testing
x_train, x_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Data split successfully!")

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# Train the model
model.fit(x_train, y_train)

print("\nRandom Forest model trained successfully!")

# Make predictions on test data

y_pred = model.predict(x_test)

print("\nPredicted Sales:")
print(y_pred)

from sklearn.metrics import mean_absolute_error, r2_score

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel Evaluation:")
print("Mean Absolute Error:", mae)
print("R2 Score:", r2)

import matplotlib.pyplot as plt

# Actual vs Predicted Sales

plt.figure(figsize=(8, 5))

plt.plot(y_test.values, label="Actual Sales", marker="o")
plt.plot(y_pred, label="Predicted Sales", marker="x")

plt.title("Actual vs Predicted Sales")
plt.xlabel("Test Data")
plt.ylabel("Total Sales")
plt.legend()

plt.show()

# Predict sales for a new product

new_data = [[
    2,      # product/category encoded value
    1,      # region encoded value
    50000   # example value
]]

predicted_sales = model.predict(new_data)

print("\nPredicted Sales for New Data:")
print(predicted_sales[0])