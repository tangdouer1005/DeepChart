#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,3717000000.0,5953000000,59574500000.0,0.0999253036114445,0.3756089366705862
2017,4107000000.0,5309000000,68442500000.0,0.0775687620995726,0.226407986438124
2018,5580000000.0,5687000000,65069000000.0,0.0873995297299789,0.0188148408651309
2019,6366000000.0,7882000000,74233500000.0,0.1061784773720759,0.1923369703121035
2020,7716000000.0,4616000000,119840000000.0,0.0385180240320427,-0.6715771230502601
2021,9261000000.0,11542000000,148547000000.0,0.0776993140218247,0.1976260613411886
2022,10043000000.0,11836000000,142667000000.0,0.082962422984993,0.1514869888475836
2023,10539000000.0,4863000000,136758000000.0,0.0355591629008906,-1.1671807526218383
2024,11025000000.0,4278000000,134936000000.0,0.0317039188948835,-1.5771388499298735
"""

def to_native(x):
    # Convert numpy/pandas types to native Python types for JSON serialization
    if pd.isna(x):
        return None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        # Convert NaN/inf to None
        if np.isfinite(x):
            return float(x)
        return None
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    return x

def compute_igr(dividends, net_income, avg_total_assets):
    # Compute retention ratio b = 1 - (dividends / net_income)
    # Compute ROA = net_income / avg_total_assets
    # IGR = (ROA * b) / (1 - ROA * b)
    try:
        if net_income is None or avg_total_assets is None:
            return None
        # ensure floats
        net_income = float(net_income)
        dividends = float(dividends) if dividends is not None else 0.0
        avg_total_assets = float(avg_total_assets)
        # Avoid division by zero
        if net_income == 0 or avg_total_assets == 0:
            return None
        b = 1.0 - (dividends / net_income)
        roa = net_income / avg_total_assets
        x = roa * b
        denom = 1.0 - x
        if denom == 0:
            return None
        igr = x / denom
        if not np.isfinite(igr):
            return None
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts preserving input columns
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Prepare der_data: calculated IGR per row
    der_data = []
    for _, row in df.iterrows():
        fy = to_native(row["Fiscal Year"]) if "Fiscal Year" in row.index else None
        dividends = to_native(row.get("Dividends", None))
        net_income = to_native(row.get("Net Income", None))
        avg_assets = to_native(row.get("Avg Total Assets", None))

        igr_value = compute_igr(dividends, net_income, avg_assets)

        der_rec = {
            "Fiscal Year": fy,
            "内部增长率 (Internal Growth Rate, IGR)": igr_value
        }
        der_data.append(der_rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve non-ASCII indicator name
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()