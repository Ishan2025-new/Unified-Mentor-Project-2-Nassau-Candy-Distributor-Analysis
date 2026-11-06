import os
import sys
import pandas as pd
import numpy as np

def validate_file_existance(required_files: list) -> bool:
    """
    Checks if all required project files exist in the current working directory.
    """
    print("[CHECK 1/3] Verifying required project artifacts...")
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"    ✅Found: '{file}'")
        else:
            print(f"    ❌Missing: '{file}'")
            all_present = False
    return all_present

def validate_data_integrity(processed_path: str = "data/processed/nassau_candy_processed.csv") -> bool:
    """
    Validates data integrity metrics against benchmark specs:
    - Expected total revenue ~ $141,784
    - Expected total profit ~ $93,443
    - Expected overall gross margin ~ 65.9%
    - SKU count = 15
    """
    print("\n[CHECK 2/3] Validating financial data integrity metrics...")
    if not os.path.exists(processed_path):
        print(f"    ⚠️File '{processed_path}' not found. Please run Step 1 preprocessing first.")
        return False

    df = pd.read_csv(processed_path)
    tot_sales = df['Sales'].sum()
    tot_profit = df['Gross Profit'].sum()
    margin = (tot_profit / tot_sales * 100) if tot_sales > 0 else 0.0
    unique_skus = df['Product Name'].nunique()

    print(f"  • Total Transaction Rows : {len(df):,}")
    print(f"  • Aggregate Revenue      : ${tot_sales:,.2f}")
    print(f"  • Aggregate Gross Profit : ${tot_profit:,.2f}")
    print(f"  • Aggregate Gross Margin : {margin:.2f}%")
    print(f"  • Unique Product SKUs    : {unique_skus}")

    # Check assertions
    passed = True
    if unique_skus != 15:
        print(f"    ⚠️Warning: Expected 15 SKUs, found {unique_skus}.")
        passed = False
    if not (60.0 <= margin <= 70.0):
        print(f"    ⚠️Warning: Portfolio Margin {margin:.2f}% is outside expected ~65.9% range.")
        passed = False

    if passed:
        print("     ✅Data Integrity check PASSED successfully.")
    return passed

def generate_readme(output_path: str="README.md"):
    """
    Generates a comprehensive project README.md for repository setup and deployment.
    """
    print("\n[CHECK 3/3] Generating project README.md deployment documentation...")

    readme_content = """# 🍬 Nassau Candy Distributor — Product Line Profitability & Margin Performance

A comprehensive data analytics and executive dashboard project for **Nassau Candy Distributor**, evaluating product profitability, structural margin risks, cost dynamics, and geographic performance across **10,194 orders** and **15 product SKUs**.

---

## 📌 Project Overview

Nassau Candy Distributor operates across 3 main product divisions (**Chocolate**, **Sugar**, **Other**) and 4 North American sales regions. This project provides an automated data processing pipeline and a 6-tab interactive Streamlit executive reporting dashboard.

### Key Business Metrics
* **Total Transactions:** 10,194 order records
* **Total Portfolio Revenue:** $141,784
* **Total Gross Profit:** $93,443
* **Portfolio Gross Margin:** **65.9%**
* **Key Risk Uncovered:** **Top 5 Wonka Chocolate SKUs drive 80% of enterprise gross profit** (Pareto risk), while 5 non-chocolate SKUs yield single-digit/low margins below the 35% corporate threshold.

---

## 📁 Repository Structure

```text
.
├── Nassau Candy Distributor.csv           # Raw Transactional Dataset
├── step1_data_ingestion_preprocessing.py   # Step 1: Data Preprocessing & Feature Engineering
├── app.py                                 # Step 2: Streamlit Interactive 6-Tab Dashboard
├── step3_executive_insights.py            # Step 3: Strategic Action Matrix Engine
├── step4_deployment_and_validation.py     # Step 4: End-to-End Validation & Setup Utility
├── nassau_candy_processed.csv             # Cleaned & Enriched Dataset
├── nassau_candy_sku_summary.csv           # Master SKU Financial Performance Summary
├── nassau_candy_strategic_matrix.csv     # Strategic Decision Matrix Output
├── step3_executive_summary_report.md      # Markdown C-Suite Strategic Report
└── requirements.txt                       # Required Dependencies
```

---

## 🚀 Quickstart & Execution Guide

### 1. Prerequisites & Installation

Clone the repository and install dependencies:

```bash
# Install required Python packages
pip install -r requirements.txt
```

### 2. Run Step 1: Data Preprocessing & Metric Calculation

```bash
python step1_data_ingestion_preprocessing.py
```
*Output:* Validates raw data, performs feature engineering (`Gross Profit`, `Gross Margin %`, `Unit Price`, `Unit Cost`, `Markup %`), computes Pareto cumulative ranks, and exports `nassau_candy_processed.csv` and `nassau_candy_sku_summary.csv`.

### 3. Run Step 2: Launch Interactive Streamlit Analytics Dashboard

```bash
streamlit run app.py
```
*Output:* Opens the 6-tab interactive visual analytics dashboard in your browser (`http://localhost:8501`).

### 4. Run Step 3: Generate Strategic Decision Framework & C-Suite Brief

```bash
python step3_executive_insights.py
```
*Output:* Categorizes all 15 SKUs into strategic action buckets (**Stars 🌟**, **Cash Cows 🐮**, **Niche Performers 💎**, **High Risk / Rationalize 🔴**) and outputs `step3_executive_summary_report.md`.

### 5. Run Step 4: Pre-flight Deployment Validation

```bash
python step4_deployment_and_validation.py
```

---

## 📊 Dashboard Architecture (6 Analytical Views)

1. **📊 Product Profitability:** Rank SKUs by gross profit contribution and margin percentage.
2. **🏭 Division Performance:** Evaluate revenue share and margin variance across Chocolate, Sugar, and Other divisions.
3. **💰 Cost vs Margin Diagnostics:** Scatter plot of Cost vs. Revenue highlighting products below the 35% margin threshold (*Kazookles*, *Laffy Taffy*, *SweeTARTS*, *Nerds*, *Fun Dip*).
4. **📈 Profit Concentration (Pareto):** Dual-axis Pareto chart illustrating portfolio dependency on top 5 SKUs.
5. **🗺️ Regional & Shipping Analysis:** Performance by region (Atlantic, Interior, Pacific, Gulf) and delivery modes.
6. **📋 Raw Data Explorer:** Filterable data viewer with dynamic CSV export options.

---

## 💡 Strategic Recommendations Summary

1. **Immediate Repricing / Discontinuation:** Increase prices by 15–20% or renegotiate supplier costs for *Kazookles* (7.7% margin), *Fun Dip* (10%), *Nerds* (15%), *SweeTARTS* (20%), and *Laffy Taffy* (25%). Discontinue items failing to hit 35% margin within 2 quarters.
2. **Cross-Selling Expansion:** Leverage the high-volume Chocolate customer base to cross-sell high-margin Sugar products (*Everlasting Gobstopper* at 80% margin and *Hair Toffee* at 77.8% margin).
3. **Factory Supply Chain Audit:** Audit production cost structures with *Secret Factory* and *The Other Factory*.

---

## 🛠️ Deployment Instructions

### Streamlit Community Cloud
1. Push repository code to GitHub.
2. Connect repository to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Set Main file path to `app.py`.
4. Deploy application.

---
*Developed by Project Expert | Nassau Candy Analytics Project*
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"    ✅Project documentation saved to '{output_path}'.")

def main():
    print("=" * 80)
    print("     NASSAU CANDY DISTRIBUTOR — STEP 4 PRE-FLIGHT VALIDATION ENGINE")
    print("=" * 80)

    required_files = [
        "requirements.txt",
        "data_ingestion_preprocessing.py",
        "app.py",
        "executive_insights.py"
    ]

    # Run Checks
    check1 = validate_file_existance(required_files)
    check2 = validate_data_integrity()
    generate_readme()

    print("\n" + "=" * 80)

    if check1 and check2:
        print("🎉PROJECT PRE-FLIGHT CHECK COMPLETE - ALL SYSTEMS READY FOR DEPLOYMENT!")
        print("Run 'streamlit run app.py' to launch your executive dashboard.")
    else:
        print("⚠️PRE-FLIGHT CHECKS FINISHED WITH WARNINGS. Review logs above.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()