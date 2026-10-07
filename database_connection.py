import mysql.connector
import pandas as pd

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

connection.close()