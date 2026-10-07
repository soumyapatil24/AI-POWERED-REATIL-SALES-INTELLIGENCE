CREATE DATABASE RETAIL_SALES;
USE RETAIL_SALES;

CREATE TABLE retail_sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_date DATE,
    product_name VARCHAR(100),
    category VARCHAR(100),
    quantity INT,
    price DECIMAL(10,2),
    customer_name VARCHAR(100),
    region VARCHAR(100)
);

USE retail_sales;

CREATE TABLE IF NOT EXISTS inventory (
    product_name VARCHAR(100) PRIMARY KEY,
    stock_quantity INT NOT NULL DEFAULT 100,
    reorder_level INT NOT NULL DEFAULT 20,
    last_restock_date DATE
);

USE retail_sales;

INSERT IGNORE INTO inventory (
    product_name,
    stock_quantity,
    reorder_level,
    last_restock_date
)
SELECT
    product_name,
    100,
    20,
    CURDATE()
FROM retail_sales
GROUP BY product_name
ON DUPLICATE KEY UPDATE
    product_name = VALUES(product_name);
    
    select * from inventory;

INSERT INTO retail_sales 
(sale_id, sale_date, product_name, category, quantity, price, customer_name, region)
VALUES
(1, '2026-01-05', 'Laptop', 'Computers', 2, 55000.00, 'Rahul Sharma', 'Bangalore'),
(2, '2026-01-08', 'Smartphone', 'Mobiles', 3, 25000.00, 'Priya Kumar', 'Mysore'),  
(3, '2026-01-12', 'Headphones', 'Accessories', 5, 2500.00, 'Arjun Rao', 'Bangalore'),
(4, '2026-01-18', 'Smartwatch', 'Wearables', 2, 4500.00, 'Sneha Shetty', 'Mangalore'), 
(5, '2026-01-25', 'Tablet', 'Tablets', 1, 22000.00, 'Vikram Singh', 'Hubli'),
(6, '2026-02-03', 'Laptop', 'Computer', 2, 55000, 'Sneha', 'Bangalore'),
(7, '2026-02-05', 'Smartphone', 'Mobiles', 3, 22000, 'Vikas', 'Belagavi'),
(8, '2026-02-08', 'Mouse', 'Accessories', 5, 800, 'Meena', 'Mysore'),
(9, '2026-02-10', 'Smartwatch', 'Wearables', 2, 4500, 'Ravi', 'Hubli'),
(10, '2026-02-12', 'Tablet', 'Tablets', 3, 22000, 'Pooja', 'Mangalore'),
(11, '2026-02-15', 'Laptop', 'Computer', 1, 60000, 'Arun', 'Bangalore'),
(12, '2026-02-18', 'Smartphone', 'Mobiles', 4, 18000, 'Anita', 'Belagavi'),
(13, '2026-02-20', 'Keyboard', 'Accessories', 6, 1200, 'Kiran', 'Mysore'),
(14, '2026-02-22', 'Fitness Band', 'Wearables', 5, 2500, 'Priya', 'Hubli'),
(15, '2026-02-25', 'Tablet', 'Tablets', 2, 25000, 'Rahul', 'Bangalore'),
(16, '2026-03-02', 'Desktop Computer', 'Computer', 1, 50000, 'Naveen', 'Mangalore'),
(17, '2026-03-05', 'Smartphone', 'Mobiles', 2, 30000, 'Divya', 'Mysore'),
(18, '2026-03-08', 'Headphones', 'Accessories', 4, 1500, 'Suresh', 'Belagavi'),
(19, '2026-03-12', 'Smartwatch', 'Wearables', 3, 5500, 'Kavya', 'Bangalore'),
(20, '2026-03-15', 'Tablet', 'Tablets', 2, 28000, 'Manoj', 'Hubli');



SELECT COUNT(*) AS TOTAL_RECORDS
FROM RETAIL_SALES;

SHOW DATABASES;

SELECT * FROM RETAIL_SALES;

#SQL ANALYSIS:
#FIND TOTAL SALES
SELECT SUM(QUANTITY*PRICE)AS TOTAL_SALES
FROM RETAIL_SALES;

#FIND TOTAL QTY
SELECT SUM(QUANTITY) AS TOTAL_SALES
FROM RETAIL_SALES;

#FIND NUM OF SALES
SELECT COUNT(*) AS TOTAL_SALES
FROM RETAIL_SALES;
 SELECT * FROM RETAIL_SALES;
 
 #FIND BEST SELLING PRODUCT
 SELECT 
    product_name,
    SUM(quantity * price) AS total_sales
FROM retail_sales
GROUP BY product_name
ORDER BY total_sales DESC;

#CATEGORY-WISE SALES
SELECT 
    category,
    SUM(quantity * price) AS total_sales
FROM retail_sales
GROUP BY category
ORDER BY total_sales DESC;


#REGION -WISE SALES
SELECT 
    region,
    SUM(quantity * price) AS total_sales
FROM retail_sales
GROUP BY region
ORDER BY total_sales DESC;


#MONTHLY SALES
SELECT
    MONTH(sale_date) AS month,
    SUM(quantity * price) AS total_sales
FROM retail_sales
GROUP BY MONTH(sale_date)
ORDER BY month;

SHOW DATABASES;

SELECT * FROM RETAIL_SALES;

USE retail_sales;

CREATE OR REPLACE VIEW customer_intelligence AS
SELECT
    customer_name,
    COUNT(*) AS total_orders,
    SUM(quantity) AS total_quantity,
    SUM(quantity * price) AS total_spent,
    AVG(quantity * price) AS average_order_value,
    MAX(sale_date) AS last_purchase_date
FROM retail_sales
GROUP BY customer_name;

SELECT * FROM customer_intelligence;

USE retail_sales;

-- ============================================================
-- CUSTOMER INTELLIGENCE
-- ============================================================

DROP VIEW IF EXISTS customer_intelligence;

CREATE VIEW customer_intelligence AS
SELECT
    customer_name,
    COUNT(*) AS total_orders,
    SUM(quantity) AS total_quantity,
    SUM(quantity * price) AS total_spent,
    AVG(quantity * price) AS average_order_value,
    MAX(sale_date) AS last_purchase_date
FROM retail_sales
WHERE customer_name IS NOT NULL
  AND customer_name <> ''
GROUP BY customer_name;


-- ============================================================
-- VERIFY CUSTOMER INTELLIGENCE
-- ============================================================

SELECT *
FROM customer_intelligence
ORDER BY total_spent DESC;










