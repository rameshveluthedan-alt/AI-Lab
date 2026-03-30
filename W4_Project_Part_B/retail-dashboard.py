"""
Retail Transaction Insights Dashboard
=======================================
Requirements:
    pip install streamlit pandas plotly openpyxl

Run:
    streamlit run retail_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
import os

st.write(os.getcwd())          # shows current working directory
st.write(os.listdir("."))      # lists all files in that directory
warnings.filterwarnings("ignore")
DATA_FILE = "Retail_Transactions_Dataset.zip"  # local file path

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Transaction Insights",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# LIGHT THEME CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #f5f5f0;
}
[data-testid="stAppViewContainer"] { background: #f5f5f0; }
[data-testid="stHeader"] { background: transparent; }

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e0e0d8;
}

h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    color: #1a1a2e !important;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #c8761a;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.4rem 0;
    border-left: 3px solid #c8761a;
    padding-left: 10px;
}

.insight-box {
    background: #ffffff;
    border: 1px solid #e0e0d8;
    border-left: 3px solid #c8761a;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
    color: #333344;
    font-size: 0.92rem;
    line-height: 1.7;
}
.insight-box strong { color: #c8761a; }

[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e0e0d8;
    border-radius: 10px;
    padding: 16px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #c8761a !important;
    font-family: 'Syne', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY LIGHT THEME HELPER
# No yaxis key here — applied separately per chart to avoid conflicts
# ─────────────────────────────────────────────
def apply_layout(fig, title=""):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="DM Sans", color="#333344"),
        title=dict(text=title, font=dict(family="Syne", color="#1a1a2e", size=15)),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#ebebeb", zerolinecolor="#ebebeb"),
        yaxis=dict(gridcolor="#ebebeb", zerolinecolor="#ebebeb"),
    )
    return fig

ACCENT  = "#c8761a"
PALETTE = ["#c8761a", "#2a9d8f", "#e76f51", "#457b9d", "#6a4c93", "#e9c46a", "#264653"]

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading & preparing data…")
def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file, compression="infer")
    df["Date"] = pd.to_datetime(df["Date"], infer_datetime_format=True, errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    df["Year"]      = df["Date"].dt.year
    df["Month"]     = df["Date"].dt.month
    df["MonthName"] = df["Date"].dt.strftime("%b")
    df["DayOfWeek"] = df["Date"].dt.day_name()
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
    df["Total_Cost"]  = pd.to_numeric(df["Total_Cost"],  errors="coerce")
    df["Total_Items"] = pd.to_numeric(df["Total_Items"], errors="coerce")
    # Clean product list column — remove [ ] and quotes
    df["Product"] = df["Product"].str.replace(r"[\[\]']", "", regex=True)
    if df["Discount_Applied"].dtype == object:
        df["Discount_Applied"] = (
            df["Discount_Applied"].str.strip().str.lower()
            .map({"true": True, "false": False, "yes": True, "no": False, "1": True, "0": False})
            .fillna(False)
        )
    return df

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 Retail Insights")
    st.markdown("---")
    uploaded = st.file_uploader(
        "Upload dataset (CSV or ZIP)",
        type=["csv", "zip"],
    )

    if uploaded:
        df = load_data(uploaded)
    elif os.path.exists(DATA_FILE):
        df = load_data(DATA_FILE)   # auto-reads local zip
        st.markdown("### Filters")
        sel_seasons = st.multiselect("Season",            sorted(df["Season"].dropna().unique()),            default=sorted(df["Season"].dropna().unique()))
        sel_cities  = st.multiselect("City",              sorted(df["City"].dropna().unique()),              default=sorted(df["City"].dropna().unique()))
        sel_cats    = st.multiselect("Customer Category", sorted(df["Customer_Category"].dropna().unique()), default=sorted(df["Customer_Category"].dropna().unique()))
        sel_stores  = st.multiselect("Store Type",        sorted(df["Store_Type"].dropna().unique()),        default=sorted(df["Store_Type"].dropna().unique()))

        mask = (
            df["Season"].isin(sel_seasons) &
            df["City"].isin(sel_cities) &
            df["Customer_Category"].isin(sel_cats) &
            df["Store_Type"].isin(sel_stores)
        )
        dff = df[mask].copy()
        st.caption(f"**{len(dff):,}** transactions selected")
    else:
        df = dff = None
    

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("<h1 style='font-size:2rem; margin-bottom:0'>Retail Transaction Insights</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#888; margin-top:4px;'>Mini Project · Part B — Interactive Analytics Dashboard</p>", unsafe_allow_html=True)
st.markdown("---")
if dff is None:
    st.info("👈 Upload your dataset CSV using the sidebar to get started.")
    st.stop()
# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tabs = st.tabs(["📊 Overview", "👤 Customer Behaviour", "🎁 Promotions & Discounts", "🌦️ Seasonality", "📈 Dashboard", "💡 Key Insights"])

# ══════════════════════════════════════════════
# TAB 1 – OVERVIEW
# ══════════════════════════════════════════════
with tabs[0]:
    st.markdown("<div class='section-title'>Summary Metrics</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    def fmt(n):
        if n >= 1_000_000:
            return f"${n/1_000_000:.1f}M"
        elif n >= 1_000:
            return f"${n/1_000:.1f}K"
        return f"${n:,.0f}"
    
    def fmt_count(n):
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        elif n >= 1_000:
            return f"{n/1_000:.1f}K"
        return f"{n:,}"

    c1.metric("Total Transactions", fmt_count(len(dff)))
    c2.metric("Unique Customers",   fmt_count(dff['Customer_Name'].nunique()))
    c3.metric("Total Revenue",      fmt(dff['Total_Cost'].sum()))
    c4.metric("Avg Transaction",    fmt(dff['Total_Cost'].mean()))
    c5.metric("Avg Items / Txn",    f"{dff['Total_Items'].mean():.1f}")

    st.markdown("<div class='section-title'>Top 5 Most Common Products</div>", unsafe_allow_html=True)
    top_prods = (
    dff["Product"].dropna()
    .str.replace(r"[\[\]']", "", regex=True)  # remove [ ] and '
    .str.split(",")
    .explode()
    .str.strip()
    .value_counts()
    .head(5)
    .reset_index()
)
    top_prods.columns = ["Product", "Count"]
    fig = px.bar(top_prods, x="Count", y="Product", orientation="h",
                 color_discrete_sequence=[ACCENT], text="Count")
    fig.update_traces(textposition="outside")
    apply_layout(fig, "Top 5 Products by Frequency")
    fig.update_layout(yaxis=dict(autorange="reversed", gridcolor="#ebebeb"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>Cities with Highest Transactions</div>", unsafe_allow_html=True)
    city_txn = dff["City"].value_counts().reset_index()
    city_txn.columns = ["City", "Transactions"]
    fig = px.bar(city_txn, x="City", y="Transactions",
                 color="Transactions", color_continuous_scale=["#f0e6d3", ACCENT],
                 text="Transactions")
    fig.update_traces(textposition="outside")
    apply_layout(fig, "Transactions by City")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 – CUSTOMER BEHAVIOUR
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown("<div class='section-title'>Avg Spend by Customer Category</div>", unsafe_allow_html=True)
    avg_spend = dff.groupby("Customer_Category")["Total_Cost"].mean().sort_values(ascending=False).reset_index()
    avg_spend.columns = ["Category", "Avg Spend"]
    fig = px.bar(avg_spend, x="Category", y="Avg Spend",
                 color="Avg Spend", color_continuous_scale=["#f0e6d3", ACCENT],
                 text=avg_spend["Avg Spend"].map(lambda x: f"${x:,.0f}"))
    fig.update_traces(textposition="outside")
    apply_layout(fig, "Average Spend per Customer Category")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='section-title'>Payment Preference by Category</div>", unsafe_allow_html=True)
        pay_cat = dff.groupby(["Customer_Category", "Payment_Method"]).size().reset_index(name="Count")
        fig = px.bar(pay_cat, x="Customer_Category", y="Count", color="Payment_Method",
                     barmode="stack", color_discrete_sequence=PALETTE)
        apply_layout(fig, "Payment Method by Customer Category")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("<div class='section-title'>Avg Items per Store Type</div>", unsafe_allow_html=True)
        items_store = dff.groupby("Store_Type")["Total_Items"].mean().sort_values(ascending=False).reset_index()
        items_store.columns = ["Store Type", "Avg Items"]
        fig = px.bar(items_store, x="Store Type", y="Avg Items",
                     color_discrete_sequence=[PALETTE[1]],
                     text=items_store["Avg Items"].map(lambda x: f"{x:.1f}"))
        fig.update_traces(textposition="outside")
        apply_layout(fig, "Avg Items per Transaction by Store Type")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 – PROMOTIONS & DISCOUNTS
# ══════════════════════════════════════════════
with tabs[2]:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-title'>Avg Cost: Discount vs No Discount</div>", unsafe_allow_html=True)
        disc_avg = dff.groupby("Discount_Applied")["Total_Cost"].mean().reset_index()
        disc_avg["Discount_Applied"] = disc_avg["Discount_Applied"].map({True: "Discount", False: "No Discount"})
        disc_avg.columns = ["Discount", "Avg Cost"]
        fig = px.bar(disc_avg, x="Discount", y="Avg Cost",
                     color="Discount", color_discrete_sequence=[ACCENT, PALETTE[2]],
                     text=disc_avg["Avg Cost"].map(lambda x: f"${x:,.0f}"))
        fig.update_traces(textposition="outside")
        apply_layout(fig, "Avg Cost: Discount Applied?")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-title'>Avg Items by Promotion Type</div>", unsafe_allow_html=True)
        promo_items = dff.groupby("Promotion")["Total_Items"].mean().sort_values(ascending=False).reset_index()
        promo_items.columns = ["Promotion", "Avg Items"]
        fig = px.bar(promo_items, x="Promotion", y="Avg Items",
                     color_discrete_sequence=[PALETTE[3]],
                     text=promo_items["Avg Items"].map(lambda x: f"{x:.1f}"))
        fig.update_traces(textposition="outside")
        apply_layout(fig, "Avg Items per Promotion Type")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>Most Effective Promotion (by Avg Total Cost)</div>", unsafe_allow_html=True)
    promo_cost = dff.groupby("Promotion")["Total_Cost"].mean().sort_values(ascending=False).reset_index()
    promo_cost.columns = ["Promotion", "Avg Total Cost"]
    fig = px.bar(promo_cost, x="Promotion", y="Avg Total Cost",
                 color="Avg Total Cost", color_continuous_scale=["#f0e6d3", ACCENT],
                 text=promo_cost["Avg Total Cost"].map(lambda x: f"${x:,.0f}"))
    fig.update_traces(textposition="outside")
    apply_layout(fig, "Avg Total Cost by Promotion Type")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 – SEASONALITY
# ══════════════════════════════════════════════
with tabs[3]:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-title'>Total Revenue by Season</div>", unsafe_allow_html=True)
        season_rev = dff.groupby("Season")["Total_Cost"].sum().sort_values(ascending=False).reset_index()
        season_rev.columns = ["Season", "Total Revenue"]
        fig = px.bar(season_rev, x="Season", y="Total Revenue",
                     color="Season", color_discrete_sequence=PALETTE,
                     text=season_rev["Total Revenue"].map(lambda x: f"${x:,.0f}"))
        fig.update_traces(textposition="outside")
        apply_layout(fig, "Total Revenue by Season")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-title'>Avg Spending per Season</div>", unsafe_allow_html=True)
        season_avg = dff.groupby("Season")["Total_Cost"].mean().reset_index()
        season_avg.columns = ["Season", "Avg Spend"]
        season_order = ["Spring", "Summer", "Fall", "Winter"]
        season_avg["Season"] = pd.Categorical(season_avg["Season"], categories=season_order, ordered=True)
        season_avg = season_avg.sort_values("Season")
        fig = px.line(season_avg, x="Season", y="Avg Spend", markers=True,
                      color_discrete_sequence=[ACCENT],
                      text=season_avg["Avg Spend"].map(lambda x: f"${x:,.0f}"))
        fig.update_traces(textposition="top center", line=dict(width=3), marker=dict(size=10))
        apply_layout(fig, "Avg Spending per Season")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>Store Type Preference by Season</div>", unsafe_allow_html=True)
    season_store = dff.groupby(["Season", "Store_Type"]).size().reset_index(name="Transactions")
    fig = px.bar(season_store, x="Season", y="Transactions",
                 color="Store_Type", barmode="group", color_discrete_sequence=PALETTE)
    apply_layout(fig, "Transactions by Season and Store Type")
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 – DASHBOARD
# ══════════════════════════════════════════════
with tabs[4]:
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("<div class='section-title'>Transactions per City</div>", unsafe_allow_html=True)
        city_count = dff["City"].value_counts().reset_index()
        city_count.columns = ["City", "Transactions"]
        fig = px.bar(city_count, x="City", y="Transactions",
                     color="Transactions", color_continuous_scale=["#f0e6d3", ACCENT])
        apply_layout(fig, "Number of Transactions per City")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-title'>Payment Method Distribution</div>", unsafe_allow_html=True)
        pay_dist = dff["Payment_Method"].value_counts().reset_index()
        pay_dist.columns = ["Method", "Count"]
        fig = px.pie(pay_dist, values="Count", names="Method",
                     color_discrete_sequence=PALETTE, hole=0.4)
        apply_layout(fig, "Payment Method Share")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>Monthly Revenue Trend</div>", unsafe_allow_html=True)
    monthly = dff.groupby(["YearMonth", "Year"])["Total_Cost"].sum().reset_index().sort_values("YearMonth")
    fig = px.line(monthly, x="YearMonth", y="Total_Cost",
                  color="Year", color_discrete_sequence=PALETTE,
                  markers=True,
                  labels={"Total_Cost": "Total Revenue", "YearMonth": "Month"})
    fig.update_traces(line_width=2.5, marker_size=6)
    apply_layout(fig, "Monthly Revenue Trends")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>Revenue Heatmap: Season × Customer Category</div>", unsafe_allow_html=True)
    pivot = (
        dff.groupby(["Season", "Customer_Category"])["Total_Cost"]
        .sum().reset_index()
        .pivot(index="Season", columns="Customer_Category", values="Total_Cost")
        .fillna(0)
    )
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#fff3e0"], [0.5, "#e8a44a"], [1, ACCENT]],
        text=[[f"${v:,.0f}" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        showscale=True,
    ))
    apply_layout(fig, "Total Revenue by Season and Customer Category")
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 6 – KEY INSIGHTS
# ══════════════════════════════════════════════
with tabs[5]:
    st.markdown("<div class='section-title'>Automatically Generated Key Insights</div>", unsafe_allow_html=True)

    top_season     = dff.groupby("Season")["Total_Cost"].sum().idxmax()
    top_season_rev = dff.groupby("Season")["Total_Cost"].sum().max()
    top_cat        = dff.groupby("Customer_Category")["Total_Cost"].mean().idxmax()
    top_cat_val    = dff.groupby("Customer_Category")["Total_Cost"].mean().max()
    disc_yes       = dff[dff["Discount_Applied"] == True]["Total_Cost"].mean()
    disc_no        = dff[dff["Discount_Applied"] == False]["Total_Cost"].mean()
    disc_diff      = ((disc_yes - disc_no) / disc_no * 100) if disc_no else 0
    top_promo      = dff.groupby("Promotion")["Total_Cost"].mean().idxmax()
    top_promo_val  = dff.groupby("Promotion")["Total_Cost"].mean().max()
    top_city       = dff["City"].value_counts().idxmax()
    top_city_n     = dff["City"].value_counts().max()
    top_pay        = dff["Payment_Method"].value_counts().idxmax()
    top_pay_pct    = dff["Payment_Method"].value_counts(normalize=True).max() * 100

    insights = [
        f"<strong>Highest-Revenue Season:</strong> <strong>{top_season}</strong> generated the most total revenue (${top_season_rev:,.0f}), suggesting it is the peak shopping period.",
        f"<strong>Top-Spending Customer Category:</strong> <strong>{top_cat}</strong> customers spend the most on average (${top_cat_val:,.0f} per transaction).",
        f"<strong>Discount Impact:</strong> Transactions with discounts average ${disc_yes:,.0f} vs ${disc_no:,.0f} without — a <strong>{'positive' if disc_diff > 0 else 'negative'} {abs(disc_diff):.1f}% difference</strong>.",
        f"<strong>Most Effective Promotion:</strong> <strong>{top_promo}</strong> achieves the highest average transaction value (${top_promo_val:,.0f}).",
        f"<strong>Busiest City:</strong> <strong>{top_city}</strong> leads with <strong>{top_city_n:,}</strong> transactions.",
        f"<strong>Preferred Payment Method:</strong> <strong>{top_pay}</strong> accounts for <strong>{top_pay_pct:.1f}%</strong> of all transactions.",
    ]
    for insight in insights:
        st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Raw Data Preview</div>", unsafe_allow_html=True)
    st.dataframe(dff.head(100), use_container_width=True, height=350)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#aaa; font-size:0.8rem;'>"
    "Retail Transaction Insights · Graded Mini Project Part B · Built with Streamlit & Plotly"
    "</p>",
    unsafe_allow_html=True,
)
