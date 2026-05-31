#!/usr/bin/env python3
import sys
import io
import json
import math
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,8806000000,7500000000,429150000000.0,0.0174764068507514,-0.1741333333333332
2017,8650000000,-8484000000,373907500000.0,-0.0226901038358417,2.01956624233852
2018,4474000000,-22355000000,345857500000.0,-0.064636447091649,1.2001341981659583
2019,649000000,-4979000000,287550000000.0,-0.0173152495218222,1.130347459329183
2020,648000000,5704000000,261105500000.0,0.0218455758304593,0.8863955119214586
2021,575000000,-6337000000,227542500000.0,-0.0278497423558236,1.090736941770554
2022,639000000,292000000,193862500000.0,0.001506222193565,-1.1883561643835616
2023,589000000,9482000000,182478500000.0,0.0519622859679359,0.9378823033115375
2024,1008000000,6556000000,150933500000.0,0.0434363477955523,0.8462477120195241
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_native(value):
    # Convert numpy/pandas types to native Python types for JSON serialization
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        # convert NaN to None
        if math.isnan(value):
            return None
        return float(value)
    if pd.isna(value):
        return None
    return value

def compute_igr(dividends, net_income, avg_total_assets):
    # Compute retention ratio b = 1 - (dividends / net_income)
    # ROA = net_income / avg_total_assets
    # IGR = (ROA * b) / (1 - (ROA * b))
    # Handle division by zero and missing data
    try:
        if net_income is None or avg_total_assets is None or dividends is None:
            return None
        # Avoid division by zero when net_income == 0
        if net_income == 0:
            return None
        b = 1.0 - (dividends / net_income)
        # Avoid division by zero when avg_total_assets == 0
        if avg_total_assets == 0:
            return None
        roa = net_income / avg_total_assets
        numerator = roa * b
        denom = 1.0 - numerator
        # If denom is zero (or numerically extremely close), return None
        if denom == 0 or math.isclose(denom, 0.0, rel_tol=1e-12, abs_tol=1e-12):
            return None
        igr = numerator / denom
        # If result is not finite (inf/nan), return None
        if not math.isfinite(igr):
            return None
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw rows from CSV with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Prepare der_data: compute IGR for each row; include Fiscal Year if present
    der_records = []
    for _, row in df.iterrows():
        dividends = row.get("Dividends")
        net_income = row.get("Net Income")
        avg_total_assets = row.get("Avg Total Assets")
        # Convert numpy types to native python numbers for computation
        dividends_val = None if pd.isna(dividends) else float(dividends)
        net_income_val = None if pd.isna(net_income) else float(net_income)
        avg_total_assets_val = None if pd.isna(avg_total_assets) else float(avg_total_assets)

        igr_value = compute_igr(dividends_val, net_income_val, avg_total_assets_val)
        rec = {}
        # include Fiscal Year if present in input
        if "Fiscal Year" in df.columns:
            fy = row.get("Fiscal Year")
            rec["Fiscal Year"] = to_native(fy)
        rec[INDICATOR_NAME] = to_native(igr_value)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()