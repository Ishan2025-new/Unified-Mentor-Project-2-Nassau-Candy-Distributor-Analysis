import os
import pandas as pd
import numpy as np

# Set display option for clean terminal output
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Loads raw CSV data with robust error handling.
    Falls back to synthetic/mock data matching the Nassau Candy schema 
    if the CSV file is not present in the workspace.
    """
    if os.path.exists(file_path):
        print(f"[INFO] Loading Dataset from '{file_path}'...")
        df = pd.read_csv(file_path)
    else:
        print(f"[WARNING] File '{file_path}' not found. Generating exact mock dataset based on project specs...")
        df = generate_mock_nassau_data()
    return df

def generate_mock_nassau_data() -> pd.DataFrame:
    """
    Generates representative data following the exact Nassau Candy Distributor metrics.
    Used as a fallback mechanism for standalone execution.
    """
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
            'Cost': cost
        })

    return pd.DataFrame(data)

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Excecute primary feature engineering and metric enrichments.
    """
    print("[INFO] Starting feature engineering and metric calculations...")

    # Ensure product hierarchy columns exist so downstream analysis can handle alternate schemas.
    for col in ['Product Name', 'Product Division', 'Factory']:
        if col not in df.columns:
            df[col] = 'Unknown'

    # 1. Standarize Dates
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True, errors='coerce')
        df['Year'] = df['Order Date'].dt.year
        df['Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)
        df['Month_Year'] = df["Order Date"].dt.to_period('M').astype(str)

    # 2. Financial Metrics Calculation
    # Ensure required financial columns exist, even when the source schema varies.
    for col in ['Sales', 'Cost', 'Quantity']:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Core Calculations
    df['Gross Profit'] = df['Sales'] - df['Cost']
    df['Gross Margin %'] = np.where(df['Sales'] > 0, (df['Gross Profit'] / df['Sales']) * 100, 0.0)
    df['Unit Price'] = np.where(df['Quantity'] > 0, df['Sales'] / df['Quantity'], 0.0)
    df['Unit Cost'] = np.where(df['Quantity'] > 0, df['Cost'] / df['Quantity'], 0.0)
    df['Markup %'] = np.where(df['Cost'] > 0, (df['Gross Profit'] / df['Cost']) * 100, 0.0)

    # 3. Categorize Margin Risk Profile
    def classify_risk(margin):
        if margin < 35.0:
            return 'High Risk 🔴'
        elif margin < 50.0:
            return 'Moderate Margin 🟡'
        else:
            return 'Healthy 🟢'

    df["Risk Flag"] = df["Gross Margin %"].apply(classify_risk)

    print("[INFO] Feature engineering completed successfully.")
    return df

def generate_pareto_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Pareto Cumulative Gross Profit Contribution by SKU.
    """
    print("[INFO] Calculating Pareto Profit Concentration...")
    sku_summary = df.groupby(['Product Name', 'Product Division', 'Factory']).agg(
        Total_Sales = ('Sales', 'sum'),
        Total_Cost = ('Cost', 'sum'),
        Total_Profit = ('Gross Profit', 'sum'),
        Total_Orders = ('Sales', 'count'),
        Total_Units = ('Quantity', 'sum')
    ).reset_index()

    sku_summary['Gross Margin %'] = (sku_summary['Total_Profit'] / sku_summary['Total_Sales']) * 100

    # Sort descending by Profit for Pareto
    sku_summary = sku_summary.sort_values(by='Total_Profit', ascending=False).reset_index(drop=True)

    sku_summary['Cumulative Profit'] = sku_summary['Total_Profit'].cumsum()
    total_portfolio_profit = sku_summary['Total_Profit'].sum()
    sku_summary['Cumulative Profit %'] = (sku_summary['Cumulative Profit'] / total_portfolio_profit) * 100

    # Categorize Pareto Segment
    sku_summary['Pareto Category'] = np.where(sku_summary['Cumulative Profit %'] <= 80.0, 
                                              'Top 80% Driver Class A', 'Remaining 20% (Class B/C)')

    return sku_summary

def print_executive_summary(df: pd.DataFrame, pareto_df: pd.DataFrame):
    """
    Prints executive high-level summary KPIs to console.
    """
    total_sales = df['Sales'].sum()
    total_cost = df["Cost"].sum()
    total_profit = df['Gross Profit'].sum()
    portfolio_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
    total_orders = len(df)
    unique_skus = df["Product Name"].nunique()
    high_risk_skus = pareto_df[pareto_df["Gross Margin %"] < 35.0]['Product Name'].tolist()

    print("\n" + "="*80)
    print("     NASSAU CANDY DISTRIBUTOR - STEP 1 PREPROCESSING KPI REPORT")
    print("="*80)
    print(f"Total Transactions Processed: {total_orders:,}")
    print(f"Unique Product SKUs: {unique_skus}")
    print(f"Total Portfolio Revenue: ${total_sales:,.2f}")
    print(f"Total Cost of Goods Sold: ${total_cost:,.2f}")
    print(f"Total Gross Profit: ${total_profit:,.2f}")
    print(f"Aggregate Portfolio Margin: {portfolio_margin:.2f}%")
    print("-"*80)
    print("HIGH RISK SKUs (Margin < 35%):")
    for sku in high_risk_skus:
        margin = pareto_df[pareto_df['Product Name'] == sku]['Gross Margin %'].values[0]
        print(f"    • {sku:<35} | Gross Margin: {margin:.2f}%")
    print("="*80 + "\n")

def main():
    """
    Main Execution Workflow for Step 1.
    """
    raw_file = "data/raw/Nassau Candy Distributor.csv"
    processed_file = "data/processed/nassau_candy_processed.csv"
    summary_file = "data/summary/nassau_candy_sku_summary.csv"

    # Step 1.1: Load
    raw_df = load_dataset(raw_file)

    # Step 1.2: Preprocess and Engineer Features
    processed_df = preprocess_data(raw_df)

    # Step 1.3: Pareto Analysis
    pareto_df = generate_pareto_analysis(processed_df)

    # Step 1.4: Save Outputs
    processed_df.to_csv(processed_file, index=False)
    pareto_df.to_csv(summary_file, index=False)
    print(f"[SUCCESS] Processed dataset saved to '{processed_file}'")
    print(f"[SUCCESS] SKU Executive summary saved to '{summary_file}'")

    # Step 1.5: Print Summary Report
    print_executive_summary(processed_df, pareto_df)

if __name__ == "__main__":
    main()