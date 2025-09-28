"""
Streamlit Dashboard for Sales Insights

This app provides interactive filters, KPIs, and charts based on the
existing SalesAnalyzer logic in `sales_analysis.py`.
"""

import os
from datetime import datetime
from typing import Tuple, List

import pandas as pd
import streamlit as st
import plotly.express as px

from sales_analysis import SalesAnalyzer


# ----------------------------
# Data Loading and Caching
# ----------------------------
@st.cache_data(show_spinner=True)
def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """Load data via SalesAnalyzer and return cleaned DataFrame.

    If the CSV does not exist, SalesAnalyzer will create a sample dataset.
    """
    analyzer = SalesAnalyzer(csv_path)
    analyzer.load_data()
    analyzer.clean_data()
    return analyzer.clean_df.copy()


def apply_filters(
    df: pd.DataFrame,
    date_range: Tuple[pd.Timestamp, pd.Timestamp],
    regions: List[str],
    categories: List[str],
) -> pd.DataFrame:
    """Filter dataframe by date range, regions, and categories."""
    start_date, end_date = date_range

    filtered = df[
        (df["OrderDate"] >= pd.to_datetime(start_date)) &
        (df["OrderDate"] <= pd.to_datetime(end_date))
    ]

    if regions:
        filtered = filtered[filtered["Region"].isin(regions)]

    if categories:
        filtered = filtered[filtered["Category"].isin(categories)]

    return filtered


def render_kpis(df: pd.DataFrame) -> None:
    """Render KPI metrics from a filtered dataframe."""
    total_sales = float(df["Sales"].sum()) if not df.empty else 0.0
    total_profit = float(df["Profit"].sum()) if not df.empty else 0.0
    total_orders = int(len(df))
    total_quantity = int(df["Quantity"].sum()) if not df.empty else 0
    aov = (total_sales / total_orders) if total_orders > 0 else 0.0
    margin = ((total_profit / total_sales) * 100.0) if total_sales > 0 else 0.0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Sales", f"Rs {total_sales:,.0f}")
    col2.metric("Total Profit", f"Rs {total_profit:,.0f}")
    col3.metric("Orders", f"{total_orders}")
    col4.metric("Quantity", f"{total_quantity}")
    col5.metric("Average Order Value", f"Rs {aov:,.0f}")
    col6.metric("Profit Margin", f"{margin:.1f}%")


def render_top_products(df: pd.DataFrame, top_n: int = 10) -> None:
    if df.empty:
        st.info("No data for selected filters.")
        return
    grouped = (
        df.groupby("ProductName", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
        .sort_values("Sales", ascending=False)
        .head(top_n)
    )
    fig = px.bar(
        grouped,
        x="ProductName",
        y="Sales",
        hover_data=["Profit", "Quantity"],
        title=f"Top {top_n} Products by Sales",
        labels={"Sales": "Sales (Rs)", "ProductName": "Product"},
    )
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)


def render_top_customers(df: pd.DataFrame, top_n: int = 10) -> None:
    if df.empty:
        st.info("No data for selected filters.")
        return
    grouped = (
        df.groupby("CustomerName", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("OrderID", "count"))
        .sort_values("Sales", ascending=False)
        .head(top_n)
    )
    fig = px.bar(
        grouped,
        x="CustomerName",
        y="Sales",
        hover_data=["Profit", "Orders"],
        title=f"Top {top_n} Customers by Sales",
        labels={"Sales": "Sales (Rs)", "CustomerName": "Customer"},
        color="Sales",
        color_continuous_scale="Blues",
    )
    fig.update_layout(xaxis_tickangle=-30, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)


def render_region_category(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No data for selected filters.")
        return
    col1, col2 = st.columns(2)

    with col1:
        by_region = df.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        fig_region = px.pie(
            by_region,
            names="Region",
            values="Sales",
            hole=0.4,
            title="Sales by Region",
        )
        st.plotly_chart(fig_region, use_container_width=True)

    with col2:
        by_cat = df.groupby("Category", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        fig_cat = px.pie(
            by_cat,
            names="Category",
            values="Sales",
            hole=0.4,
            title="Sales by Category",
        )
        st.plotly_chart(fig_cat, use_container_width=True)


def render_monthly_trend(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No data for selected filters.")
        return
    trend = (
        df.groupby(["Year", "Month", "MonthName"], as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values(["Year", "Month"])
    )
    trend["MonthLabel"] = trend["MonthName"] + " " + trend["Year"].astype(str)
    fig = px.line(
        trend,
        x="MonthLabel",
        y="Sales",
        markers=True,
        title="Monthly Sales Trend",
        labels={"Sales": "Sales (Rs)", "MonthLabel": "Month"},
    )
    fig.update_traces(mode="lines+markers")
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Sales Insights Dashboard", layout="wide")
    st.title("Sales Insights Dashboard")
    st.caption("Interactive dashboard with filters, KPIs, and charts")

    # Sidebar: Data source and filters
    st.sidebar.header("Filters")
    data_path = st.sidebar.text_input("Data CSV Path", value="data/sales_data.csv")

    # Load and prepare data
    df = load_and_prepare_data(data_path)

    # Ensure correct dtypes
    if not pd.api.types.is_datetime64_any_dtype(df["OrderDate"]):
        df["OrderDate"] = pd.to_datetime(df["OrderDate"])

    # Filter controls
    min_date = pd.to_datetime(df["OrderDate"].min())
    max_date = pd.to_datetime(df["OrderDate"].max())
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )
    # Normalize tuple of dates
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
    else:
        start, end = (min_date.date(), max_date.date())

    regions = sorted(df["Region"].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect("Region", options=regions, default=regions)

    categories = sorted(df["Category"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect("Category", options=categories, default=categories)

    # Apply filters
    filtered_df = apply_filters(df, (pd.to_datetime(start), pd.to_datetime(end)), selected_regions, selected_categories)

    # KPIs
    st.subheader("KPIs")
    render_kpis(filtered_df)

    # Charts
    st.subheader("Top Performers")
    render_top_products(filtered_df, top_n=10)
    render_top_customers(filtered_df, top_n=10)

    st.subheader("Distribution")
    render_region_category(filtered_df)

    st.subheader("Trends")
    render_monthly_trend(filtered_df)


if __name__ == "__main__":
    main()


#to execute-# streamlit run sales_dashboard.py