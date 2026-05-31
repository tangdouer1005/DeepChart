#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,0.0,10217000000,57184000000.0,0.1786688584219362,1.0
2017,0.0,15934000000,74742500000.0,0.2131852694250259,1.0
2018,0.0,22112000000,90929000000.0,0.2431787438550957,1.0
2019,2337000000.0,18485000000,115355000000.0,0.160244462745438,0.8735731674330538
2020,0.0,29146000000,146346000000.0,0.199158159430391,1.0
2021,0.0,39370000000,162651500000.0,0.2420512568282493,1.0
2022,0.0,23200000000,175857000000.0,0.1319253711822674,1.0
2023,0.0,39098000000,207675000000.0,0.1882653184061634,1.0
2024,5072000000.0,62360000000,252838500000.0,0.2466396533755737,0.9186658114175754
"""

def to_native(value):
    """Convert numpy/pandas scalar types to native Python types for JSON serialization."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        # convert to regular float
        return float(value)
    return value

def compute_igr(dividends, net_income, avg_total_assets):
    """
    Compute Internal Growth Rate (IGR) using:
      b = 1 - (Dividends / Net Income)
      ROA = Net Income / Avg Total Assets
      IGR = (ROA * b) / (1 - (ROA * b))
    Returns a Python float or None if cannot be computed.
    """
    # Validate inputs
    try:
        if net_income is None or avg_total_assets is None:
            return None
        # ensure numeric
        net_income = float(net_income)
        avg_total_assets = float(avg_total_assets)
        dividends = 0.0 if dividends is None else float(dividends)

        # Avoid division by zero for retention ratio and ROA
        if net_income == 0 or avg_total_assets == 0:
            return None

        b = 1.0 - (dividends / net_income)
        roa = net_income / avg_total_assets

        roab = roa * b
        denom = 1.0 - roab
        if denom == 0:
            return None

        igr = roab / denom
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts representing the raw input rows
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Prepare der_data: compute IGR for each row
    der_records = []
    for _, row in df.iterrows():
        dividends = row.get("Dividends")
        net_income = row.get("Net Income")
        avg_total_assets = row.get("Avg Total Assets")

        igr_value = compute_igr(dividends, net_income, avg_total_assets)
        # include the fiscal year if present
        entry = {}
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = to_native(row["Fiscal Year"])
        entry["内部增长率 (Internal Growth Rate, IGR)"] = to_native(igr_value)
        der_records.append(entry)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()