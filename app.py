"""
Sales Analytics — Business Intelligence Dashboard (Version 3)
Run: streamlit run app.py
"""

from datetime import timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Sales Analytics | BI Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_PATH = PROJECT_ROOT / "data" / "sales.csv"

ACCENT = "#3B82F6"
CHART_COLORS = ["#1E3A5F", "#3B82F6", "#64748B", "#0EA5E9", "#334155", "#94A3B8"]

# ---------------------------------------------------------------------------
# CSS — clean professional BI styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Extra top padding so the main title is not clipped by Streamlit chrome */
        .block-container {
            padding-top: 2.6rem !important;
            padding-bottom: 1rem;
            padding-left: 1.4rem;
            padding-right: 1.4rem;
            max-width: 1320px;
            overflow: visible !important;
        }
        [data-testid="stSidebar"] { display: none; }

        /* Header: readable on dark theme by default; light-theme override below */
        .dash-title {
            margin: 0.15rem 0 0.35rem 0;
            padding-top: 0.15rem;
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            line-height: 1.3;
            overflow: visible;
            color: #F8FAFC !important;
        }
        .dash-subtitle {
            margin: 0.1rem 0 0.2rem 0;
            font-size: 1.0rem;
            font-weight: 650;
            line-height: 1.35;
            color: #E2E8F0 !important;
        }
        .dash-support {
            margin: 0.15rem 0 0.85rem 0;
            font-size: 0.84rem;
            line-height: 1.4;
            color: #CBD5E1 !important;
        }

        .filter-panel {
            background: rgba(148, 163, 184, 0.12);
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 10px;
            padding: 0.45rem 0.55rem 0.2rem 0.55rem;
            margin-bottom: 0.95rem;
        }
        .filter-hint {
            font-size: 0.75rem;
            color: #94A3B8 !important;
            margin: 0 0 0.15rem 0;
        }

        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 4px solid #3B82F6;
            border-radius: 10px;
            padding: 0.7rem 0.85rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
            min-height: 98px;
        }
        .kpi-label {
            margin: 0;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #64748B;
        }
        .kpi-value {
            margin: 0.16rem 0 0.1rem 0;
            font-size: 1.45rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.05;
        }
        .kpi-desc {
            margin: 0;
            font-size: 0.72rem;
            color: #64748B;
        }
        .kpi-up { color: #15803D; font-weight: 650; }
        .kpi-down { color: #B91C1C; font-weight: 650; }
        .kpi-flat { color: #64748B; font-weight: 650; }

        /* Section headings: light text for dark Streamlit theme readability */
        .section-label {
            display: block;
            margin: 0.55rem 0 0.35rem 0;
            font-size: 0.98rem;
            font-weight: 700;
            line-height: 1.35;
            color: #F1F5F9 !important;
        }

        .panel-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 0.75rem 0.85rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
            height: 320px;
            overflow-y: auto;
        }
        .insight-item {
            margin: 0 0 0.65rem 0;
            padding-left: 0.55rem;
            border-left: 3px solid #3B82F6;
            font-size: 0.86rem;
            line-height: 1.4;
            color: #1E293B;
        }

        .footer {
            margin-top: 0.85rem;
            padding-top: 0.55rem;
            border-top: 1px solid rgba(148, 163, 184, 0.35);
            text-align: center;
            font-size: 0.75rem;
            color: #94A3B8 !important;
            line-height: 1.4;
        }

        /* Light-theme overrides so desktop light mode stays readable */
        [data-theme="light"] .dash-title,
        .stApp[data-theme="light"] .dash-title { color: #0F172A !important; }
        [data-theme="light"] .dash-subtitle,
        .stApp[data-theme="light"] .dash-subtitle { color: #1E293B !important; }
        [data-theme="light"] .dash-support,
        .stApp[data-theme="light"] .dash-support { color: #475569 !important; }
        [data-theme="light"] .section-label,
        .stApp[data-theme="light"] .section-label { color: #0F172A !important; }
        [data-theme="light"] .filter-hint,
        .stApp[data-theme="light"] .filter-hint { color: #64748B !important; }
        [data-theme="light"] .footer,
        .stApp[data-theme="light"] .footer { color: #64748B !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
@st.cache_data
def load_sales_data(csv_path: str) -> tuple[pd.DataFrame, dict]:
    """Load and validate sales.csv."""
    raw_df = pd.read_csv(csv_path)
    work = raw_df.copy()
    work["OrderDate"] = pd.to_datetime(work["OrderDate"], errors="coerce")
    for col in ["Quantity", "UnitPrice", "Sales"]:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    invalid_mask = (
        work["OrderDate"].isna()
        | work["Quantity"].isna()
        | work["UnitPrice"].isna()
        | work["Sales"].isna()
        | (work["Quantity"] <= 0)
        | (work["UnitPrice"] <= 0)
        | (work["Sales"] <= 0)
    )

    quality = {
        "source_records": int(len(raw_df)),
        "source_missing_values": int(raw_df.isnull().sum().sum()),
        "source_duplicate_rows": int(raw_df.duplicated().sum()),
        "invalid_values": int(invalid_mask.sum()),
    }
    df = work.loc[~invalid_mask].copy()
    quality["validated_records"] = int(len(df))
    return df, quality


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_compact_currency(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 10_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def format_pct_change(change: float | None) -> str:
    if change is None:
        return ""
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%"


def month_label(period_value) -> str:
    return pd.Period(period_value, freq="M").strftime("%b %Y")


def chart_layout(fig: go.Figure, height: int = 300) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=8, r=8, t=18, b=8),
        font=dict(family="Arial, Helvetica, sans-serif", size=12, color="#1E293B"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        title=None,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title=None)
    fig.update_yaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False, title=None)
    return fig


def calc_pct_change(current: float, previous: float) -> float | None:
    """Return percent change, or None when comparison is unreliable."""
    if previous <= 0:
        return None
    return ((current - previous) / previous) * 100


def get_previous_period_df(
    source_df: pd.DataFrame,
    start_date,
    end_date,
    active_regions: list,
    active_categories: list,
    active_products: list,
) -> pd.DataFrame | None:
    """
    Build an equal-length previous period for comparison.
    Returns None when there is not enough overlapping historical data.
    """
    period_days = (end_date - start_date).days + 1
    if period_days <= 0:
        return None

    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days - 1)

    data_min = source_df["OrderDate"].min().date()
    data_max = source_df["OrderDate"].max().date()

    # Previous window must overlap available data
    if prev_end < data_min or prev_start > data_max:
        return None

    clipped_start = max(prev_start, data_min)
    clipped_end = min(prev_end, data_max)

    # If clipping removes most of the window, skip to avoid misleading deltas
    available_days = (clipped_end - clipped_start).days + 1
    if available_days < max(1, int(period_days * 0.5)):
        return None

    previous_df = source_df[
        source_df["Region"].isin(active_regions)
        & source_df["Category"].isin(active_categories)
        & source_df["Product"].isin(active_products)
        & (source_df["OrderDate"].dt.date >= clipped_start)
        & (source_df["OrderDate"].dt.date <= clipped_end)
    ].copy()

    if previous_df.empty:
        return None
    return previous_df


def kpi_card_html(label: str, value: str, description: str) -> str:
    return f"""
    <div class="kpi-card">
        <p class="kpi-label">{label}</p>
        <p class="kpi-value">{value}</p>
        <p class="kpi-desc">{description}</p>
    </div>
    """


def change_html(change: float | None, label: str = "vs prior period") -> str:
    if change is None:
        return "No prior-period comparison"
    css = "kpi-flat"
    if change > 0.05:
        css = "kpi-up"
    elif change < -0.05:
        css = "kpi-down"
    return f'{label}: <span class="{css}">{format_pct_change(change)}</span>'


def build_insights(filtered_df: pd.DataFrame) -> list[str]:
    """3–5 dynamic insights from the filtered dataframe."""
    if filtered_df.empty:
        return ["No records match the current filters."]

    total_revenue = filtered_df["Sales"].sum()
    total_orders = filtered_df["OrderID"].nunique()
    aov = total_revenue / total_orders if total_orders else 0.0

    category_sales = filtered_df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    region_sales = filtered_df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    product_sales = filtered_df.groupby("Product")["Sales"].sum().sort_values(ascending=False)
    customer_sales = (
        filtered_df.groupby("CustomerName")["Sales"].sum().sort_values(ascending=False)
    )

    top_category = category_sales.index[0]
    top_region = region_sales.index[0]
    top_product = product_sales.index[0]
    top_customer = customer_sales.index[0]
    region_share = (region_sales.iloc[0] / total_revenue * 100) if total_revenue else 0.0

    return [
        (
            f"Highest-revenue category is {top_category} "
            f"({format_currency(category_sales.iloc[0])})."
        ),
        (
            f"Highest-revenue region is {top_region} "
            f"({region_share:.1f}% of filtered revenue)."
        ),
        (
            f"Top-performing product is {top_product} "
            f"({format_currency(product_sales.iloc[0])})."
        ),
        f"Average order value is {format_currency(aov)}.",
        (
            f"Highest-value customer is {top_customer} "
            f"({format_currency(customer_sales.iloc[0])})."
        ),
    ]


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
if not CSV_PATH.exists():
    st.error(f"Missing data file: `{CSV_PATH}`")
    st.stop()

try:
    df, source_quality = load_sales_data(str(CSV_PATH))
except Exception as error:
    st.error(f"Unable to load sales data: {error}")
    st.stop()

if df.empty:
    st.warning("No valid sales records available after validation.")
    st.stop()

regions = sorted(df["Region"].dropna().unique().tolist())
categories = sorted(df["Category"].dropna().unique().tolist())
products = sorted(df["Product"].dropna().unique().tolist())
min_date = df["OrderDate"].min().date()
max_date = df["OrderDate"].max().date()

# Default filters = full dataset
if "v3_dates" not in st.session_state:
    st.session_state.v3_dates = (min_date, max_date)
if "v3_region" not in st.session_state:
    st.session_state.v3_region = "All"
if "v3_category" not in st.session_state:
    st.session_state.v3_category = "All"
if "v3_product" not in st.session_state:
    st.session_state.v3_product = "All"

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<p class="dash-title">Sales Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="dash-subtitle">Business Intelligence Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="dash-support">Interactive analysis of revenue, orders, customers, products, and regional performance.</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
st.markdown(
    '<p class="filter-hint">Defaults to all records. Use filters to refine the view.</p>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns([1.4, 1, 1, 1.15, 0.9], gap="small")

with c1:
    selected_dates = st.date_input(
        "Date Range",
        min_value=min_date,
        max_value=max_date,
        key="v3_dates",
    )
with c2:
    selected_region = st.selectbox("Region", options=["All"] + regions, key="v3_region")
with c3:
    selected_category = st.selectbox(
        "Category", options=["All"] + categories, key="v3_category"
    )
with c4:
    selected_product = st.selectbox(
        "Product", options=["All"] + products, key="v3_product"
    )
with c5:
    st.write("")
    if st.button("Reset Filters", use_container_width=True):
        st.session_state.v3_dates = (min_date, max_date)
        st.session_state.v3_region = "All"
        st.session_state.v3_category = "All"
        st.session_state.v3_product = "All"
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date, end_date = min_date, max_date

active_regions = regions if selected_region == "All" else [selected_region]
active_categories = categories if selected_category == "All" else [selected_category]
active_products = products if selected_product == "All" else [selected_product]

filtered_df = df[
    df["Region"].isin(active_regions)
    & df["Category"].isin(active_categories)
    & df["Product"].isin(active_products)
    & (df["OrderDate"].dt.date >= start_date)
    & (df["OrderDate"].dt.date <= end_date)
].copy()

if filtered_df.empty:
    st.warning("No records match the current filters.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------------------------
total_revenue = float(filtered_df["Sales"].sum())
total_orders = int(filtered_df["OrderID"].nunique())
total_units = int(filtered_df["Quantity"].sum())
aov = total_revenue / total_orders if total_orders else 0.0
avg_units_per_order = total_units / total_orders if total_orders else 0.0
num_customers = int(filtered_df["CustomerName"].nunique())

# Prior-period comparison (only when reliable)
previous_df = get_previous_period_df(
    df, start_date, end_date, active_regions, active_categories, active_products
)
revenue_change = None
orders_change = None
if previous_df is not None:
    prev_revenue = float(previous_df["Sales"].sum())
    prev_orders = int(previous_df["OrderID"].nunique())
    revenue_change = calc_pct_change(total_revenue, prev_revenue)
    orders_change = calc_pct_change(float(total_orders), float(prev_orders))

# ---------------------------------------------------------------------------
# KPI cards (6)
# ---------------------------------------------------------------------------
k1, k2, k3 = st.columns(3, gap="small")
with k1:
    st.markdown(
        kpi_card_html(
            "Total Revenue",
            format_compact_currency(total_revenue),
            change_html(revenue_change),
        ),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        kpi_card_html(
            "Total Orders",
            f"{total_orders:,}",
            change_html(orders_change),
        ),
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        kpi_card_html("Units Sold", f"{total_units:,}", "Total quantity sold"),
        unsafe_allow_html=True,
    )

k4, k5, k6 = st.columns(3, gap="small")
with k4:
    st.markdown(
        kpi_card_html(
            "Average Order Value",
            f"${aov:,.0f}",
            f"Exact: {format_currency(aov)}",
        ),
        unsafe_allow_html=True,
    )
with k5:
    st.markdown(
        kpi_card_html(
            "Avg Units per Order",
            f"{avg_units_per_order:.2f}",
            "Quantity / orders",
        ),
        unsafe_allow_html=True,
    )
with k6:
    st.markdown(
        kpi_card_html(
            "Number of Customers",
            f"{num_customers:,}",
            "Unique customers",
        ),
        unsafe_allow_html=True,
    )

st.caption(f"Active view: **{len(filtered_df):,}** of **{len(df):,}** validated records")

# ---------------------------------------------------------------------------
# Row 1 — Revenue Trend + Category
# ---------------------------------------------------------------------------
r1c1, r1c2 = st.columns([1.55, 1], gap="medium")

with r1c1:
    st.markdown('<p class="section-label">Revenue Trend</p>', unsafe_allow_html=True)
    monthly = (
        filtered_df.groupby(filtered_df["OrderDate"].dt.to_period("M"))["Sales"]
        .sum()
        .sort_index()
    )
    month_labels = [month_label(idx) for idx in monthly.index]
    month_values = monthly.values.tolist()

    fig_trend = go.Figure()
    fig_trend.add_trace(
        go.Scatter(
            x=month_labels,
            y=month_values,
            mode="lines+markers",
            fill="tozeroy",
            line=dict(color=ACCENT, width=2.6),
            marker=dict(size=7, color="#1E3A5F"),
            hovertemplate="Month: %{x}<br>Revenue: $%{y:,.2f}<extra></extra>",
        )
    )
    fig_trend.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=month_labels,
        tickangle=0,
    )
    fig_trend.update_yaxes(tickprefix="$", separatethousands=True)
    st.plotly_chart(chart_layout(fig_trend, height=310), width="stretch")

with r1c2:
    st.markdown('<p class="section-label">Sales by Category</p>', unsafe_allow_html=True)
    by_category = (
        filtered_df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
        .rename(columns={"Sales": "Revenue"})
    )
    by_category["Share"] = (
        by_category["Revenue"] / by_category["Revenue"].sum() * 100
        if by_category["Revenue"].sum()
        else 0
    )
    fig_cat = px.pie(
        by_category,
        names="Category",
        values="Revenue",
        hole=0.58,
        color_discrete_sequence=CHART_COLORS,
    )
    fig_cat.update_traces(
        textposition="outside",
        textinfo="label+percent",
        customdata=by_category[["Share"]],
        hovertemplate=(
            "%{label}<br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
        ),
    )
    st.plotly_chart(chart_layout(fig_cat, height=310), width="stretch")

# ---------------------------------------------------------------------------
# Row 2 — Regional + Top Products
# ---------------------------------------------------------------------------
r2c1, r2c2 = st.columns(2, gap="medium")

with r2c1:
    st.markdown('<p class="section-label">Regional Performance</p>', unsafe_allow_html=True)
    by_region = (
        filtered_df.groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=True)
        .rename(columns={"Sales": "Revenue"})
    )
    region_total = by_region["Revenue"].sum()
    by_region["Share"] = (
        by_region["Revenue"] / region_total * 100 if region_total else 0
    )
    fig_region = px.bar(
        by_region,
        x="Revenue",
        y="Region",
        orientation="h",
        text="Revenue",
        color_discrete_sequence=[ACCENT],
        custom_data=["Share"],
    )
    fig_region.update_traces(
        texttemplate="$%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "Region: %{y}<br>Revenue: $%{x:,.2f}<br>Share: %{customdata[0]:.1f}%<extra></extra>"
        ),
    )
    st.plotly_chart(chart_layout(fig_region, height=280), width="stretch")

with r2c2:
    st.markdown('<p class="section-label">Top 10 Products</p>', unsafe_allow_html=True)
    top_products = (
        filtered_df.groupby("Product", as_index=False)
        .agg(Revenue=("Sales", "sum"), Units=("Quantity", "sum"))
        .sort_values("Revenue", ascending=False)
        .head(10)
    )
    fig_products = px.bar(
        top_products.sort_values("Revenue", ascending=True),
        x="Revenue",
        y="Product",
        orientation="h",
        color_discrete_sequence=["#1E3A5F"],
        custom_data=["Units"],
    )
    fig_products.update_traces(
        hovertemplate=(
            "Product: %{y}<br>Revenue: $%{x:,.2f}<br>Units Sold: %{customdata[0]:,}<extra></extra>"
        )
    )
    st.plotly_chart(chart_layout(fig_products, height=280), width="stretch")

# ---------------------------------------------------------------------------
# Row 3 — Top Customers + Insights
# ---------------------------------------------------------------------------
r3c1, r3c2 = st.columns(2, gap="medium")

with r3c1:
    st.markdown('<p class="section-label">Top 10 Customers</p>', unsafe_allow_html=True)
    top_customers = (
        filtered_df.groupby("CustomerName", as_index=False)
        .agg(Revenue=("Sales", "sum"), Orders=("OrderID", "nunique"))
        .sort_values("Revenue", ascending=False)
        .head(10)
    )
    fig_customers = px.bar(
        top_customers.sort_values("Revenue", ascending=True),
        x="Revenue",
        y="CustomerName",
        orientation="h",
        color_discrete_sequence=[ACCENT],
        custom_data=["Orders"],
    )
    fig_customers.update_traces(
        hovertemplate=(
            "Customer: %{y}<br>Revenue: $%{x:,.2f}<br>Orders: %{customdata[0]:,}<extra></extra>"
        )
    )
    st.plotly_chart(chart_layout(fig_customers, height=320), width="stretch")

with r3c2:
    st.markdown('<p class="section-label">Business Insights</p>', unsafe_allow_html=True)
    insight_html = '<div class="panel-card">'
    for item in build_insights(filtered_df):
        insight_html += f'<p class="insight-item">{item}</p>'
    insight_html += "</div>"
    st.markdown(insight_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Download filtered data
# ---------------------------------------------------------------------------
st.download_button(
    label="Download Filtered Data",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_sales.csv",
    mime="text/csv",
    use_container_width=False,
)

# ---------------------------------------------------------------------------
# Data Quality + Explore Data
# ---------------------------------------------------------------------------
with st.expander("Data Quality & Validation", expanded=False):
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Records", f"{len(filtered_df):,}")
    q2.metric("Missing Values", f"{int(filtered_df.isnull().sum().sum()):,}")
    q3.metric("Duplicate Rows", f"{int(filtered_df.duplicated().sum()):,}")
    q4.metric(
        "Date Range",
        f"{filtered_df['OrderDate'].min().date()} → {filtered_df['OrderDate'].max().date()}",
    )
    st.caption(
        f"Source: {source_quality['source_records']:,} rows | "
        f"Missing: {source_quality['source_missing_values']:,} | "
        f"Duplicates: {source_quality['source_duplicate_rows']:,} | "
        f"Invalid values removed: {source_quality['invalid_values']:,}"
    )

with st.expander("Explore Data", expanded=False):
    st.dataframe(
        filtered_df.sort_values("OrderDate").reset_index(drop=True),
        width="stretch",
        hide_index=True,
        height=300,
    )

st.markdown(
    """
    <div class="footer">
        Built by Gopi Krishna<br>
        M.S. Computer Science | University of North Texas
    </div>
    """,
    unsafe_allow_html=True,
)
