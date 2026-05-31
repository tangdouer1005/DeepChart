#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

csv_data = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,6988000000,14092000000,36908000000,78778000000,21080000000,316947945.20547944
2017,4813000000,15353000000,36432000000,95114000000,20166000000,360400000.0
2018,9342000000,15050000000,30459000000,113997000000,24392000000,395769863.0136986
2019,5686000000,13325000000,30434000000,109331000000,19011000000,382917808.2191781
2020,5596000000,11471000000,29757000000,71656000000,17067000000,277843835.6164383
2021,5640000000,18419000000,29328000000,110174000000,24059000000,382197260.27397263
2022,17678000000,20456000000,34327000000,161735000000,38134000000,537156164.3835616
2023,8178000000,19921000000,26601000000,136522000000,28099000000,446912328.7671233
2024,6781000000,20684000000,27827000000,136488000000,27465000000,450178082.1917808
"""

def sanitize_value(v):
    # Convert numpy types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(csv_data))

    # Calculation for Defensive Interval Ratio (DIR)
    # Quick Assets is provided in the CSV as "Quick Assets"
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption

    # Ensure numeric columns are numeric
    numeric_cols = ["Cash & Equiv", "Receivables", "Operating Expenses", "Cost of Revenue", "Quick Assets"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    daily_consumption = (df["Operating Expenses"] + df["Cost of Revenue"]) / 365.0
    dir_values = df["Quick Assets"] / daily_consumption

    # Prepare scr_data: original rows as list of dicts with sanitized values
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = sanitize_value(row[col])
        # If Daily Burn column exists in CSV, include it as well (it was in the CSV)
        scr_data.append(rec)

    # Prepare der_data: calculated DIR per row
    der_data = []
    for i, row in df.iterrows():
        year = sanitize_value(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None
        dir_val = sanitize_value(dir_values.iat[i])
        rec = {}
        if year is not None:
            rec["Fiscal Year"] = year
        rec["防御区间比率 (Defensive Interval Ratio, DIR)"] = dir_val
        der_data.append(rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()