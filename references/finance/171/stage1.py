#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,11006000000,20539000000,184083000000.0,0.1115746701216299,0.4641413895515848
2017,11845000000,25489000000,217390000000.0,0.117250103500621,0.535289732825925
2018,12699000000,16571000000,249967000000.0,0.0662927506430848,0.2336612153762597
2019,13811000000,39240000000,272702000000.0,0.143893334115628,0.6480377166156983
2020,15137000000,44281000000,293933500000.0,0.1506497217908132,0.6581603848151578
2021,16521000000,61271000000,317545000000.0,0.1929521800059834,0.730361835125916
2022,18135000000,72738000000,349309500000.0,0.2082336724308958,0.7506805246226181
2023,19800000000,72361000000,388408000000.0,0.1863015179913905,0.7263719406862813
2024,21771000000,88136000000,462069500000.0,0.1907418689179874,0.7529840246891168
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_native(val):
    # Convert numpy / pandas scalar types to native Python types, keep None for NA
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val

def compute_igr(dividends, net_income, total_assets):
    """
    Compute Internal Growth Rate (IGR) per:
    b = 1 - (dividends / net_income)
    ROA = net_income / total_assets
    IGR = (ROA * b) / (1 - ROA * b)
    Return None if cannot compute (e.g., division by zero or missing data)
    """
    try:
        if net_income is None or total_assets is None or dividends is None:
            return None
        # ensure floats
        net_income = float(net_income)
        total_assets = float(total_assets)
        dividends = float(dividends)
        if net_income == 0 or total_assets == 0:
            return None
        b = 1.0 - (dividends / net_income)
        roa = net_income / total_assets
        denom = 1.0 - (roa * b)
        if denom == 0:
            return None
        igr = (roa * b) / denom
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: mirror input CSV rows with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Compute der_data: one entry per row with Fiscal Year (if exists) and IGR
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row.get("Fiscal Year"))
        dividends = to_native(row.get("Dividends"))
        net_income = to_native(row.get("Net Income"))
        avg_total_assets = to_native(row.get("Avg Total Assets"))

        igr_value = compute_igr(dividends=dividends, net_income=net_income, total_assets=avg_total_assets)

        rec = {}
        # include year if present
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[INDICATOR_NAME] = igr_value
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()