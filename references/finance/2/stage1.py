#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,5100000000.0,4758000000.0,10466000000,5833000000,9858000000.0,44654794.52054795
2017,9303000000.0,5088000000.0,11629000000,7040000000,14391000000.0,51147945.20547945
2018,7289000000.0,5384000000.0,18652000000,7718000000,12673000000.0,72246575.34246576
2019,39924000000.0,5428000000.0,12844000000,7439000000,45352000000.0,55569863.01369863
2020,8449000000.0,8822000000.0,19054000000,15387000000,17271000000.0,94358904.10958904
2021,9746000000.0,9977000000.0,20827000000,17446000000,19723000000.0,104857534.24657534
2022,9201000000.0,11254000000.0,22523000000,17414000000,20455000000.0,109416438.35616438
2023,12814000000.0,11155000000.0,21146000000,20415000000,23969000000.0,113865753.42465754
2024,5524000000.0,10919000000.0,30293000000,16904000000,16443000000.0,129306849.3150685
"""

INDICATOR_NAME = "防御区间比率 (Defensive Interval Ratio, DIR)"

def to_native(v):
    """Convert numpy / pandas scalars to native Python types for JSON serialization."""
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        # convert to Python float
        return float(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with native types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate DIR for each row dynamically
    der_data = []
    for _, row in df.iterrows():
        # Determine quick assets:
        # Prefer explicit 'Quick Assets' column if present and not null,
        # otherwise attempt to compute from Cash & Equiv + Receivables + TradingFinancialAssets (if present).
        if 'Quick Assets' in df.columns and not pd.isna(row['Quick Assets']):
            quick_assets = float(row['Quick Assets'])
        else:
            # fall back to summing known components
            cash = float(row['Cash & Equiv']) if ('Cash & Equiv' in df.columns and not pd.isna(row['Cash & Equiv'])) else 0.0
            receivables = float(row['Receivables']) if ('Receivables' in df.columns and not pd.isna(row['Receivables'])) else 0.0
            tfa = float(row['Trading Financial Assets']) if ('Trading Financial Assets' in df.columns and not pd.isna(row['Trading Financial Assets'])) else 0.0
            quick_assets = cash + receivables + tfa

        # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
        op_exp = float(row['Operating Expenses']) if ('Operating Expenses' in df.columns and not pd.isna(row['Operating Expenses'])) else 0.0
        cogs = float(row['Cost of Revenue']) if ('Cost of Revenue' in df.columns and not pd.isna(row['Cost of Revenue'])) else 0.0
        daily_consumption = (op_exp + cogs) / 365.0

        if daily_consumption == 0:
            dir_value = None
        else:
            dir_value = quick_assets / daily_consumption

        entry = {}
        # include Fiscal Year if present
        if 'Fiscal Year' in df.columns and not pd.isna(row['Fiscal Year']):
            entry['Fiscal Year'] = to_native(row['Fiscal Year'])
        entry[INDICATOR_NAME] = to_native(dir_value)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()