import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Retail Sales Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI-Powered Retail Sales Intelligence")

st.write(
    "Retail sales analysis, AI prediction, forecasting, "
    "inventory intelligence, customer intelligence and AI insights"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 Retail Sales")
st.sidebar.write("AI-Powered Sales Intelligence")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Sales Analysis",
        "AI Prediction",
        "Sales Forecasting",
        "Inventory Intelligence",
        "Customer Intelligence",
        "🤖 AI Insights"
    ]
)


# ============================================================
# MYSQL CONNECTION
# ============================================================

try:

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="retail_sales"
    )

except mysql.connector.Error as e:

    st.error(f"❌ MySQL connection failed: {e}")
    st.stop()


# ============================================================
# LOAD SALES DATA
# ============================================================

try:

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM retail_sales"
    )

    rows = cursor.fetchall()

    columns = cursor.column_names

    cursor.close()

except mysql.connector.Error as e:

    connection.close()

    st.error(
        f"❌ Could not load sales data: {e}"
    )

    st.stop()


df = pd.DataFrame(
    rows,
    columns=columns
)


if df.empty:

    connection.close()

    st.warning(
        "⚠️ No sales data found."
    )

    st.stop()


# ============================================================
# DATA CLEANING
# ============================================================

df["quantity"] = pd.to_numeric(
    df["quantity"],
    errors="coerce"
)

df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
)

df["sale_date"] = pd.to_datetime(
    df["sale_date"],
    errors="coerce"
)

df["total_sales"] = (
    df["quantity"] * df["price"]
)

df["total_sales"] = pd.to_numeric(
    df["total_sales"],
    errors="coerce"
).astype(float)

df["quantity"] = df[
    "quantity"
].astype(float)

df["price"] = df[
    "price"
].astype(float)

df = df.dropna(
    subset=[
        "sale_date",
        "quantity",
        "price",
        "total_sales"
    ]
).copy()


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.header("📊 Sales Dashboard")

    st.subheader("🔎 Filters")

    col1, col2 = st.columns(2)

    with col1:

        categories = sorted(
            df["category"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_category = st.selectbox(
            "Select Category",
            ["All"] + categories
        )

    with col2:

        regions = sorted(
            df["region"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_region = st.selectbox(
            "Select Region",
            ["All"] + regions
        )

    filtered_df = df.copy()

    if selected_category != "All":

        filtered_df = filtered_df[
            filtered_df["category"]
            == selected_category
        ]

    if selected_region != "All":

        filtered_df = filtered_df[
            filtered_df["region"]
            == selected_region
        ]

    total_sales = (
        filtered_df["total_sales"].sum()
    )

    total_quantity = (
        filtered_df["quantity"].sum()
    )

    total_products = (
        filtered_df["product_name"].nunique()
    )

    total_regions = (
        filtered_df["region"].nunique()
    )

    total_orders = len(filtered_df)

    if total_orders > 0:

        average_order_value = (
            total_sales / total_orders
        )

    else:

        average_order_value = 0

    if not filtered_df.empty:

        product_sales = (
            filtered_df
            .groupby("product_name")[
                "total_sales"
            ]
            .sum()
        )

        top_product = (
            product_sales.idxmax()
        )

    else:

        top_product = "N/A"

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:

        st.metric(
            "💰 Total Sales",
            f"₹{total_sales:,.2f}"
        )

    with col2:

        st.metric(
            "📦 Total Quantity",
            f"{total_quantity:,.0f}"
        )

    with col3:

        st.metric(
            "🛍️ Products",
            total_products
        )

    with col4:

        st.metric(
            "🌍 Regions",
            total_regions
        )

    with col5:

        st.metric(
            "🧾 Average Order",
            f"₹{average_order_value:,.2f}"
        )

    with col6:

        st.metric(
            "🏆 Top Product",
            top_product
        )

    st.divider()

    st.subheader(
        "📋 Filtered Sales Data"
    )

    st.dataframe(
        filtered_df,
        width="stretch"
    )

    csv = filtered_df.to_csv(
        index=False
    )

    st.download_button(
        label="📥 Download Filtered Sales CSV",
        data=csv,
        file_name="filtered_sales.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader(
        "📋 Complete Sales Data"
    )

    st.dataframe(
        df,
        width="stretch"
    )


# ============================================================
# SALES ANALYSIS
# ============================================================

elif page == "Sales Analysis":

    st.header("📈 Sales Analysis")

    st.subheader(
        "🛍️ Product-wise Sales"
    )

    product_sales = (
        df.groupby("product_name")[
            "total_sales"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .astype(float)
    )

    st.dataframe(
        product_sales.reset_index(),
        width="stretch"
    )

    fig, ax = plt.subplots()

    product_sales.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Sales by Product"
    )

    ax.set_xlabel(
        "Product"
    )

    ax.set_ylabel(
        "Sales"
    )

    plt.xticks(
        rotation=45
    )

    st.pyplot(fig)

    st.subheader(
        "🏆 Top 5 Products"
    )

    st.dataframe(
        product_sales
        .head(5)
        .reset_index(),
        width="stretch"
    )

    st.subheader(
        "📂 Category-wise Sales"
    )

    category_sales = (
        df.groupby("category")[
            "total_sales"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .astype(float)
    )

    st.dataframe(
        category_sales.reset_index(),
        width="stretch"
    )

    fig, ax = plt.subplots()

    category_sales.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Sales by Category"
    )

    ax.set_xlabel(
        "Category"
    )

    ax.set_ylabel(
        "Sales"
    )

    plt.xticks(
        rotation=45
    )

    st.pyplot(fig)

    st.subheader(
        "🥧 Category Sales Distribution"
    )

    fig, ax = plt.subplots()

    category_sales.plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax
    )

    ax.set_ylabel("")

    st.pyplot(fig)

    st.subheader(
        "🌍 Region-wise Sales"
    )

    region_sales = (
        df.groupby("region")[
            "total_sales"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .astype(float)
    )

    st.dataframe(
        region_sales.reset_index(),
        width="stretch"
    )

    fig, ax = plt.subplots()

    region_sales.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Sales by Region"
    )

    ax.set_xlabel(
        "Region"
    )

    ax.set_ylabel(
        "Sales"
    )

    plt.xticks(
        rotation=45
    )

    st.pyplot(fig)

    st.subheader(
        "📅 Monthly Sales"
    )

    monthly_sales = (
        df.assign(
            month=df["sale_date"]
            .dt.to_period("M")
            .astype(str)
        )
        .groupby("month")[
            "total_sales"
        ]
        .sum()
        .astype(float)
    )

    st.dataframe(
        monthly_sales.reset_index(),
        width="stretch"
    )

    fig, ax = plt.subplots()

    monthly_sales.plot(
        kind="line",
        marker="o",
        ax=ax
    )

    ax.set_title(
        "Monthly Sales Trend"
    )

    ax.set_xlabel(
        "Month"
    )

    ax.set_ylabel(
        "Sales"
    )

    plt.xticks(
        rotation=45
    )

    st.pyplot(fig)

    st.subheader(
        "📆 Daily Sales Trend"
    )

    daily_sales = (
        df.groupby("sale_date")[
            "total_sales"
        ]
        .sum()
        .astype(float)
        .sort_index()
    )

    fig, ax = plt.subplots()

    daily_sales.plot(
        kind="line",
        ax=ax
    )

    ax.set_title(
        "Daily Sales Trend"
    )

    ax.set_xlabel(
        "Date"
    )

    ax.set_ylabel(
        "Sales"
    )

    st.pyplot(fig)

    st.subheader(
        "🗓️ Sales by Day of Week"
    )

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    df["day_of_week"] = (
        df["sale_date"].dt.day_name()
    )

    day_sales = (
        df.groupby("day_of_week")[
            "total_sales"
        ]
        .sum()
        .reindex(day_order)
        .astype(float)
    )

    st.dataframe(
        day_sales.reset_index(),
        width="stretch"
    )

    fig, ax = plt.subplots()

    day_sales.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Sales by Day of Week"
    )

    ax.set_xlabel(
        "Day"
    )

    ax.set_ylabel(
        "Sales"
    )

    plt.xticks(
        rotation=45
    )

    st.pyplot(fig)

    st.subheader(
        "📊 Sales Performance Summary"
    )

    highest_sale = (
        df["total_sales"].max()
    )

    lowest_sale = (
        df["total_sales"].min()
    )

    average_sale = (
        df["total_sales"].mean()
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🔥 Highest Sale",
            f"₹{highest_sale:,.2f}"
        )

    with col2:

        st.metric(
            "⬇️ Lowest Sale",
            f"₹{lowest_sale:,.2f}"
        )

    with col3:

        st.metric(
            "📊 Average Sale",
            f"₹{average_sale:,.2f}"
        )

    st.subheader(
        "👥 Top 5 Customers"
    )

    customer_sales = (
        df.groupby("customer_name")[
            "total_sales"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .astype(float)
    )

    st.dataframe(
        customer_sales
        .head(5)
        .reset_index(),
        width="stretch"
    )

    best_customer = (
        customer_sales.idxmax()
    )

    st.success(
        f"🏆 Best Customer: {best_customer}"
    )

    highest_sale_row = df.loc[
        df["total_sales"].idxmax()
    ]

    st.info(
        f"💰 Highest Single Sale: "
        f"{highest_sale_row['product_name']} - "
        f"₹{highest_sale_row['total_sales']:,.2f}"
    )

    best_region = (
        region_sales.idxmax()
    )

    st.success(
        f"🌍 Best Performing Region: {best_region}"
    )

    st.subheader(
        "🌍 Region Sales Summary"
    )

    region_summary = (
        df.groupby("region")
        .agg(
            total_sales=(
                "total_sales",
                "sum"
            ),
            total_quantity=(
                "quantity",
                "sum"
            ),
            orders=(
                "sale_id",
                "count"
            )
        )
        .reset_index()
    )

    region_summary[
        "total_sales"
    ] = region_summary[
        "total_sales"
    ].astype(float)

    st.dataframe(
        region_summary,
        width="stretch"
    )

    st.subheader(
        "📦 Quantity Sold by Product"
    )

    quantity_product = (
        df.groupby("product_name")[
            "quantity"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .astype(float)
    )

    st.dataframe(
        quantity_product.reset_index(),
        width="stretch"
    )

    st.subheader(
        "💵 Average Price by Product"
    )

    average_price = (
        df.groupby("product_name")[
            "price"
        ]
        .mean()
        .sort_values(
            ascending=False
        )
        .astype(float)
    )

    st.dataframe(
        average_price.reset_index(),
        width="stretch"
    )


# ============================================================
# AI PREDICTION
# ============================================================

elif page == "AI Prediction":

    st.header(
        "🤖 AI Sales Prediction"
    )

    st.write(
        "Use Machine Learning to predict sales "
        "from quantity and price."
    )

    X = df[
        [
            "quantity",
            "price"
        ]
    ].astype(float)

    y = df[
        "total_sales"
    ].astype(float)

    model = LinearRegression()

    model.fit(
        X,
        y
    )

    model_score = model.score(
        X,
        y
    )

    st.subheader(
        "🧠 Model Information"
    )

    st.write(
        "Model: Linear Regression"
    )

    st.write(
        f"R² Score: {model_score:.4f}"
    )

    st.divider()

    st.subheader(
        "Enter Sales Information"
    )

    col1, col2 = st.columns(2)

    with col1:

        quantity_input = st.number_input(
            "Enter Quantity",
            min_value=1,
            value=1,
            step=1
        )

    with col2:

        price_input = st.number_input(
            "Enter Price",
            min_value=0.0,
            value=100.0,
            step=10.0
        )

    if st.button(
        "🔮 Predict Sales"
    ):

        input_data = pd.DataFrame(
            {
                "quantity": [
                    float(quantity_input)
                ],
                "price": [
                    float(price_input)
                ]
            }
        )

        prediction = model.predict(
            input_data
        )[0]

        prediction = max(
            0,
            prediction
        )

        st.success(
            f"💰 Predicted Sales: "
            f"₹{prediction:,.2f}"
        )


# ============================================================
# SALES FORECASTING
# ============================================================

elif page == "Sales Forecasting":

    st.header(
        "📈 Sales Forecasting"
    )

    st.write(
        "Forecast future sales using "
        "historical daily sales."
    )

    daily_sales = (
        df.groupby("sale_date")[
            "total_sales"
        ]
        .sum()
        .astype(float)
        .sort_index()
        .reset_index()
    )

    daily_sales.columns = [
        "Date",
        "Sales"
    ]

    if len(daily_sales) < 2:

        st.warning(
            "⚠️ At least 2 different sales dates "
            "are required for forecasting."
        )

    else:

        daily_sales[
            "day_number"
        ] = range(
            len(daily_sales)
        )

        X = daily_sales[
            ["day_number"]
        ]

        y = daily_sales[
            "Sales"
        ]

        forecast_model = (
            LinearRegression()
        )

        forecast_model.fit(
            X,
            y
        )

        forecast_days = st.slider(
            "Select number of future days",
            min_value=1,
            max_value=365,
            value=30
        )

        future_day_numbers = range(
            len(daily_sales),
            len(daily_sales)
            + forecast_days
        )

        future_day_df = pd.DataFrame(
            {
                "day_number":
                list(
                    future_day_numbers
                )
            }
        )

        future_predictions = (
            forecast_model
            .predict(
                future_day_df
            )
        )

        future_predictions = [
            max(0, value)
            for value in future_predictions
        ]

        last_date = daily_sales[
            "Date"
        ].max()

        future_dates = pd.date_range(
            start=(
                last_date
                + pd.Timedelta(days=1)
            ),
            periods=forecast_days,
            freq="D"
        )

        forecast_df = pd.DataFrame(
            {
                "Date": future_dates,
                "Forecasted Sales":
                    future_predictions
            }
        )

        total_forecast = sum(
            future_predictions
        )

        average_forecast = (
            total_forecast
            / forecast_days
        )

        highest_forecast = max(
            future_predictions
        )

        st.subheader(
            "🔮 Forecast Summary"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "💰 Total Forecast",
                f"₹{total_forecast:,.2f}"
            )

        with col2:

            st.metric(
                "📊 Average Daily Forecast",
                f"₹{average_forecast:,.2f}"
            )

        with col3:

            st.metric(
                "🔥 Highest Forecast",
                f"₹{highest_forecast:,.2f}"
            )

        st.subheader(
            "📈 Historical + Forecasted Sales"
        )

        fig, ax = plt.subplots()

        ax.plot(
            daily_sales["Date"],
            daily_sales["Sales"],
            label="Historical Sales"
        )

        ax.plot(
            forecast_df["Date"],
            forecast_df[
                "Forecasted Sales"
            ],
            label="Forecasted Sales"
        )

        ax.set_xlabel(
            "Date"
        )

        ax.set_ylabel(
            "Sales"
        )

        ax.set_title(
            "Sales Forecast"
        )

        ax.legend()

        plt.xticks(
            rotation=45
        )

        st.pyplot(fig)

        st.subheader(
            "📋 Forecast Details"
        )

        st.dataframe(
            forecast_df,
            width="stretch"
        )

        forecast_csv = (
            forecast_df.to_csv(
                index=False
            )
        )

        st.download_button(
            label="📥 Download Forecast CSV",
            data=forecast_csv,
            file_name="sales_forecast.csv",
            mime="text/csv"
        )

        st.info(
            "Model used: Linear Regression "
            "based on historical daily sales."
        )


# ============================================================
# INVENTORY INTELLIGENCE
# ============================================================

elif page == "Inventory Intelligence":

    st.header(
        "📦 Inventory Intelligence"
    )

    st.write(
        "Monitor stock levels and identify "
        "products that require restocking."
    )

    inventory_query = """
    SELECT
        product_name,
        stock_quantity,
        reorder_level,
        last_restock_date
    FROM inventory
    ORDER BY product_name
    """

    try:

        cursor = connection.cursor()

        cursor.execute(
            inventory_query
        )

        inventory_rows = (
            cursor.fetchall()
        )

        inventory_columns = (
            cursor.column_names
        )

        cursor.close()

    except mysql.connector.Error as e:

        st.error(
            f"❌ Could not load inventory data: {e}"
        )

        connection.close()

        st.stop()

    inventory_df = pd.DataFrame(
        inventory_rows,
        columns=inventory_columns
    )

    if inventory_df.empty:

        st.warning(
            "⚠️ No inventory data found."
        )

        connection.close()

        st.stop()

    inventory_df[
        "stock_quantity"
    ] = pd.to_numeric(
        inventory_df[
            "stock_quantity"
        ],
        errors="coerce"
    )

    inventory_df[
        "reorder_level"
    ] = pd.to_numeric(
        inventory_df[
            "reorder_level"
        ],
        errors="coerce"
    )

    inventory_df[
        "last_restock_date"
    ] = pd.to_datetime(
        inventory_df[
            "last_restock_date"
        ],
        errors="coerce"
    )

    daily_product_sales = (
        df.groupby(
            [
                "product_name",
                "sale_date"
            ]
        )["quantity"]
        .sum()
        .reset_index()
    )

    average_daily_sales = (
        daily_product_sales
        .groupby("product_name")[
            "quantity"
        ]
        .mean()
    )

    inventory_df[
        "average_daily_sales"
    ] = (
        inventory_df[
            "product_name"
        ]
        .map(
            average_daily_sales
        )
        .fillna(0)
    )

    def calculate_days_of_stock(row):

        if (
            row["average_daily_sales"]
            <= 0
        ):

            return 999

        return (
            row["stock_quantity"]
            /
            row["average_daily_sales"]
        )

    inventory_df[
        "days_of_stock"
    ] = inventory_df.apply(
        calculate_days_of_stock,
        axis=1
    )

    def get_stock_status(row):

        if row["stock_quantity"] <= 0:

            return "❌ Out of Stock"

        elif (
            row["stock_quantity"]
            <= row["reorder_level"]
        ):

            return "🔴 Reorder Now"

        elif (
            row["days_of_stock"]
            <= 7
        ):

            return "🟠 Low Stock"

        else:

            return "🟢 Healthy"

    inventory_df[
        "status"
    ] = inventory_df.apply(
        get_stock_status,
        axis=1
    )

    def get_recommendation(row):

        if row["stock_quantity"] <= 0:

            return "Order Immediately"

        elif (
            row["stock_quantity"]
            <= row["reorder_level"]
        ):

            return "Reorder Now"

        elif (
            row["days_of_stock"]
            <= 7
        ):

            return "Reorder Soon"

        else:

            return "No Reorder Needed"

    inventory_df[
        "recommendation"
    ] = inventory_df.apply(
        get_recommendation,
        axis=1
    )

    total_stock = (
        inventory_df[
            "stock_quantity"
        ].sum()
    )

    out_of_stock = (
        inventory_df["status"]
        == "❌ Out of Stock"
    ).sum()

    reorder_now = (
        inventory_df["status"]
        == "🔴 Reorder Now"
    ).sum()

    healthy_products = (
        inventory_df["status"]
        == "🟢 Healthy"
    ).sum()

    st.subheader(
        "📊 Inventory Overview"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📦 Total Stock",
            f"{total_stock:,.0f}"
        )

    with col2:

        st.metric(
            "❌ Out of Stock",
            out_of_stock
        )

    with col3:

        st.metric(
            "🔴 Reorder Now",
            reorder_now
        )

    with col4:

        st.metric(
            "🟢 Healthy Products",
            healthy_products
        )

    st.divider()

    attention_products = (
        inventory_df[
            inventory_df["status"].isin(
                [
                    "❌ Out of Stock",
                    "🔴 Reorder Now",
                    "🟠 Low Stock"
                ]
            )
        ]
    )

    st.subheader(
        "⚠️ Inventory Alerts"
    )

    if not attention_products.empty:

        for _, row in (
            attention_products.iterrows()
        ):

            if (
                row["status"]
                == "❌ Out of Stock"
            ):

                st.error(
                    f"❌ {row['product_name']} "
                    "is OUT OF STOCK."
                )

            elif (
                row["status"]
                == "🔴 Reorder Now"
            ):

                st.warning(
                    f"🔴 {row['product_name']} "
                    "needs to be reordered."
                )

            else:

                st.warning(
                    f"🟠 {row['product_name']} "
                    f"has approximately "
                    f"{row['days_of_stock']:.1f} "
                    "days of stock."
                )

    else:

        st.success(
            "✅ All products have healthy stock levels."
        )

    st.subheader(
        "📋 Inventory Status"
    )

    inventory_display = inventory_df[
        [
            "product_name",
            "stock_quantity",
            "reorder_level",
            "average_daily_sales",
            "days_of_stock",
            "status",
            "recommendation",
            "last_restock_date"
        ]
    ].copy()

    inventory_display[
        "average_daily_sales"
    ] = inventory_display[
        "average_daily_sales"
    ].round(2)

    inventory_display[
        "days_of_stock"
    ] = inventory_display[
        "days_of_stock"
    ].round(1)

    st.dataframe(
        inventory_display,
        width="stretch"
    )

    st.subheader(
        "📊 Current Stock by Product"
    )

    stock_chart = (
        inventory_df
        .set_index("product_name")[
            "stock_quantity"
        ]
    )

    fig, ax = plt.subplots()

    stock_chart.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Current Stock by Product"
    )

    ax.set_xlabel(
        "Product"
    )

    ax.set_ylabel(
        "Stock Quantity"
    )

    plt.xticks(
        rotation=45
    )

    st.pyplot(fig)

    st.subheader(
        "⏳ Estimated Days of Stock Remaining"
    )

    days_chart = (
        inventory_df
        .set_index("product_name")[
            "days_of_stock"
        ]
        .clip(
            upper=60
        )
    )

    fig, ax = plt.subplots()

    days_chart.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Estimated Days of Stock Remaining"
    )

    ax.set_xlabel(
        "Product"
    )

    ax.set_ylabel(
        "Days of Stock"
    )

    plt.xticks(
        rotation=45
    )

    st.pyplot(fig)

    st.subheader(
        "🚨 Products Requiring Attention"
    )

    if not attention_products.empty:

        attention_display = (
            attention_products[
                [
                    "product_name",
                    "stock_quantity",
                    "reorder_level",
                    "average_daily_sales",
                    "days_of_stock",
                    "status",
                    "recommendation"
                ]
            ].copy()
        )

        attention_display[
            "average_daily_sales"
        ] = attention_display[
            "average_daily_sales"
        ].round(2)

        attention_display[
            "days_of_stock"
        ] = attention_display[
            "days_of_stock"
        ].round(1)

        st.dataframe(
            attention_display,
            width="stretch"
        )

    else:

        st.success(
            "No products currently require attention."
        )

    inventory_csv = (
        inventory_display.to_csv(
            index=False
        )
    )

    st.download_button(
        label="📥 Download Inventory Report",
        data=inventory_csv,
        file_name="inventory_report.csv",
        mime="text/csv"
    )

    st.info(
        "ℹ️ Days of Stock = Current Stock ÷ "
        "Average Daily Product Sales."
    )


# ============================================================
# CUSTOMER INTELLIGENCE
# ============================================================

elif page == "Customer Intelligence":

    st.header(
        "👥 Customer Intelligence"
    )

    st.write(
        "Analyze customer purchasing behavior, "
        "identify valuable customers and understand "
        "repeat purchasing patterns."
    )

    customer_query = """
    SELECT
        customer_name,
        total_orders,
        total_quantity,
        total_spent,
        average_order_value,
        last_purchase_date
    FROM customer_intelligence
    ORDER BY total_spent DESC
    """

    try:

        cursor = connection.cursor()

        cursor.execute(
            customer_query
        )

        customer_rows = (
            cursor.fetchall()
        )

        customer_columns = (
            cursor.column_names
        )

        cursor.close()

    except mysql.connector.Error as e:

        st.error(
            f"❌ Could not load customer intelligence: {e}"
        )

        connection.close()

        st.stop()

    customer_df = pd.DataFrame(
        customer_rows,
        columns=customer_columns
    )

    if customer_df.empty:

        st.warning(
            "⚠️ No customer data found."
        )

        connection.close()

        st.stop()

    customer_df[
        "total_orders"
    ] = pd.to_numeric(
        customer_df[
            "total_orders"
        ],
        errors="coerce"
    )

    customer_df[
        "total_quantity"
    ] = pd.to_numeric(
        customer_df[
            "total_quantity"
        ],
        errors="coerce"
    )

    customer_df[
        "total_spent"
    ] = pd.to_numeric(
        customer_df[
            "total_spent"
        ],
        errors="coerce"
    ).astype(float)

    customer_df[
        "average_order_value"
    ] = pd.to_numeric(
        customer_df[
            "average_order_value"
        ],
        errors="coerce"
    ).astype(float)

    customer_df[
        "last_purchase_date"
    ] = pd.to_datetime(
        customer_df[
            "last_purchase_date"
        ],
        errors="coerce"
    )

    customer_df = customer_df.dropna(
        subset=[
            "customer_name",
            "total_spent"
        ]
    ).copy()

    st.subheader(
        "📊 Customer Overview"
    )

    total_customers = (
        customer_df[
            "customer_name"
        ].nunique()
    )

    customer_revenue = (
        customer_df[
            "total_spent"
        ].sum()
    )

    average_customer_spending = (
        customer_df[
            "total_spent"
        ].mean()
    )

    average_orders_per_customer = (
        customer_df[
            "total_orders"
        ].mean()
    )

    best_customer_row = (
        customer_df.loc[
            customer_df[
                "total_spent"
            ].idxmax()
        ]
    )

    best_customer = (
        best_customer_row[
            "customer_name"
        ]
    )

    best_customer_spending = (
        best_customer_row[
            "total_spent"
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "👥 Total Customers",
            total_customers
        )

    with col2:

        st.metric(
            "💰 Customer Revenue",
            f"₹{customer_revenue:,.2f}"
        )

    with col3:

        st.metric(
            "🛍️ Avg Orders / Customer",
            f"{average_orders_per_customer:.2f}"
        )

    with col4:

        st.metric(
            "💎 Avg Customer Spending",
            f"₹{average_customer_spending:,.2f}"
        )

    st.divider()

    st.subheader(
        "🏆 Best Customer"
    )

    st.success(
        f"🏆 {best_customer} is your best customer "
        f"with total spending of "
        f"₹{best_customer_spending:,.2f}."
    )

    st.subheader(
        "🏆 Top 5 Customers"
    )

    top_5_customers = (
        customer_df
        .sort_values(
            "total_spent",
            ascending=False
        )
        .head(5)
        .copy()
    )

    top_5_display = top_5_customers[
        [
            "customer_name",
            "total_orders",
            "total_quantity",
            "total_spent",
            "average_order_value",
            "last_purchase_date"
        ]
    ].copy()

    top_5_display[
        "total_spent"
    ] = top_5_display[
        "total_spent"
    ].round(2)

    top_5_display[
        "average_order_value"
    ] = top_5_display[
        "average_order_value"
    ].round(2)

    st.dataframe(
        top_5_display,
        width="stretch"
    )

    st.subheader(
        "💰 Customer Spending Chart"
    )

    spending_chart = (
        customer_df
        .sort_values(
            "total_spent",
            ascending=False
        )
        .head(10)
        .set_index(
            "customer_name"
        )[
            "total_spent"
        ]
    )

    fig, ax = plt.subplots()

    spending_chart.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Top 10 Customers by Spending"
    )

    ax.set_xlabel(
        "Customer"
    )

    ax.set_ylabel(
        "Total Spending"
    )

    plt.xticks(
        rotation=45
    )

    st.pyplot(fig)

    st.subheader(
        "🔁 Repeat vs One-Time Customers"
    )

    repeat_customers = customer_df[
        customer_df[
            "total_orders"
        ] > 1
    ]

    one_time_customers = customer_df[
        customer_df[
            "total_orders"
        ] == 1
    ]

    repeat_count = len(
        repeat_customers
    )

    one_time_count = len(
        one_time_customers
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "🔁 Repeat Customers",
            repeat_count
        )

    with col2:

        st.metric(
            "🧍 One-Time Customers",
            one_time_count
        )

    repeat_data = pd.Series(
        {
            "Repeat Customers":
                repeat_count,

            "One-Time Customers":
                one_time_count
        }
    )

    fig, ax = plt.subplots()

    repeat_data.plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax
    )

    ax.set_ylabel("")

    ax.set_title(
        "Customer Type Distribution"
    )

    st.pyplot(fig)

    st.subheader(
        "💎 Customer Segmentation"
    )

    spending_75 = (
        customer_df[
            "total_spent"
        ].quantile(0.75)
    )

    spending_25 = (
        customer_df[
            "total_spent"
        ].quantile(0.25)
    )

    def classify_customer(spending):

        if spending >= spending_75:

            return "💎 High Value"

        elif spending >= spending_25:

            return "⭐ Medium Value"

        else:

            return "🔹 Low Value"

    customer_df[
        "customer_segment"
    ] = customer_df[
        "total_spent"
    ].apply(
        classify_customer
    )

    high_value_count = (
        customer_df[
            customer_df[
                "customer_segment"
            ] == "💎 High Value"
        ].shape[0]
    )

    medium_value_count = (
        customer_df[
            customer_df[
                "customer_segment"
            ] == "⭐ Medium Value"
        ].shape[0]
    )

    low_value_count = (
        customer_df[
            customer_df[
                "customer_segment"
            ] == "🔹 Low Value"
        ].shape[0]
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "💎 High Value",
            high_value_count
        )

    with col2:

        st.metric(
            "⭐ Medium Value",
            medium_value_count
        )

    with col3:

        st.metric(
            "🔹 Low Value",
            low_value_count
        )

    segment_counts = (
        customer_df[
            "customer_segment"
        ]
        .value_counts()
    )

    fig, ax = plt.subplots()

    segment_counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Customer Segments"
    )

    ax.set_xlabel(
        "Customer Segment"
    )

    ax.set_ylabel(
        "Number of Customers"
    )

    plt.xticks(
        rotation=0
    )

    st.pyplot(fig)

    st.subheader(
        "📋 Complete Customer Intelligence"
    )

    customer_display = customer_df[
        [
            "customer_name",
            "total_orders",
            "total_quantity",
            "total_spent",
            "average_order_value",
            "last_purchase_date",
            "customer_segment"
        ]
    ].copy()

    customer_display[
        "total_spent"
    ] = customer_display[
        "total_spent"
    ].round(2)

    customer_display[
        "average_order_value"
    ] = customer_display[
        "average_order_value"
    ].round(2)

    st.dataframe(
        customer_display,
        width="stretch"
    )

    st.subheader(
        "💡 Business Insights"
    )

    if repeat_count > one_time_count:

        st.success(
            f"🔁 Repeat customers ({repeat_count}) "
            f"are higher than one-time customers "
            f"({one_time_count}). "
            "This indicates good customer retention."
        )

    elif one_time_count > repeat_count:

        st.warning(
            f"⚠️ One-time customers ({one_time_count}) "
            f"are higher than repeat customers "
            f"({repeat_count}). "
            "Consider loyalty programs and "
            "customer retention campaigns."
        )

    else:

        st.info(
            "ℹ️ Repeat and one-time customers "
            "are equal."
        )

    if high_value_count > 0:

        high_value_revenue = (
            customer_df[
                customer_df[
                    "customer_segment"
                ] == "💎 High Value"
            ]["total_spent"].sum()
        )

        high_value_percentage = (
            high_value_revenue
            /
            customer_revenue
            *
            100
        )

        st.info(
            f"💎 High-value customers generate "
            f"approximately "
            f"{high_value_percentage:.1f}% "
            "of total customer revenue."
        )

    if average_customer_spending > 0:

        st.info(
            f"💰 The average customer spends "
            f"₹{average_customer_spending:,.2f}."
        )

    st.info(
        f"🏆 {best_customer} is currently the "
        f"highest-value customer with "
        f"₹{best_customer_spending:,.2f} "
        "in total spending."
    )

    st.subheader(
        "📥 Customer Report"
    )

    customer_csv = (
        customer_display.to_csv(
            index=False
        )
    )

    st.download_button(
        label="📥 Download Customer Intelligence CSV",
        data=customer_csv,
        file_name="customer_intelligence_report.csv",
        mime="text/csv"
    )

    st.info(
        "ℹ️ Customer segments are calculated using "
        "customer spending. The top 25% are classified "
        "as High Value, the middle 50% as Medium Value, "
        "and the bottom 25% as Low Value."
    )


# ============================================================
# AI INSIGHTS
# ============================================================

elif page == "🤖 AI Insights":

    st.header(
        "🤖 AI Insights"
    )

    st.write(
        "Use Artificial Intelligence to detect unusual "
        "sales patterns and generate automatic business recommendations."
    )

    st.divider()

    # ========================================================
    # DAILY SALES DATA
    # ========================================================

    st.subheader(
        "🚨 Sales Anomaly Detection"
    )

    daily_sales_ai = (
        df.groupby("sale_date")[
            "total_sales"
        ]
        .sum()
        .astype(float)
        .sort_index()
        .reset_index()
    )

    daily_sales_ai.columns = [
        "sale_date",
        "total_sales"
    ]

    # Need at least 5 observations for meaningful anomaly detection

    if len(daily_sales_ai) < 5:

        st.warning(
            "⚠️ At least 5 different sales days are "
            "recommended for AI anomaly detection."
        )

    else:

        # ====================================================
        # ISOLATION FOREST MODEL
        # ====================================================

        anomaly_model = IsolationForest(
            contamination=0.10,
            random_state=42
        )

        daily_sales_ai[
            "anomaly_prediction"
        ] = anomaly_model.fit_predict(
            daily_sales_ai[
                ["total_sales"]
            ]
        )

        daily_sales_ai[
            "anomaly_score"
        ] = anomaly_model.decision_function(
            daily_sales_ai[
                ["total_sales"]
            ]
        )

        daily_sales_ai[
            "anomaly"
        ] = daily_sales_ai[
            "anomaly_prediction"
        ].apply(
            lambda x:
            "🚨 Anomaly"
            if x == -1
            else "✅ Normal"
        )

        # ====================================================
        # CALCULATE THRESHOLD
        # ====================================================

        average_daily_sales_ai = (
            daily_sales_ai[
                "total_sales"
            ].mean()
        )

        # ====================================================
        # HIGH / LOW ANOMALIES
        # ====================================================

        anomaly_df = daily_sales_ai[
            daily_sales_ai[
                "anomaly_prediction"
            ] == -1
        ].copy()

        high_anomalies = anomaly_df[
            anomaly_df[
                "total_sales"
            ] > average_daily_sales_ai
        ].copy()

        low_anomalies = anomaly_df[
            anomaly_df[
                "total_sales"
            ] < average_daily_sales_ai
        ].copy()

        # ====================================================
        # KPI VALUES
        # ====================================================

        total_sales_days = len(
            daily_sales_ai
        )

        anomalous_days = len(
            anomaly_df
        )

        normal_days = (
            total_sales_days
            -
            anomalous_days
        )

        # ====================================================
        # KPI DISPLAY
        # ====================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "📅 Total Sales Days",
                total_sales_days
            )

        with col2:

            st.metric(
                "✅ Normal Sales Days",
                normal_days
            )

        with col3:

            st.metric(
                "🚨 Anomalous Sales Days",
                anomalous_days
            )

        st.divider()

        # ====================================================
        # HIGH SALES ANOMALIES
        # ====================================================

        st.subheader(
            "📈 High Sales Anomalies"
        )

        if not high_anomalies.empty:

            high_display = high_anomalies[
                [
                    "sale_date",
                    "total_sales",
                    "anomaly_score"
                ]
            ].copy()

            high_display[
                "total_sales"
            ] = high_display[
                "total_sales"
            ].round(2)

            high_display[
                "anomaly_score"
            ] = high_display[
                "anomaly_score"
            ].round(4)

            st.dataframe(
                high_display,
                width="stretch"
            )

        else:

            st.info(
                "ℹ️ No unusually high sales days "
                "were detected."
            )

        # ====================================================
        # LOW SALES ANOMALIES
        # ====================================================

        st.subheader(
            "📉 Low Sales Anomalies"
        )

        if not low_anomalies.empty:

            low_display = low_anomalies[
                [
                    "sale_date",
                    "total_sales",
                    "anomaly_score"
                ]
            ].copy()

            low_display[
                "total_sales"
            ] = low_display[
                "total_sales"
            ].round(2)

            low_display[
                "anomaly_score"
            ] = low_display[
                "anomaly_score"
            ].round(4)

            st.dataframe(
                low_display,
                width="stretch"
            )

        else:

            st.info(
                "ℹ️ No unusually low sales days "
                "were detected."
            )

        # ====================================================
        # ANOMALY CHART
        # ====================================================

        st.subheader(
            "📊 Sales Anomaly Visualization"
        )

        fig, ax = plt.subplots()

        normal_data = daily_sales_ai[
            daily_sales_ai[
                "anomaly_prediction"
            ] == 1
        ]

        anomaly_data = daily_sales_ai[
            daily_sales_ai[
                "anomaly_prediction"
            ] == -1
        ]

        ax.plot(
            daily_sales_ai[
                "sale_date"
            ],
            daily_sales_ai[
                "total_sales"
            ],
            label="Daily Sales"
        )

        if not normal_data.empty:

            ax.scatter(
                normal_data[
                    "sale_date"
                ],
                normal_data[
                    "total_sales"
                ],
                label="Normal"
            )

        if not anomaly_data.empty:

            ax.scatter(
                anomaly_data[
                    "sale_date"
                ],
                anomaly_data[
                    "total_sales"
                ],
                marker="X",
                s=100,
                label="Anomaly"
            )

        ax.axhline(
            average_daily_sales_ai,
            linestyle="--",
            label="Average Sales"
        )

        ax.set_title(
            "AI Sales Anomaly Detection"
        )

        ax.set_xlabel(
            "Date"
        )

        ax.set_ylabel(
            "Sales"
        )

        ax.legend()

        plt.xticks(
            rotation=45
        )

        st.pyplot(fig)

        # ====================================================
        # AI BUSINESS RECOMMENDATIONS
        # ====================================================

        st.subheader(
            "💡 AI Business Recommendations"
        )

        recommendations = []

        if len(high_anomalies) > 0:

            recommendations.append(
                "📈 Unusually high sales were detected. "
                "Review the products and dates involved and "
                "consider increasing inventory for high-demand products."
            )

        if len(low_anomalies) > 0:

            recommendations.append(
                "📉 Unusually low sales were detected. "
                "Investigate possible causes such as low demand, "
                "pricing issues, stock availability or reduced marketing."
            )

        if anomalous_days == 0:

            recommendations.append(
                "✅ Sales are relatively stable. "
                "No significant unusual sales patterns were detected."
            )

        if len(high_anomalies) > 0:

            recommendations.append(
                "📦 Check inventory levels after unusually high "
                "sales days to reduce the risk of stock shortages."
            )

        if len(low_anomalies) > 0:

            recommendations.append(
                "📢 Consider targeted marketing campaigns "
                "for products or periods showing weak sales."
            )

        # Product-level recommendation

        product_ai_sales = (
            df.groupby("product_name")[
                "total_sales"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if not product_ai_sales.empty:

            best_ai_product = (
                product_ai_sales.idxmax()
            )

            recommendations.append(
                f"🏆 {best_ai_product} is currently the "
                "highest-selling product. Monitor its inventory "
                "and consider promoting it further."
            )

        for recommendation in recommendations:

            st.info(
                recommendation
            )

        # ====================================================
        # AI INSIGHTS SUMMARY TABLE
        # ====================================================

        st.subheader(
            "📋 Complete AI Anomaly Report"
        )

        ai_report = daily_sales_ai[
            [
                "sale_date",
                "total_sales",
                "anomaly",
                "anomaly_score"
            ]
        ].copy()

        ai_report[
            "total_sales"
        ] = ai_report[
            "total_sales"
        ].round(2)

        ai_report[
            "anomaly_score"
        ] = ai_report[
            "anomaly_score"
        ].round(4)

        st.dataframe(
            ai_report,
            width="stretch"
        )

        # ====================================================
        # DOWNLOAD REPORT
        # ====================================================

        st.subheader(
            "📥 Download AI Report"
        )

        ai_csv = (
            ai_report.to_csv(
                index=False
            )
        )

        st.download_button(
            label="📥 Download AI Anomaly Report",
            data=ai_csv,
            file_name="ai_sales_anomaly_report.csv",
            mime="text/csv"
        )

        st.success(
            "🤖 AI analysis completed successfully."
        )

        st.info(
            "ℹ️ Isolation Forest is used to identify "
            "unusual daily sales patterns. An anomaly does "
            "not necessarily mean an error; it indicates a "
            "sales value that differs significantly from the "
            "usual pattern."
        )


# ============================================================
# CLOSE DATABASE CONNECTION
# ============================================================

connection.close()