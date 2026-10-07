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
    page_title="AI Retail Sales Intelligence",
    page_icon="🛒",
    layout="wide"
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
except Exception as e:
    st.error("❌ Could not connect to MySQL.")
    st.error(e)
    st.stop()


# ============================================================
# LOAD SALES DATA
# ============================================================

query = """
SELECT
    sale_id,
    sale_date,
    product_name,
    category,
    quantity,
    price,
    customer_name,
    region
FROM retail_sales
"""

try:
    df = pd.read_sql(query, connection)
except Exception as e:
    st.error("❌ Could not load sales data.")
    st.error(e)
    connection.close()
    st.stop()


# ============================================================
# DATA CLEANING
# ============================================================

df["sale_date"] = pd.to_datetime(
    df["sale_date"],
    errors="coerce"
)

df["quantity"] = pd.to_numeric(
    df["quantity"],
    errors="coerce"
)

df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
)

df["total_sales"] = (
    df["quantity"] * df["price"]
)

df["total_sales"] = pd.to_numeric(
    df["total_sales"],
    errors="coerce"
).astype(float)

df["quantity"] = df["quantity"].astype(float)
df["price"] = df["price"].astype(float)

df = df.dropna(
    subset=[
        "sale_date",
        "quantity",
        "price",
        "total_sales"
    ]
)

df["day_of_week"] = df["sale_date"].dt.day_name()
df["month"] = df["sale_date"].dt.to_period("M").astype(str)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🛒 Retail Intelligence")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Sales Analysis",
        "Advanced Product Intelligence",
        "AI Prediction",
        "Sales Forecasting",
        "Inventory Intelligence",
        "Customer Intelligence",
        "🤖 AI Insights"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.title("📊 Executive Retail Sales Dashboard")

    st.write(
        "Analyze sales performance, products, customers and regions."
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    st.subheader("🔎 Dashboard Filters")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        categories = [
            "All Categories"
        ] + sorted(
            df["category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_category = st.selectbox(
            "Category",
            categories
        )

    with filter_col2:

        regions = [
            "All Regions"
        ] + sorted(
            df["region"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_region = st.selectbox(
            "Region",
            regions
        )

    with filter_col3:

        min_date = df["sale_date"].min().date()
        max_date = df["sale_date"].max().date()

        selected_dates = st.date_input(
            "Date Range",
            value=(min_date, max_date)
        )

    dashboard_df = df.copy()

    if selected_category != "All Categories":
        dashboard_df = dashboard_df[
            dashboard_df["category"] == selected_category
        ]

    if selected_region != "All Regions":
        dashboard_df = dashboard_df[
            dashboard_df["region"] == selected_region
        ]

    if (
        isinstance(selected_dates, tuple)
        and len(selected_dates) == 2
    ):
        start_date, end_date = selected_dates

        dashboard_df = dashboard_df[
            (
                dashboard_df["sale_date"].dt.date >= start_date
            )
            &
            (
                dashboard_df["sale_date"].dt.date <= end_date
            )
        ]

    if dashboard_df.empty:

        st.warning(
            "⚠️ No sales data found for the selected filters."
        )

    else:

        # ----------------------------------------------------
        # KPI CALCULATIONS
        # ----------------------------------------------------

        total_sales = dashboard_df["total_sales"].sum()

        total_quantity = dashboard_df["quantity"].sum()

        total_orders = dashboard_df["sale_id"].nunique()

        total_products = dashboard_df["product_name"].nunique()

        average_order_value = (
            total_sales / total_orders
            if total_orders > 0
            else 0
        )

        # ----------------------------------------------------
        # SALES GROWTH
        # ----------------------------------------------------

        unique_dates = sorted(
            dashboard_df["sale_date"].dt.date.unique()
        )

        growth_percentage = 0

        if len(unique_dates) >= 2:

            middle = len(unique_dates) // 2

            first_half_dates = unique_dates[:middle]
            second_half_dates = unique_dates[middle:]

            first_sales = dashboard_df[
                dashboard_df["sale_date"].dt.date.isin(
                    first_half_dates
                )
            ]["total_sales"].sum()

            second_sales = dashboard_df[
                dashboard_df["sale_date"].dt.date.isin(
                    second_half_dates
                )
            ]["total_sales"].sum()

            if first_sales != 0:
                growth_percentage = (
                    (second_sales - first_sales)
                    / first_sales
                ) * 100

        # ----------------------------------------------------
        # TOP PRODUCT
        # ----------------------------------------------------

        product_sales_dashboard = (
            dashboard_df
            .groupby("product_name")["total_sales"]
            .sum()
            .sort_values(ascending=False)
        )

        top_product = (
            product_sales_dashboard.index[0]
            if not product_sales_dashboard.empty
            else "N/A"
        )

        # ----------------------------------------------------
        # BEST REGION
        # ----------------------------------------------------

        region_sales_dashboard = (
            dashboard_df
            .groupby("region")["total_sales"]
            .sum()
            .sort_values(ascending=False)
        )

        best_region = (
            region_sales_dashboard.index[0]
            if not region_sales_dashboard.empty
            else "N/A"
        )

        # ----------------------------------------------------
        # KPI DISPLAY
        # ----------------------------------------------------

        st.subheader("📌 Key Performance Indicators")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "💰 Total Revenue",
            f"₹{total_sales:,.2f}"
        )

        c2.metric(
            "📦 Quantity Sold",
            f"{total_quantity:,.0f}"
        )

        c3.metric(
            "🧾 Total Orders",
            f"{total_orders:,}"
        )

        c4.metric(
            "🛍️ Products",
            f"{total_products:,}"
        )

        c5, c6, c7, c8 = st.columns(4)

        c5.metric(
            "💵 Average Order Value",
            f"₹{average_order_value:,.2f}"
        )

        c6.metric(
            "📈 Sales Growth",
            f"{growth_percentage:.2f}%"
        )

        c7.metric(
            "🏆 Top Product",
            str(top_product)
        )

        c8.metric(
            "🌍 Best Region",
            str(best_region)
        )

        # ----------------------------------------------------
        # MONTHLY SALES
        # ----------------------------------------------------

        st.subheader("📈 Monthly Sales Trend")

        monthly_dashboard = (
            dashboard_df
            .groupby(
                dashboard_df["sale_date"].dt.to_period("M")
            )["total_sales"]
            .sum()
            .reset_index()
        )

        monthly_dashboard["sale_date"] = (
            monthly_dashboard["sale_date"]
            .astype(str)
        )

        monthly_dashboard = monthly_dashboard.rename(
            columns={
                "sale_date": "Month",
                "total_sales": "Sales"
            }
        )

        st.line_chart(
            monthly_dashboard.set_index("Month")
        )

        # ----------------------------------------------------
        # TOP PRODUCTS
        # ----------------------------------------------------

        st.subheader("🏆 Top 5 Products")

        top5_products = (
            dashboard_df
            .groupby("product_name")["total_sales"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        top5_df = top5_products.reset_index()

        top5_df.columns = [
            "Product",
            "Revenue"
        ]

        st.dataframe(
            top5_df,
            width="stretch"
        )

        st.bar_chart(
            top5_products
        )

        # ----------------------------------------------------
        # CATEGORY PERFORMANCE
        # ----------------------------------------------------

        st.subheader("📊 Category Performance")

        category_dashboard = (
            dashboard_df
            .groupby("category")
            .agg(
                Revenue=("total_sales", "sum"),
                Quantity=("quantity", "sum")
            )
            .sort_values(
                "Revenue",
                ascending=False
            )
        )

        st.dataframe(
            category_dashboard,
            width="stretch"
        )

        st.bar_chart(
            category_dashboard["Revenue"]
        )

        # ----------------------------------------------------
        # REGION PERFORMANCE
        # ----------------------------------------------------

        st.subheader("🌍 Region Performance")

        region_dashboard = (
            dashboard_df
            .groupby("region")
            .agg(
                Revenue=("total_sales", "sum"),
                Quantity=("quantity", "sum")
            )
            .sort_values(
                "Revenue",
                ascending=False
            )
        )

        st.dataframe(
            region_dashboard,
            width="stretch"
        )

        st.bar_chart(
            region_dashboard["Revenue"]
        )

        # ----------------------------------------------------
        # AUTOMATIC INSIGHTS
        # ----------------------------------------------------

        st.subheader("💡 Automatic Business Insights")

        insight1 = (
            f"🏆 **Top Product:** {top_product}"
        )

        insight2 = (
            f"🌍 **Best Region:** {best_region}"
        )

        insight3 = (
            f"📈 **Sales Growth:** "
            f"{growth_percentage:.2f}%"
        )

        st.write(insight1)
        st.write(insight2)
        st.write(insight3)

        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        st.download_button(
            "📥 Download Dashboard Data",
            dashboard_df.to_csv(index=False),
            "executive_dashboard.csv",
            "text/csv"
        )


# ============================================================
# SALES ANALYSIS
# ============================================================

elif page == "Sales Analysis":

    st.title("📈 Sales Analysis")

    st.subheader("Product-wise Sales")

    product_sales = (
        df.groupby("product_name")["total_sales"]
        .sum()
        .sort_values(ascending=False)
    )

    st.dataframe(
        product_sales.reset_index(),
        width="stretch"
    )

    st.bar_chart(product_sales)

    st.subheader("🏆 Top 5 Products")

    st.dataframe(
        product_sales.head(5).reset_index(),
        width="stretch"
    )

    st.subheader("📊 Category-wise Sales")

    category_sales = (
        df.groupby("category")["total_sales"]
        .sum()
        .sort_values(ascending=False)
    )

    st.dataframe(
        category_sales.reset_index(),
        width="stretch"
    )

    st.bar_chart(category_sales)

    st.subheader("🌍 Region-wise Sales")

    region_sales = (
        df.groupby("region")["total_sales"]
        .sum()
        .sort_values(ascending=False)
    )

    st.dataframe(
        region_sales.reset_index(),
        width="stretch"
    )

    st.bar_chart(region_sales)

    st.subheader("📅 Monthly Sales")

    monthly_sales = (
        df.groupby("month")["total_sales"]
        .sum()
    )

    st.line_chart(monthly_sales)

    st.subheader("📈 Daily Sales Trend")

    daily_sales = (
        df.groupby("sale_date")["total_sales"]
        .sum()
    )

    st.line_chart(daily_sales)

    st.subheader("📆 Sales by Day of Week")

    weekday_sales = (
        df.groupby("day_of_week")["total_sales"]
        .sum()
    )

    st.bar_chart(weekday_sales)

    st.subheader("📊 Sales Performance Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    summary_col1.metric(
        "Total Revenue",
        f"₹{df['total_sales'].sum():,.2f}"
    )

    summary_col2.metric(
        "Average Sale",
        f"₹{df['total_sales'].mean():,.2f}"
    )

    summary_col3.metric(
        "Highest Sale",
        f"₹{df['total_sales'].max():,.2f}"
    )

    st.subheader("👥 Top 5 Customers")

    customer_sales = (
        df.groupby("customer_name")["total_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    st.dataframe(
        customer_sales.reset_index(),
        width="stretch"
    )

    st.subheader("🏆 Best Customer")

    if not customer_sales.empty:
        st.success(
            f"Best Customer: {customer_sales.index[0]}"
        )

    st.subheader("💰 Highest Single Sale")

    highest_sale = df.loc[
        df["total_sales"].idxmax()
    ]

    st.info(
        f"Product: {highest_sale['product_name']} | "
        f"Revenue: ₹{highest_sale['total_sales']:,.2f}"
    )

    st.subheader("🌍 Best Performing Region")

    if not region_sales.empty:

        st.success(
            f"Best Region: {region_sales.index[0]}"
        )

    st.subheader("📦 Quantity Sold by Product")

    quantity_product = (
        df.groupby("product_name")["quantity"]
        .sum()
        .sort_values(ascending=False)
    )

    st.dataframe(
        quantity_product.reset_index(),
        width="stretch"
    )

    st.subheader("💵 Average Price by Product")

    average_price = (
        df.groupby("product_name")["price"]
        .mean()
        .sort_values(ascending=False)
    )

    st.dataframe(
        average_price.reset_index(),
        width="stretch"
    )


# ============================================================
# ADVANCED PRODUCT INTELLIGENCE
# ============================================================

elif page == "Advanced Product Intelligence":

    st.title("🧠 Advanced Product Intelligence")

    st.write(
        "Use product-level analytics and AI-style rules "
        "to identify high-performing, weak and declining products."
    )

    # --------------------------------------------------------
    # PRODUCT SUMMARY
    # --------------------------------------------------------

    product_summary = (
        df.groupby("product_name")
        .agg(
            total_revenue=("total_sales", "sum"),
            total_quantity=("quantity", "sum"),
            average_price=("price", "mean"),
            total_orders=("sale_id", "nunique"),
            average_order_value=("total_sales", "mean"),
            first_sale=("sale_date", "min"),
            last_sale=("sale_date", "max")
        )
        .reset_index()
    )

    product_summary = product_summary.sort_values(
        "total_revenue",
        ascending=False
    )

    total_revenue_all_products = (
        product_summary["total_revenue"].sum()
    )

    if total_revenue_all_products > 0:

        product_summary["revenue_contribution"] = (
            product_summary["total_revenue"]
            / total_revenue_all_products
        ) * 100

    else:

        product_summary["revenue_contribution"] = 0

    # --------------------------------------------------------
    # PRODUCT RANK
    # --------------------------------------------------------

    product_summary["performance_rank"] = (
        product_summary["total_revenue"]
        .rank(
            ascending=False,
            method="dense"
        )
        .astype(int)
    )

    # --------------------------------------------------------
    # PRODUCT PERFORMANCE SCORE
    # --------------------------------------------------------

    max_revenue = product_summary["total_revenue"].max()

    max_quantity = product_summary["total_quantity"].max()

    if max_revenue > 0:
        revenue_score = (
            product_summary["total_revenue"]
            / max_revenue
        ) * 100
    else:
        revenue_score = 0

    if max_quantity > 0:
        quantity_score = (
            product_summary["total_quantity"]
            / max_quantity
        ) * 100
    else:
        quantity_score = 0

    product_summary["performance_score"] = (
        revenue_score * 0.70
        + quantity_score * 0.30
    )

    # --------------------------------------------------------
    # BEST AND WORST PRODUCTS
    # --------------------------------------------------------

    best_product = product_summary.iloc[0]

    worst_product = product_summary.iloc[-1]

    # --------------------------------------------------------
    # KPI SECTION
    # --------------------------------------------------------

    st.subheader("📌 Product Intelligence KPIs")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "🛍️ Total Products",
        f"{len(product_summary):,}"
    )

    k2.metric(
        "🏆 Best Product",
        str(best_product["product_name"])
    )

    k3.metric(
        "⚠️ Lowest Revenue Product",
        str(worst_product["product_name"])
    )

    k4.metric(
        "💰 Product Revenue",
        f"₹{total_revenue_all_products:,.2f}"
    )

    # --------------------------------------------------------
    # PRODUCT PERFORMANCE RANKING
    # --------------------------------------------------------

    st.subheader("🏆 Product Performance Ranking")

    ranking_display = product_summary[
        [
            "performance_rank",
            "product_name",
            "total_revenue",
            "total_quantity",
            "total_orders",
            "average_price",
            "revenue_contribution",
            "performance_score"
        ]
    ].copy()

    ranking_display.columns = [
        "Rank",
        "Product",
        "Revenue",
        "Quantity",
        "Orders",
        "Average Price",
        "Revenue Contribution %",
        "Performance Score"
    ]

    st.dataframe(
        ranking_display,
        width="stretch"
    )

    # --------------------------------------------------------
    # PRODUCT REVENUE CHART
    # --------------------------------------------------------

    st.subheader("💰 Revenue by Product")

    revenue_chart = (
        product_summary
        .set_index("product_name")[
            "total_revenue"
        ]
        .sort_values(ascending=False)
    )

    st.bar_chart(
        revenue_chart
    )

    # --------------------------------------------------------
    # REVENUE CONTRIBUTION
    # --------------------------------------------------------

    st.subheader("📊 Revenue Contribution by Product")

    contribution_chart = (
        product_summary
        .set_index("product_name")[
            "revenue_contribution"
        ]
        .sort_values(ascending=False)
    )

    st.bar_chart(
        contribution_chart
    )

    # --------------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------------

    st.subheader("🥇 Top 5 Products")

    top5_product_intelligence = (
        product_summary
        .head(5)
        [
            [
                "product_name",
                "total_revenue",
                "total_quantity",
                "revenue_contribution"
            ]
        ]
    )

    st.dataframe(
        top5_product_intelligence,
        width="stretch"
    )

    # --------------------------------------------------------
    # WORST PRODUCTS
    # --------------------------------------------------------

    st.subheader("⚠️ Bottom 5 Products")

    bottom5_products = (
        product_summary
        .sort_values(
            "total_revenue",
            ascending=True
        )
        .head(5)
        [
            [
                "product_name",
                "total_revenue",
                "total_quantity",
                "revenue_contribution"
            ]
        ]
    )

    st.dataframe(
        bottom5_products,
        width="stretch"
    )

    # --------------------------------------------------------
    # PRODUCT SALES TREND
    # --------------------------------------------------------

    st.subheader("📈 Product Sales Trends")

    product_list = sorted(
        df["product_name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if product_list:

        selected_product = st.selectbox(
            "Select a product",
            product_list
        )

        selected_product_df = df[
            df["product_name"] == selected_product
        ]

        product_daily_sales = (
            selected_product_df
            .groupby("sale_date")["total_sales"]
            .sum()
            .sort_index()
        )

        if not product_daily_sales.empty:

            st.line_chart(
                product_daily_sales
            )

            trend_col1, trend_col2, trend_col3 = st.columns(3)

            trend_col1.metric(
                "Product Revenue",
                f"₹{selected_product_df['total_sales'].sum():,.2f}"
            )

            trend_col2.metric(
                "Quantity Sold",
                f"{selected_product_df['quantity'].sum():,.0f}"
            )

            trend_col3.metric(
                "Average Price",
                f"₹{selected_product_df['price'].mean():,.2f}"
            )

    # --------------------------------------------------------
    # DECLINING SALES DETECTION
    # --------------------------------------------------------

    st.subheader("⚠️ Products With Declining Sales")

    declining_products = []

    for product in product_list:

        product_data = df[
            df["product_name"] == product
        ].copy()

        product_daily = (
            product_data
            .groupby("sale_date")["total_sales"]
            .sum()
            .sort_index()
        )

        if len(product_daily) >= 4:

            middle = len(product_daily) // 2

            first_period = (
                product_daily.iloc[:middle]
                .mean()
            )

            second_period = (
                product_daily.iloc[middle:]
                .mean()
            )

            if first_period > 0:

                change = (
                    (second_period - first_period)
                    / first_period
                ) * 100

                if change < -10:

                    declining_products.append(
                        {
                            "product_name": product,
                            "first_period_average": first_period,
                            "second_period_average": second_period,
                            "sales_change_percent": change
                        }
                    )

    if declining_products:

        declining_df = pd.DataFrame(
            declining_products
        ).sort_values(
            "sales_change_percent"
        )

        st.dataframe(
            declining_df,
            width="stretch"
        )

        st.warning(
            f"⚠️ {len(declining_df)} product(s) "
            "show a significant sales decline."
        )

    else:

        st.success(
            "✅ No significant product sales decline detected."
        )

    # --------------------------------------------------------
    # AI PRODUCT RECOMMENDATIONS
    # --------------------------------------------------------

    st.subheader("🤖 AI Product Recommendations")

    recommendations = []

    average_product_revenue = (
        product_summary["total_revenue"].mean()
    )

    average_product_quantity = (
        product_summary["total_quantity"].mean()
    )

    for _, row in product_summary.iterrows():

        product = row["product_name"]

        revenue = row["total_revenue"]

        quantity = row["total_quantity"]

        score = row["performance_score"]

        contribution = row["revenue_contribution"]

        if revenue >= average_product_revenue * 1.5:

            recommendations.append(
                {
                    "Product": product,
                    "Recommendation": (
                        "⭐ High-value product. "
                        "Consider increasing inventory "
                        "and promotional visibility."
                    ),
                    "Priority": "High"
                }
            )

        elif quantity >= average_product_quantity * 1.5:

            recommendations.append(
                {
                    "Product": product,
                    "Recommendation": (
                        "📦 High-demand product. "
                        "Monitor stock levels closely "
                        "to avoid stock-outs."
                    ),
                    "Priority": "High"
                }
            )

        elif contribution < 2:

            recommendations.append(
                {
                    "Product": product,
                    "Recommendation": (
                        "📉 Low revenue contribution. "
                        "Consider promotion, pricing review "
                        "or product positioning changes."
                    ),
                    "Priority": "Medium"
                }
            )

        elif score < 35:

            recommendations.append(
                {
                    "Product": product,
                    "Recommendation": (
                        "⚠️ Weak overall performance. "
                        "Review demand, pricing and marketing."
                    ),
                    "Priority": "Medium"
                }
            )

    if recommendations:

        recommendations_df = pd.DataFrame(
            recommendations
        )

        priority_order = {
            "High": 1,
            "Medium": 2
        }

        recommendations_df["priority_order"] = (
            recommendations_df["Priority"]
            .map(priority_order)
        )

        recommendations_df = (
            recommendations_df
            .sort_values("priority_order")
            .drop(columns=["priority_order"])
        )

        st.dataframe(
            recommendations_df,
            width="stretch"
        )

    else:

        st.success(
            "✅ No immediate product actions detected."
        )

    # --------------------------------------------------------
    # PRODUCT PERFORMANCE MATRIX
    # --------------------------------------------------------

    st.subheader("📊 Product Performance Matrix")

    matrix_df = product_summary[
        [
            "product_name",
            "total_revenue",
            "total_quantity",
            "performance_score"
        ]
    ].copy()

    matrix_df["Revenue Level"] = matrix_df[
        "total_revenue"
    ].apply(
        lambda x:
        "High"
        if x >= average_product_revenue
        else "Low"
    )

    matrix_df["Demand Level"] = matrix_df[
        "total_quantity"
    ].apply(
        lambda x:
        "High"
        if x >= average_product_quantity
        else "Low"
    )

    matrix_df["Strategy"] = matrix_df.apply(
        lambda row:
        (
            "🚀 Promote & Maintain"
            if row["Revenue Level"] == "High"
            and row["Demand Level"] == "High"
            else
            "📦 Improve Availability"
            if row["Revenue Level"] == "High"
            and row["Demand Level"] == "Low"
            else
            "📢 Increase Promotion"
            if row["Revenue Level"] == "Low"
            and row["Demand Level"] == "High"
            else
            "🔍 Review Product"
        ),
        axis=1
    )

    matrix_display = matrix_df[
        [
            "product_name",
            "total_revenue",
            "total_quantity",
            "performance_score",
            "Revenue Level",
            "Demand Level",
            "Strategy"
        ]
    ]

    st.dataframe(
        matrix_display,
        width="stretch"
    )

    # --------------------------------------------------------
    # BUSINESS INSIGHTS
    # --------------------------------------------------------

    st.subheader("💡 Product Business Insights")

    top_revenue_share = (
        product_summary
        .head(3)["revenue_contribution"]
        .sum()
    )

    st.info(
        f"🏆 The top 3 products contribute "
        f"approximately {top_revenue_share:.2f}% "
        "of total product revenue."
    )

    st.info(
        f"🥇 Best-performing product: "
        f"{best_product['product_name']} "
        f"with revenue of "
        f"₹{best_product['total_revenue']:,.2f}."
    )

    st.info(
        f"⚠️ Lowest-revenue product: "
        f"{worst_product['product_name']} "
        f"with revenue of "
        f"₹{worst_product['total_revenue']:,.2f}."
    )

    # --------------------------------------------------------
    # DOWNLOAD PRODUCT INTELLIGENCE
    # --------------------------------------------------------

    st.subheader("📥 Product Intelligence Report")

    download_df = product_summary.copy()

    st.download_button(
        "📥 Download Product Intelligence CSV",
        download_df.to_csv(index=False),
        "product_intelligence_report.csv",
        "text/csv"
    )


# ============================================================
# AI PREDICTION
# ============================================================

elif page == "AI Prediction":

    st.title("🤖 AI Sales Prediction")

    st.write(
        "Predict expected sales using Machine Learning."
    )

    prediction_df = df[
        [
            "quantity",
            "price",
            "total_sales"
        ]
    ].dropna()

    if len(prediction_df) < 2:

        st.warning(
            "⚠️ Not enough data for AI prediction."
        )

    else:

        X = prediction_df[
            [
                "quantity",
                "price"
            ]
        ]

        y = prediction_df[
            "total_sales"
        ]

        model = LinearRegression()

        model.fit(X, y)

        quantity_input = st.number_input(
            "Quantity",
            min_value=1.0,
            value=1.0
        )

        price_input = st.number_input(
            "Price",
            min_value=0.0,
            value=100.0
        )

        if st.button("🔮 Predict Sales"):

            prediction = model.predict(
                [[
                    quantity_input,
                    price_input
                ]]
            )[0]

            st.success(
                f"Predicted Sales: ₹{prediction:,.2f}"
            )

        st.subheader("📊 Model Information")

        st.write(
            f"Intercept: {model.intercept_:.2f}"
        )

        st.write(
            f"Quantity coefficient: "
            f"{model.coef_[0]:.2f}"
        )

        st.write(
            f"Price coefficient: "
            f"{model.coef_[1]:.2f}"
        )

        st.info(
            "The model uses quantity and price "
            "to estimate total sales."
        )


# ============================================================
# SALES FORECASTING
# ============================================================

elif page == "Sales Forecasting":

    st.title("📈 Sales Forecasting")

    daily_forecast = (
        df.groupby("sale_date")["total_sales"]
        .sum()
        .sort_index()
        .reset_index()
    )

    daily_forecast.columns = [
        "sale_date",
        "total_sales"
    ]

    if len(daily_forecast) < 5:

        st.warning(
            "⚠️ At least 5 sales days are recommended."
        )

    else:

        daily_forecast["day_number"] = range(
            len(daily_forecast)
        )

        X = daily_forecast[
            ["day_number"]
        ]

        y = daily_forecast[
            "total_sales"
        ]

        forecast_model = LinearRegression()

        forecast_model.fit(X, y)

        future_days = st.slider(
            "Forecast Days",
            min_value=1,
            max_value=365,
            value=30
        )

        last_day_number = (
            daily_forecast["day_number"].max()
        )

        future_numbers = range(
            last_day_number + 1,
            last_day_number + future_days + 1
        )

        future_predictions = (
            forecast_model.predict(
                pd.DataFrame(
                    {
                        "day_number":
                        list(future_numbers)
                    }
                )
            )
        )

        last_date = daily_forecast[
            "sale_date"
        ].max()

        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=future_days
        )

        forecast_df = pd.DataFrame(
            {
                "sale_date": future_dates,
                "forecast_sales":
                future_predictions
            }
        )

        forecast_df["forecast_sales"] = (
            forecast_df["forecast_sales"]
            .clip(lower=0)
        )

        total_forecast = (
            forecast_df["forecast_sales"].sum()
        )

        average_forecast = (
            forecast_df["forecast_sales"].mean()
        )

        highest_forecast = (
            forecast_df["forecast_sales"].max()
        )

        f1, f2, f3 = st.columns(3)

        f1.metric(
            "Total Forecast",
            f"₹{total_forecast:,.2f}"
        )

        f2.metric(
            "Average Daily Forecast",
            f"₹{average_forecast:,.2f}"
        )

        f3.metric(
            "Highest Forecast",
            f"₹{highest_forecast:,.2f}"
        )

        st.subheader("📈 Historical + Forecast")

        historical_chart = daily_forecast[
            [
                "sale_date",
                "total_sales"
            ]
        ].copy()

        historical_chart.columns = [
            "Date",
            "Sales"
        ]

        historical_chart = historical_chart.set_index(
            "Date"
        )

        forecast_chart = forecast_df[
            [
                "sale_date",
                "forecast_sales"
            ]
        ].copy()

        forecast_chart.columns = [
            "Date",
            "Sales"
        ]

        forecast_chart = forecast_chart.set_index(
            "Date"
        )

        combined_chart = pd.concat(
            [
                historical_chart,
                forecast_chart
            ]
        )

        st.line_chart(
            combined_chart
        )

        st.subheader("📋 Forecast Table")

        st.dataframe(
            forecast_df,
            width="stretch"
        )

        st.download_button(
            "📥 Download Forecast CSV",
            forecast_df.to_csv(index=False),
            "sales_forecast.csv",
            "text/csv"
        )


# ============================================================
# INVENTORY INTELLIGENCE
# ============================================================

elif page == "Inventory Intelligence":

    st.title("📦 Inventory Intelligence")

    st.write(
        "Monitor stock levels and identify products "
        "that may require restocking."
    )

    inventory_query = """
    SELECT
        product_name,
        stock_quantity,
        reorder_level,
        last_restock_date
    FROM inventory
    """

    try:

        inventory_df = pd.read_sql(
            inventory_query,
            connection
        )

    except Exception as e:

        st.error(
            "❌ Could not load inventory data."
        )

        st.error(e)

        connection.close()

        st.stop()

    if inventory_df.empty:

        st.warning(
            "⚠️ Inventory table contains no data."
        )

        connection.close()

        st.stop()

    # --------------------------------------------------------
    # AVERAGE DAILY SALES
    # --------------------------------------------------------

    days = (
        df["sale_date"]
        .dt.date
        .nunique()
    )

    if days == 0:
        days = 1

    avg_daily_sales = (
        df.groupby("product_name")["quantity"]
        .sum()
        / days
    )

    inventory_df["average_daily_sales"] = (
        inventory_df["product_name"]
        .map(avg_daily_sales)
        .fillna(0)
    )

    inventory_df["days_of_stock"] = (
        inventory_df["stock_quantity"]
        /
        inventory_df["average_daily_sales"]
        .replace(0, pd.NA)
    )

    def inventory_status(row):

        stock = row["stock_quantity"]

        reorder = row["reorder_level"]

        if stock <= 0:
            return "🚨 Out of Stock"

        elif stock <= reorder:
            return "🔴 Reorder Now"

        elif stock <= reorder * 2:
            return "🟠 Low Stock"

        else:
            return "🟢 Healthy"

    inventory_df["status"] = (
        inventory_df.apply(
            inventory_status,
            axis=1
        )
    )

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    i1, i2, i3, i4 = st.columns(4)

    i1.metric(
        "📦 Total Products",
        f"{len(inventory_df):,}"
    )

    i2.metric(
        "🚨 Out of Stock",
        f"{(inventory_df['status'] == '🚨 Out of Stock').sum():,}"
    )

    i3.metric(
        "🔴 Reorder Now",
        f"{(inventory_df['status'] == '🔴 Reorder Now').sum():,}"
    )

    i4.metric(
        "🟠 Low Stock",
        f"{(inventory_df['status'] == '🟠 Low Stock').sum():,}"
    )

    st.subheader("📋 Inventory Status")

    st.dataframe(
        inventory_df,
        width="stretch"
    )

    st.subheader("📊 Current Stock")

    stock_chart = (
        inventory_df
        .set_index("product_name")[
            "stock_quantity"
        ]
    )

    st.bar_chart(
        stock_chart
    )

    st.subheader("📅 Days of Stock Remaining")

    days_chart = (
        inventory_df
        .set_index("product_name")[
            "days_of_stock"
        ]
        .dropna()
    )

    st.bar_chart(
        days_chart
    )

    st.subheader("⚠️ Products Requiring Attention")

    attention_df = inventory_df[
        inventory_df["status"].isin(
            [
                "🚨 Out of Stock",
                "🔴 Reorder Now",
                "🟠 Low Stock"
            ]
        )
    ]

    if attention_df.empty:

        st.success(
            "✅ No immediate inventory issues."
        )

    else:

        st.dataframe(
            attention_df,
            width="stretch"
        )

    st.download_button(
        "📥 Download Inventory Report",
        inventory_df.to_csv(index=False),
        "inventory_intelligence.csv",
        "text/csv"
    )


# ============================================================
# CUSTOMER INTELLIGENCE
# ============================================================

elif page == "Customer Intelligence":

    st.title("👥 Customer Intelligence")

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

        customer_df = pd.read_sql(
            customer_query,
            connection
        )

    except Exception as e:

        st.error(
            "❌ Could not load customer intelligence."
        )

        st.error(e)

        connection.close()

        st.stop()

    if customer_df.empty:

        st.warning(
            "⚠️ No customer data available."
        )

    else:

        total_customers = (
            customer_df["customer_name"]
            .nunique()
        )

        total_customer_revenue = (
            customer_df["total_spent"].sum()
        )

        best_customer = (
            customer_df.iloc[0]["customer_name"]
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "👥 Total Customers",
            f"{total_customers:,}"
        )

        c2.metric(
            "💰 Customer Revenue",
            f"₹{total_customer_revenue:,.2f}"
        )

        c3.metric(
            "🏆 Best Customer",
            str(best_customer)
        )

        st.subheader("🏆 Top 5 Customers")

        top5_customers = customer_df.head(5)

        st.dataframe(
            top5_customers,
            width="stretch"
        )

        st.subheader("💰 Customer Spending")

        customer_chart = (
            customer_df
            .head(10)
            .set_index("customer_name")[
                "total_spent"
            ]
        )

        st.bar_chart(
            customer_chart
        )

        st.subheader("🔁 Repeat vs One-Time Customers")

        repeat_customers = (
            customer_df["total_orders"] > 1
        ).sum()

        one_time_customers = (
            customer_df["total_orders"] == 1
        ).sum()

        repeat_df = pd.DataFrame(
            {
                "Customer Type": [
                    "Repeat Customers",
                    "One-Time Customers"
                ],
                "Customers": [
                    repeat_customers,
                    one_time_customers
                ]
            }
        )

        st.dataframe(
            repeat_df,
            width="stretch"
        )

        st.bar_chart(
            repeat_df.set_index(
                "Customer Type"
            )
        )

        st.subheader("🎯 Customer Segmentation")

        def customer_segment(spent):

            if spent >= customer_df[
                "total_spent"
            ].quantile(0.75):

                return "High Value"

            elif spent >= customer_df[
                "total_spent"
            ].quantile(0.40):

                return "Medium Value"

            else:

                return "Low Value"

        customer_df["segment"] = (
            customer_df["total_spent"]
            .apply(customer_segment)
        )

        st.dataframe(
            customer_df,
            width="stretch"
        )

        st.subheader("💡 Customer Business Insights")

        high_value = (
            customer_df["segment"]
            == "High Value"
        ).sum()

        st.info(
            f"⭐ There are {high_value} high-value customers."
        )

        st.info(
            f"🔁 There are {repeat_customers} repeat customers."
        )

        st.download_button(
            "📥 Download Customer Intelligence CSV",
            customer_df.to_csv(index=False),
            "customer_intelligence.csv",
            "text/csv"
        )


# ============================================================
# AI INSIGHTS
# ============================================================

elif page == "🤖 AI Insights":

    st.title("🤖 AI Sales Insights")

    st.write(
        "AI-powered anomaly detection identifies "
        "unusual sales days."
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

    if len(daily_sales_ai) < 5:

        st.warning(
            "⚠️ At least 5 different sales days "
            "are recommended for AI anomaly detection."
        )

    else:

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

        daily_sales_ai["anomaly"] = (
            daily_sales_ai[
                "anomaly_prediction"
            ].apply(
                lambda x:
                "🚨 Anomaly"
                if x == -1
                else "✅ Normal"
            )
        )

        average_daily_sales_ai = (
            daily_sales_ai[
                "total_sales"
            ].mean()
        )

        high_anomalies = daily_sales_ai[
            (
                daily_sales_ai[
                    "anomaly_prediction"
                ] == -1
            )
            &
            (
                daily_sales_ai[
                    "total_sales"
                ] > average_daily_sales_ai
            )
        ]

        low_anomalies = daily_sales_ai[
            (
                daily_sales_ai[
                    "anomaly_prediction"
                ] == -1
            )
            &
            (
                daily_sales_ai[
                    "total_sales"
                ] < average_daily_sales_ai
            )
        ]

        a1, a2, a3 = st.columns(3)

        a1.metric(
            "📅 Total Sales Days",
            f"{len(daily_sales_ai):,}"
        )

        a2.metric(
            "🚨 Anomalous Days",
            f"{(daily_sales_ai['anomaly_prediction'] == -1).sum():,}"
        )

        a3.metric(
            "📊 Normal Days",
            f"{(daily_sales_ai['anomaly_prediction'] == 1).sum():,}"
        )

        st.subheader("🚀 High Sales Anomalies")

        if high_anomalies.empty:

            st.success(
                "No unusually high sales days detected."
            )

        else:

            st.dataframe(
                high_anomalies,
                width="stretch"
            )

        st.subheader("📉 Low Sales Anomalies")

        if low_anomalies.empty:

            st.success(
                "No unusually low sales days detected."
            )

        else:

            st.dataframe(
                low_anomalies,
                width="stretch"
            )

        st.subheader("📈 AI Sales Anomaly Chart")

        anomaly_chart = daily_sales_ai[
            [
                "sale_date",
                "total_sales"
            ]
        ].set_index(
            "sale_date"
        )

        st.line_chart(
            anomaly_chart
        )

        st.subheader("💡 AI Business Recommendations")

        if not high_anomalies.empty:

            st.success(
                "🚀 High-sales anomalies detected. "
                "Investigate promotions, seasonal demand "
                "or unusual customer activity."
            )

        if not low_anomalies.empty:

            st.warning(
                "📉 Low-sales anomalies detected. "
                "Review stock availability, pricing, "
                "customer demand and marketing activity."
            )

        if (
            high_anomalies.empty
            and low_anomalies.empty
        ):

            st.info(
                "✅ Sales are currently following "
                "a relatively normal pattern."
            )

        st.subheader("📋 Complete AI Anomaly Report")

        st.dataframe(
            daily_sales_ai,
            width="stretch"
        )

        st.download_button(
            "📥 Download AI Anomaly Report",
            daily_sales_ai.to_csv(index=False),
            "ai_sales_anomaly_report.csv",
            "text/csv"
        )


# ============================================================
# CLOSE CONNECTION
# ============================================================

if connection.is_connected():
    connection.close()