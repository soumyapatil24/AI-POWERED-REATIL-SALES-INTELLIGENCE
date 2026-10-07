import mysql.connector
import pandas as pd

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="retail_sales"
)

# Load sales data
query = "SELECT * FROM retail_sales"
df = pd.read_sql(query, connection)

# Calculate total sales
df["total_sales"] = df["quantity"] * df["price"]

print("Sales data loaded successfully!")
print(df)


# Prepare data for Machine Learning

df["sale_date"] = pd.to_datetime(df["sale_date"])

# Create a numeric date feature
df["day_number"] = (df["sale_date"] - df["sale_date"].min()).dt.days

# Select input and output
X = df[["day_number"]]
y = df["total_sales"]

print("\nInput (X):")
print(X)

print("\nOutput (y):")
print(y)


from sklearn.model_selection import train_test_split

# Split data into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining data:")
print(X_train)

print("\nTesting data:")
print(X_test)


from sklearn.linear_model import LinearRegression

# Create the Linear Regression model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

print("\nLinear Regression model trained successfully!")


from sklearn.metrics import mean_absolute_error, r2_score

# Make predictions on test data
y_pred = model.predict(X_test)

print("\nActual Sales:")
print(y_test)

print("\nPredicted Sales:")
print(y_pred)

# Calculate model performance
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nMean Absolute Error (MAE):")
print(mae)

print("\nR² Score:")
print(r2)