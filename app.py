"""
Sales Analytics — Business Intelligence Dashboard (Version 2)
Run: streamlit run app.py
"""

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
# CSS — high-contrast executive BI styling (light + dark readable)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 0.9rem;
            padding-bottom: 1rem;
            padding-left: 1.4rem;
            padding-right: 1.4rem;
            max-width: 1320px;
        }
        [data-testid="stSidebar"] { display: none; }

        .dash-title {
            margin: 0;
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            line-height: 1.1;
            color: #0F172A;
        }
        .dash-subtitle {
            margin: 0.2rem 0 0 0;
            font-size: 1.02rem;
            font-weight: 650;
            color: #1E293B;
        }
        .dash-support {
            margin: 0.2rem 0 0.55rem 0;
            font-size: 0.82rem;
            color: #475569;
        }

        /* Dark-mode readable header text */
        @media (prefers-color-scheme: dark) {
            .dash-title { color: #F8FAFC !important; }
            .dash-subtitle { color: #E2E8F0 !important; }
            .dash-support { color: #CBD5E1 !important; }
        }
        [data-theme="dark"] .dash-title,
        .stApp[data-theme="dark"] .dash-title { color: #F8FAFC !important; }
        [data-theme="dark"] .dash-subtitle,
        .stApp[data-theme="dark"] .dash-subtitle { color: #E2E8F0 !important; }
        [data-theme="dark"] .dash-support,
        .stApp[data-theme="dark"] .dash-support { color: #CBD5E1 !important; }

        .filter-panel {
            background: rgba(148, 163, 184, 0.12);
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 10px;
            padding: 0.45rem 0.55rem 0.2rem 0.55rem;
            margin-bottom: 0.65rem;
        }
        .filter-hint {
            font-size: 0.75rem;
            color: #64748B;
            margin: 0 0 0.15rem 0;
        }
        [data-theme="dark"] .filter-hint,
        .stApp[data-theme="dark"] .filter-hint { color: #94A3B8 !important; }

        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 4px solid #3B82F6;
            border-radius: 10px;
            padding: 0.8rem 0.95rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
            min-height: 92px;
        }
        .kpi-label {
            margin: 0;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #64748B;
        }
        .kpi-value {
            margin: 0.18rem 0 0.12rem 0;
            font-size: 1.6rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.05;
        }
        .kpi-desc {
            margin: 0;
            font-size: 0.74rem;
            color: #64748B;
        }

        .section-label {
            margin: 0.05rem 0 0.05rem 0;
            font-size: 0.95rem;
            font-weight: 700;
            color: #0F172A;
        }
        [data-theme="dark"] .section-label,
        .stApp[data-theme="dark"] .section-label { color: #F8FAFC !important; }

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
            margin-top: 0.75rem;
            padding-top: 0.55rem;
            border-top: 1px solid rgba(148, 163, 184, 0.35);
            text-align: center;
            font-size: 0.75rem;
            color: #64748B;
            line-height: 1.4;
        }
        [data-theme="dark"] .footer,
        .stApp[data-theme="dark"] .footer { color: #94A3B8 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
@st.cache_data
def load_sales_data(csv_path: str) -> tuple[pd.DataFrame, dict]:
    """Load sales.csv, validate rows, and return cleaned data + quality stats."""
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


def format_aov(value: float) -> str:
    return f"${value:,.0f}"


def kpi_card_html(label: str, value: str, description: str) -> str:
    return f"""
    <div class="kpi-card">
        <p class="kpi-label">{label}</p>
        <p class="kpi-value">{value}</p>
        <p class="kpi-desc">{description}</p>
    </div>
    """


def month_label(period_value) -> str:
    """Human month labels like 'Jan 2024' (no timestamps)."""
    period = pd.Period(period_value, freq="M")
    return period.strftime("%b %Y")


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


def build_insights(filtered_df: pd.DataFrame) -> list[str]:
    """Dynamic insights from filtered data only."""
    if filtered_df.empty:
        return ["No records match the current filters."]

    total_revenue = filtered_df["Sales"].sum()
    category_sales = filtered_df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    region_sales = filtered_df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    product_sales = filtered_df.groupby("Product")["Sales"].sum().sort_values(ascending=False)
    monthly = (
        filtered_df.groupby(filtered_df["OrderDate"].dt.to_period("M"))["Sales"]
        .sum()
        .sort_index()
    )
    best_month = pd.Period(monthly.idxmax(), freq="M").strftime("%B %Y")

    return [
        f"The selected view generated {format_currency(total_revenue)} in revenue.",
        f"{category_sales.index[0]} generated the highest revenue.",
        f"{region_sales.index[0]} generated the highest regional revenue.",
        f"{product_sales.index[0]} generated the highest product revenue.",
        f"{best_month} recorded the highest monthly revenue.",
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

# Default session state = ALL data
if "v2_dates" not in st.session_state:
    st.session_state.v2_dates = (min_date, max_date)
if "v2_region" not in st.session_state:
    st.session_state.v2_region = "All"
if "v2_category" not in st.session_state:
    st.session_state.v2_category = "All"
if "v2_product" not in st.session_state:
    st.session_state.v2_product = "All"

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<p class="dash-title">SALES ANALYTICS</p>', unsafe_allow_html=True)
st.markdown('<p class="dash-subtitle">Business Intelligence Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="dash-support">Revenue, customer, product and regional performance</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Compact filter bar — defaults to All / full date range
# ---------------------------------------------------------------------------
st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
st.markdown(
    '<p class="filter-hint">Filters default to all records. Choose values to refine the view.</p>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns([1.4, 1, 1, 1.15, 0.75], gap="small")

with c1:
    selected_dates = st.date_input(
        "Date Range",
        min_value=min_date,
        max_value=max_date,
        key="v2_dates",
    )
with c2:
    selected_region = st.selectbox(
        "Region",
        options=["All"] + regions,
        key="v2_region",
    )
with c3:
    selected_category = st.selectbox(
        "Category",
        options=["All"] + categories,
        key="v2_category",
    )
with c4:
    selected_product = st.selectbox(
        "Product",
        options=["All"] + products,
        key="v2_product",
    )
with c5:
    st.write("")
    if st.button("Reset", use_container_width=True):
        st.session_state.v2_dates = (min_date, max_date)
        st.session_state.v2_region = "All"
        st.session_state.v2_category = "All"
        st.session_state.v2_product = "All"
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
# KPI cards
# ---------------------------------------------------------------------------
total_revenue = float(filtered_df["Sales"].sum())
total_orders = int(filtered_df["OrderID"].nunique())
total_units = int(filtered_df["Quantity"].sum())
aov = total_revenue / total_orders if total_orders else 0.0

k1, k2, k3, k4 = st.columns(4, gap="small")
with k1:
    st.markdown(
        kpi_card_html(
            "Total Revenue",
            format_compact_currency(total_revenue),
            f"Exact: {format_currency(total_revenue)}",
        ),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        kpi_card_html("Total Orders", f"{total_orders:,}", "Unique order IDs"),
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        kpi_card_html("Units Sold", f"{total_units:,}", "Total quantity sold"),
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        kpi_card_html(
            "Average Order Value",
            format_aov(aov),
            f"Exact: {format_currency(aov)}",
        ),
        unsafe_allow_html=True,
    )

st.caption(f"Active view: **{len(filtered_df):,}** of **{len(df):,}** validated records")

# ---------------------------------------------------------------------------
# Row 1 — Revenue Trend + Sales by Category
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
    # Force categorical months so Plotly never shows timestamps / Dec 31
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
        hovertemplate=(
            "%{label}<br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
        ),
    )
    st.plotly_chart(chart_layout(fig_cat, height=310), width="stretch")

# ---------------------------------------------------------------------------
# Row 2 — Regional Performance + Top Products
# ---------------------------------------------------------------------------
r2c1, r2c2 = st.columns(2, gap="medium")

with r2c1:
    st.markdown('<p class="section-label">Regional Performance</p>', unsafe_allow_html=True)
    by_region = (
        filtered_df.groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=True)  # highest appears at top in barh
        .rename(columns={"Sales": "Revenue"})
    )
    fig_region = px.bar(
        by_region,
        x="Revenue",
        y="Region",
        orientation="h",
        text="Revenue",
        color_discrete_sequence=[ACCENT],
    )
    fig_region.update_traces(
        texttemplate="$%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="Region: %{y}<br>Revenue: $%{x:,.2f}<extra></extra>",
    )
    st.plotly_chart(chart_layout(fig_region, height=280), width="stretch")

with r2c2:
    st.markdown('<p class="section-label">Top 10 Products</p>', unsafe_allow_html=True)
    top_products = (
        filtered_df.groupby("Product", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
        .head(10)
        .rename(columns={"Sales": "Revenue"})
    )
    fig_products = px.bar(
        top_products.sort_values("Revenue", ascending=True),
        x="Revenue",
        y="Product",
        orientation="h",
        color_discrete_sequence=["#1E3A5F"],
    )
    fig_products.update_traces(
        hovertemplate="Product: %{y}<br>Revenue: $%{x:,.2f}<extra></extra>"
    )
    st.plotly_chart(chart_layout(fig_products, height=280), width="stretch")

# ---------------------------------------------------------------------------
# Row 3 — Top Customers + Business Insights
# ---------------------------------------------------------------------------
r3c1, r3c2 = st.columns(2, gap="medium")

with r3c1:
    st.markdown('<p class="section-label">Top 10 Customers</p>', unsafe_allow_html=True)
    top_customers = (
        filtered_df.groupby("CustomerName", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
        .head(10)
        .rename(columns={"Sales": "Revenue"})
    )
    fig_customers = px.bar(
        top_customers.sort_values("Revenue", ascending=True),
        x="Revenue",
        y="CustomerName",
        orientation="h",
        color_discrete_sequence=[ACCENT],
    )
    fig_customers.update_traces(
        hovertemplate="Customer: %{y}<br>Revenue: $%{x:,.2f}<extra></extra>"
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
# Bottom sections
# ---------------------------------------------------------------------------
with st.expander("Data Quality & Validation", expanded=False):
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Records", f"{len(filtered_df):,}")
    q2.metric("Missing Values", f"{int(filtered_df.isnull().sum().sum()):,}")
    q3.metric("Duplicate Rows", f"{int(filtered_df.duplicated().sum()):,}")
    q4.metric("Invalid Values", f"{source_quality['invalid_values']:,}")
    q5.metric(
        "Date Range",
        f"{filtered_df['OrderDate'].min().date()} → {filtered_df['OrderDate'].max().date()}",
    )
    st.caption(
        f"Source: {source_quality['source_records']:,} rows | "
        f"Missing: {source_quality['source_missing_values']:,} | "
        f"Duplicates: {source_quality['source_duplicate_rows']:,} | "
        f"Validated: {source_quality['validated_records']:,}"
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
