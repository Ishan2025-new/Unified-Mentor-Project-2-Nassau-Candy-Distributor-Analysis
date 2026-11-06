import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# 1. PAGE CONFIGURATION AND CUSTOM STYLING
st.set_page_config(
    page_title="Nassau Candy -- Profitability Analytics",
    page_icon=":candy:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished visual aesthetics
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: White;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .stMetric label {
        font-weight: 600 !important;
        color: White !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. DATA LOADING AND FALLBACK DATA GENERATOR
@st.cache_data
def load_data():
    """
    Load Preprocessed Dataset. If missing, runs embedded fallback generator.
    """
    processed_path = "data/processed/nassau_candy_processed.csv"
    if os.path.exists(processed_path):
        df = pd.read_csv(processed_path)

        # Normalize common source column names to the names used by the dashboard.
        normalized_columns = {
            str(column).strip().lower().replace('_', ' ').replace('-', ' '): column
            for column in df.columns
        }
        customer_column = normalized_columns.get('customer name')
        if customer_column is None:
            customer_column = normalized_columns.get('customer')
        if customer_column is not None and customer_column != 'Customer Name':
            df = df.rename(columns={customer_column: 'Customer Name'})

        # Handle missing customer columns without crashing downstream metrics.
        if 'Customer Name' not in df.columns:
            for candidate in ('Customer ID', 'CustomerId', 'Customer ID'):
                if candidate in df.columns:
                    df = df.rename(columns={candidate: 'Customer Name'})
                    break
            else:
                df['Customer Name'] = 'Unknown Customer'

        order_date_column = normalized_columns.get('order date')
        if order_date_column is not None and order_date_column != 'Order Date':
            df = df.rename(columns={order_date_column: 'Order Date'})
        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        return df

    # Fallback Generator matching Nassau Candy Specs
    np.random.seed(42)
    records = 10194

    products = [
        {"name": "Wonka Bar - Scrumdiddlyumptious", "division": "Chocolate", "factory": "Lot's O' Nuts", 
            "sales_share": 0.196, "target_margin": 0.694},
        {"name": "Wonka Bar - Triple Dazzle Caramel", "division": "Chocolate", "factory": "Wicked Choccy's", 
            "sales_share": 0.200, "target_margin": 0.653},
        {"name": "Wonka Bar - Milk Chocolate", "division": "Chocolate", "factory": "Wicked Choccy's", 
            "sales_share": 0.189, "target_margin": 0.649},
        {"name": "Wonka Bar - Nutty Crunch Surprise", "division": "Chocolate", "factory": "Lot's O' Nuts", 
            "sales_share": 0.166, "target_margin": 0.713},
        {"name": "Wonka Bar - Fudge Mallows", "division": "Chocolate", "factory": "Lot's O' Nuts", 
            "sales_share": 0.175, "target_margin": 0.667},
        {"name": "Lickable Wallpaper", "division": "Other", "factory": "The Other Factory", 
            "sales_share": 0.055, "target_margin": 0.500},
        {"name": "Wonka Gum", "division": "Other", "factory": "The Other Factory", 
            "sales_share": 0.004, "target_margin": 0.520},
        {"name": "Kazookles", "division": "Other", "factory": "The Other Factory", 
            "sales_share": 0.008, "target_margin": 0.077},
        {"name": "Everlasting Gobstopper", "division": "Sugar", "factory": "Sugar Shack", 
            "sales_share": 0.001, "target_margin": 0.800},
        {"name": "Hair Toffee", "division": "Sugar", "factory": "Sugar Shack", 
            "sales_share": 0.001, "target_margin": 0.778},
        {"name": "Fizzy Lifting Drinks", "division": "Sugar", "factory": "Sugar Shack", 
            "sales_share": 0.001, "target_margin": 0.600},
        {"name": "Laffy Taffy", "division": "Sugar", "factory": "Secret Factory", 
            "sales_share": 0.001, "target_margin": 0.250},
        {"name": "SweeTARTS", "division": "Sugar", "factory": "Secret Factory", 
            "sales_share": 0.001, "target_margin": 0.200},
        {"name": "Nerds", "division": "Sugar", "factory": "Secret Factory", 
            "sales_share": 0.001, "target_margin": 0.150},
        {"name": "Fun Dip", "division": "Sugar", "factory": "Secret Factory", 
            "sales_share": 0.001, "target_margin": 0.100},
    ]

    regions = ['Atlantic', 'Interior', 'Pacific', 'Gulf']
    ship_modes = ['Standard', 'First Class', 'Second Class', 'Same Day']

    data = []
    prod_indices = np.random.choice(len(products), p=[p['sales_share'] for p in products], size=records)

    dates = pd.date_range(start='2024-01-01', end='2025-12-31', periods=records)

    for idx, p_idx in enumerate(prod_indices):
        prod = products[p_idx]
        qty = np.random.randint(1, 20)
        base_unit_price = np.random.uniform(5.0, 25.0)
        sales = round(qty * base_unit_price, 2)
        margin = prod['target_margin'] + np.random.uniform(-0.02, 0.02)
        cost = round(sales * (1 - margin), 2)

        data.append({
            'Order ID': f'ORD-{10000 + idx}',
            'Order Date': dates[idx].strftime('%Y-%m-%d'),
            'Customer Name': f'Customer_{np.random.randint(1000, 6044)}',
            'Region': np.random.choice(regions),
            'Ship Mode': np.random.choice(ship_modes),
            'Product Division': prod['division'],
            'Factory': prod['factory'],
            'Product Name': prod['name'],
            'Quantity': qty,
            'Sales': sales,
            'Cost': cost,
            'Gross Profit': sales - cost,
            'Gross Margin %': ((sales - cost) / sales) * 100 if sales > 0 else 0,
            'Risk Flag': 'High Risk :red_circle:' if (((sales - cost) / sales) * 100) < 35.0 else 'Healthy :green_circle:'
        })

    return pd.DataFrame(data)

df_raw = load_data()

# 3. SIDEBAR FILTERS
st.sidebar.image("https://img.icons8.com/color/96/candy.png", width=70)
st.sidebar.title("Filter Controls")

# Division Filter
divisions = ['All'] + list(df_raw['Product Division'].unique())
selected_division = st.sidebar.selectbox("Select Division", divisions)

# Region Filter
regions = ['All'] + list(df_raw['Region'].unique())
selected_region = st.sidebar.selectbox("Select Region", regions)

# Factory Filter
factories = ['All'] + list(df_raw['Factory'].unique())
selected_factory = st.sidebar.selectbox("Select Factory", factories)

# Apply Filters
df = df_raw.copy()
if selected_division != 'All':
    df = df[df['Product Division'] == selected_division]
if selected_region != 'All':
    df = df[df['Region'] == selected_region]
if selected_factory != 'All':
    df = df[df['Factory'] == selected_factory]

# Sidebar Metadata Summary
st.sidebar.markdown("---")
st.sidebar.markdown("### Executive Summary")
st.sidebar.metric("Filtered Records", f"{len(df):,}")
st.sidebar.metric("Unique Customers", f"{df['Customer Name'].nunique():,}")

# 4. DASHBOARD HEADER & KPI METRICS
st.markdown('<div class="main-title">🍬 Nassau Candy Distributor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Product Line Profitability and Margin Performance Dashboard</div>', 
            unsafe_allow_html=True)

# Executive KPI Cards
tot_sales = df['Sales'].sum()
tot_cost = df['Cost'].sum()
tot_profit = df['Gross Profit'].sum()
agg_margin = (tot_profit / tot_sales * 100) if tot_sales > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${tot_sales:,.2f}")
col2.metric("Cost Base (COGS)", f"${tot_cost:,.2f}")
col3.metric("Gross Profit", f"${tot_profit:,.2f}")
col4.metric("Aggregate Margin", f"{agg_margin:.2f}%", delta=f"{agg_margin - 35.0:.1f}% vs Target")

st.markdown("---")

# 5. TABBED ANALYTICS DASHBOARD
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    ":bar_chart: Product Profitability",
    ":factory: Division Performance",
    ":moneybag: Cost vs Margin Performance",
    ":chart_with_upwards_trend: Profit Concentration (Pareto)",
    ":world_map: Regional and Shipping Analysis",
    ":clipboard: Raw Data Explorer"
])

# TAB 1: PRODUCT PROFITABILITY OVERVIEW
with tab1:
    st.subheader("Product SKU Profitability Leaderboard")

    sku_agg = df.groupby('Product Name').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Cost=('Cost', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Division=('Product Division', 'first')
    ).reset_index()
    sku_agg['Gross Margin %'] = (sku_agg['Total_Profit'] / sku_agg['Total_Sales']) * 100
    sku_agg = sku_agg.sort_values(by='Total_Profit', ascending=True)

    col_left, col_right = st.columns(2)

    with col_left:
        fig_profit = px.bar(
            sku_agg,
            x='Total_Profit',
            y='Product Name',
            orientation='h',
            color='Division',
            title='Gross Profit Contribution by Product ($)',
            text_auto='.2s',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_profit.update_layout(xaxis_title="Total Gross Profit ($)", yaxis_title="")
        st.plotly_chart(fig_profit, use_container_width=True)

    with col_right:
        sku_agg_margin = sku_agg.sort_values(by="Gross Margin %", ascending=True)
        fig_margin = px.bar(
            sku_agg_margin,
            x="Gross Margin %",
            y="Product Name",
            orientation='h',
            color="Gross Margin %",
            title="Gross Margin % By Product SKU",
            color_continuous_scale="RdYlGn"
        )
        fig_margin.add_vline(x=35.0, line_dash="dash", line_color="red", annotation_text="35% Target Cutoff")
        fig_margin.update_layout(xaxis_title="Gross Margin (%)", yaxis_title="")
        st.plotly_chart(fig_margin, use_container_width=True)

# TAB 2: DIVISION PERFORMANCE DASHBOARD
with tab2:
    st.subheader("Division Performance Breakdown")

    div_agg = df.groupby('Product Division').agg(
        Total_Sales = ('Sales', 'sum'),
        Total_Cost = ('Cost', 'sum'),
        Total_Profit = ('Gross Profit', 'sum')
    ).reset_index()
    div_agg['Gross Margin %'] = (div_agg['Total_Profit'] / div_agg['Total_Sales']) * 100

    c1, c2 = st.columns(2)

    with c1:
        fig_pie = px.pie(
            div_agg,
            names='Product Division',
            values='Total_Sales',
            title='Revenue Share By Division',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        fig_div_bar = px.bar(
            div_agg,
            x='Product Division',
            y=['Total_Sales', 'Total_Profit'],
            barmode='group',
            title='Revenue vs Gross Profit by Division',
            labels={'value': 'Amount ($)', 'variable': 'Metric'}
        )
        st.plotly_chart(fig_div_bar, use_container_width=True)

    st.dataframe(div_agg.style.format({
        'Total_Sales': '${:,.2f}',
        'Total_Cost': '${:,.2f}',
        'Total_Profit': '${:,.2f}',
        'Gross Margin %': '{:.2f}%'
    }), use_container_width=True)

# TAB 3: COST VS MARGIN DIAGNOSTICS
with tab3:
    st.subheader("Cost Structure vs Profitability Diagnostics")

    sku_diag = df.groupby(['Product Name', 'Product Division']).agg(
        Sales=('Sales', 'sum'),
        Cost=('Cost', 'sum'),
        Profit=('Gross Profit', 'sum')
    ).reset_index()
    sku_diag['Gross Margin %'] = (sku_diag['Profit'] / sku_diag['Sales']) * 100
    sku_diag['Risk Flag'] = np.where(sku_diag['Gross Margin %'] < 35.0, 'High Risk :red_circle:', 'Healthy :green_circle:')

    fig_scatter = px.scatter(
        sku_diag,
        x='Cost',
        y='Sales',
        size='Profit',
        color='Risk Flag',
        hover_name='Product Name',
        text='Product Name',
        title='Sales vs. Cost Diagnostic (Size = Gross Profit)',
        color_discrete_map={'High Risk :red_circle:': '#EF4444', 'Healthy :green_circle:': '#10B981'}
    )
    fig_scatter.update_traces(textposition='top center')
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("### :red_circle: High-Risk SKU Alert Table (Margin < 35%)")
    high_risk_df = sku_diag[sku_diag['Gross Margin %'] < 35.0]
    if not high_risk_df.empty:
        st.dataframe(high_risk_df.style.format({
            'Sales': '${:,.2f}',
            'Cost': '${:,.2f}',
            'Profit': '${:,.2f}',
            'Gross Margin %': '{:.2f}%'
        }), use_container_width=True)
    else:
        st.success("No Products currently under perform below the 35% margin threshold under current filters.")

# TAB 4: PROFIT CONCENTRATION (PARETO ANALYSIS)
with tab4:
    st.subheader("Profit Concentration & Pareto Analysis (80/20 Rule)")

    pareto_df = df.groupby('Product Name').agg(
        Total_Profit=('Gross Profit', 'sum')
    ).reset_index().sort_values(by='Total_Profit', ascending=False)

    pareto_df['Cumulative Profit'] = pareto_df['Total_Profit'].cumsum()
    tot_p = pareto_df['Total_Profit'].sum()
    pareto_df['Cumulative %'] = (pareto_df['Cumulative Profit'] / tot_p) * 100

    # Create Dual Axis Chart
    fig_pareto = go.Figure()

    fig_pareto.add_trace(go.Bar(
        x=pareto_df['Product Name'],
        y=pareto_df['Total_Profit'],
        name='Gross Profit ($)',
        marker_color="#3B82F6"
    ))

    fig_pareto.add_trace(go.Scatter(
        x=pareto_df['Product Name'],
        y=pareto_df['Cumulative %'],
        name='Cumulative Profit %',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#EF4444', width=3)
    ))

    fig_pareto.update_layout(
        title='Pareto Chart - Cumulative Profit Contribution',
        yaxis=dict(title='Gross Profit ($)'),
        yaxis2=dict(title='Cumulative Profit %', overlaying='y', side='right', range=[0, 105]),
        xaxis=dict(tickangle=-45),
        showlegend=True
    )

    st.plotly_chart(fig_pareto, use_container_width=True)

# TAB 5: REGIONAL & SHIPPING ANALYSIS
with tab5:
    st.subheader("Geographic & Logistics Channel Performance")

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        reg_agg = df.groupby('Region').agg(Sales=('Sales', 'sum'), Profit=('Gross Profit', 'sum')).reset_index()
        fig_reg = px.bar(reg_agg, x='Region', y=['Sales', 'Profit'], barmode='group', title='Sales vs Profit by Region')
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_r2:
        ship_agg = df.groupby('Ship Mode').agg(Sales=('Sales', 'sum'), Orders=('Order ID', 'count')).reset_index()
        fig_ship = px.pie(ship_agg, names='Ship Mode', values='Sales', title='Sales Volume by Shipping Mode')
        st.plotly_chart(fig_ship, use_container_width=True)

# TAB 6: RAW DATA EXPLORER & EXPORT
with tab6:
    st.subheader("Filtered Transactional Data")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=":inbox_tray: Download Filtered Dataset as CSV",
        data=csv,
        file_name="nassau_candy_filtered_data.csv",
        mime="text/csv"
    )