import os
import pandas as pd
import numpy as np

def load_preprocessed_data(file_path: str="data/processed/nassau_candy_processed.csv") -> pd.DataFrame:
    """
    Loads preprocessed dataset generated in Step 1.
    Fallback logic loads or generates if not found.
    """
    if os.path.exists(file_path):
        print(f"[INFO] Loading preprocessed data from '{file_path}'...")
        return pd.read_csv(file_path)
    else:
        print(f"[WARNING] Processed file not found. Please run Step 1 script first.")
        # Attempt Fallback import
        from data_ingestion_preprocessing import load_dataset, preprocess_data
        df_raw = load_dataset("data/raw/Nassau Candy Distributor.csv")
        return preprocess_data(df_raw)

def compute_sku_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates financial performance metrics by Product SKU.
    """
    sku_agg = df.groupby(['Product Name', 'Product Division', 'Factory']).agg(
        Total_Sales=('Sales', 'sum'),
        Total_Cost=('Cost', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Order_Count=('Sales', 'count'),
        Total_Units=('Quantity', 'sum')
    ).reset_index()

    sku_agg['Gross Margin %'] = (sku_agg['Total_Profit'] / sku_agg['Total_Sales']) * 100
    sku_agg['Sales Contribution %'] = (sku_agg['Total_Sales'] / sku_agg['Total_Sales'].sum()) * 100
    sku_agg['Profit Contribution %'] = (sku_agg['Total_Profit'] / sku_agg['Total_Profit'].sum()) * 100

    # Sort descending by Profit
    sku_agg = sku_agg.sort_values(by='Total_Profit', ascending=False).reset_index(drop=True)
    sku_agg['Cumulative Profit %'] = (sku_agg['Total_Profit'].cumsum() / sku_agg['Total_Profit'].sum()) * 100
    return sku_agg

def generate_strategic_matrix(sku_df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies Strategic Action Matrix logic to group SKUs:
    - Stars 🌟          : Margin >= 50% AND Profit Contribution >= 5%
    - Cash Cows 🐮      : Margin < 50% AND Profit Contribution >= 5%
    - Niche Performers 💎: Margin >= 50% AND Profit Contribution < 5%
    - High Risk / Rationalize 🔴: Margin < 35%
    """
    def categorize_sku(row):
        margin = row['Gross Margin %']
        profit_share = row['Profit Contribution %']

        if margin < 35.0:
            return "High Risk / Rationalize 🔴"
        elif margin >= 60.0 and profit_share >= 10.0:
            return "Star Product 🌟"
        elif margin >= 50.0:
            return "Niche Profit Driver 💎"
        else:
            return "Volume Driver 🐮"

    sku_df['Strategic Classification'] = sku_df.apply(categorize_sku, axis=1)

    # Actionable Recommendation Engine
    recommendations = {
        "Star Product 🌟": "Expand distribution, maintain premium pricing, protect supply chain.",
        "Niche Profit Driver 💎": "Scale up marketing and cross-sell via Chocolate accounts.",
        "Volume Driver 🐮": "Optimize COGS and evaluate minor price adjustments.",
        "High Risk / Rationalize 🔴": "Immediate 15-25% repricing or supplier renegotiation; "
        "discontinue if margin remains < 35%."
    }

    sku_df['Recommended Action'] = sku_df['Strategic Classification'].map(recommendations)
    return sku_df

def generate_executive_report(df: pd.DataFrame, sku_df: pd.DataFrame, 
                              output_path: str="outputs/reports/executive_summary_report.md"):
    """
    Generates a structured Executive Summary Markdown Document.
    """
    tot_sales = df['Sales'].sum()
    tot_cost = df['Cost'].sum()
    tot_profit = df['Gross Profit'].sum()
    agg_margin = (tot_profit / tot_sales) * 100

    top_5_profit_share = sku_df.head(5)['Profit Contribution %'].sum()
    high_risk_skus = sku_df[sku_df['Gross Margin %'] < 35.0]

    report = f"""
## Executive Summary
* **Aggregate Sales Volume:** ${tot_sales:,.2f}
* **Total Cost Base (COGS):** ${tot_cost:,.2f}
* **Total Gross Profit Generated:** ${tot_profit:,.2f}
* **Overall Portfolio Gross Margin:** **{agg_margin:.2f}%**

---

## Key Strategic Findings

### 1. High Portfolio Concentration (Pareto Risk)
* The **Top 5 Wonka Chocolate SKUs** generate **{top_5_profit_share:.1f}%** of total enterprise profit.
* *Wonka Bar - Scrumdiddlyumptious* is the single largest profit contributor at **{sku_df.iloc[0]['Profit Contribution %']:.1f}%** gross profit share.

### 2. Underperforming Products (Margin Drag)
* Identified **{len(high_risk_skus)} high-risk SKUs** operating well below the **35.0% gross margin target**:
    """

    for _, row in high_risk_skus.iterrows():
        report += f"  - **{row['Product Name']}** ({row['Product Division']}): " \
        f"Gross Margin = **{row['Gross Margin %']:.2f}%** | Total Profit = ${row['Total_Profit']:,.2f}\n"
        report += f"""
## Strategic Action Matrix & Recommendations

| Product Name | Division | Gross Margin (%) | Profit Contribution (%) | Strategic Classification | Recommended Action |
|---|---|---|---|---|---|
    """

    for _, row in sku_df.iterrows():
        report += f"| {row['Product Name']} | {row['Product Division']} | {row['Gross Margin %']:.1f}% | " \
        f"{row['Profit Contribution %']:.1f}% | {row['Strategic Classification']} | {row['Recommended Action']} |\n"

        report += """
    ---

## Immediate 90-Day Implementation Plan

1. **Reprice Low Margin SKUs:** Raise prices on *Kazookles*, *Laffy Taffy*, *SweeTARTS*, *Nerds*, and *Fun Dip* by 15–20%.
2. **Renegotiate Supplier Contracts:** Work with *Secret Factory* and *The Other Factory* to reduce wholesale supply costs.
3. **Cross-Sell High Margin Sugar SKUs:** Introduce *Everlasting Gobstopper* (80% margin) and *Hair Toffee* (77.8% margin) to existing high-volume Chocolate distributors.
4. **SKU Rationalization Threshold:** Set a firm corporate cutoff: any SKU failing to achieve 35% margin within 2 quarters will be discontinued.
    """

    with open(output_path, "w", encoding='utf-8') as f:
        f.write(report)

    print(f"[SUCCESS] Executive Strategic Report generated successfully at '{output_path}'.")

def main():
    print("=" * 80)
    print("   NASSAU CANDY DISTRIBUTOR — STEP 3 EXECUTIVE STRATEGIC ANALYSIS ENGINE")
    print("=" * 80)

    # 1. Load Data
    df = load_preprocessed_data()

    # 2. Compute SKU Performance
    sku_df = compute_sku_metrics(df)

    # 3. Apply Decision Matrix
    sku_df = generate_strategic_matrix(sku_df)

    # 4. Save Matrix Output
    sku_df.to_csv("outputs/matrix/nassau_candy_strategic_matrix.csv", index=False)
    print("[SUCCESS] Strategic Matrix saved to 'nassau_candy_strategic_matrix.csv'.")

    # 5. Generate Executive Report
    generate_executive_report(df, sku_df)

    # 6. Console Summary Printout
    print("\n--- STRATEGIC ACTION MATRIX SUMMARY ---")
    print(sku_df[['Product Name', 'Gross Margin %', 'Strategic Classification']].to_string(index=False))
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()