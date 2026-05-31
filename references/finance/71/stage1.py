#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,8032000000,-497000000,262309000000.0,-0.0018947119618465,17.16096579476861
2017,8132000000,9195000000,256942000000.0,0.0357862863992652,0.1156063077759651
2018,8500000000,14824000000,253834500000.0,0.058400256860277,0.4266055045871559
2019,9000000000,2924000000,245645500000.0,0.0119033322409732,-2.0779753761969904
2020,9700000000,-5543000000,238609000000.0,-0.0232304732847461,2.749954898069637
2021,10200000000,15625000000,239662500000.0,0.0651958483283784,0.3471999999999999
2022,11000000000,35465000000,248622000000.0,0.1426462662194013,0.6898350486395037
2023,11336000000,21369000000,259670500000.0,0.0822927517758081,0.4695119097758435
2024,11800000000,17661000000,259285000000.0,0.0681142372293036,0.3318611630145518
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_plain_python(value):
    """
    Convert numpy/pandas scalar types to native Python types for JSON serialization.
    """
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value

def calculate_igr(dividends, net_income, total_assets):
    """
    Calculate Internal Growth Rate (IGR) per reference:
    b = 1 - (Dividends / Net Income)
    ROA = Net Income / Total Assets
    IGR = (ROA * b) / (1 - (ROA * b))
    Returns None when calculation is not possible (e.g., division by zero).
    """
    # protect against invalid inputs
    try:
        # retention ratio
        if net_income == 0 or net_income is None:
            return None
        b = 1.0 - (dividends / net_income)

        if total_assets == 0 or total_assets is None:
            return None
        roa = net_income / total_assets

        product = roa * b
        denom = 1.0 - product
        if denom == 0:
            return None
        igr = product / denom
        return float(igr)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert dataframe rows to plain python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_plain_python(row[col])
        scr_records.append(rec)

    # Prepare der_data by computing IGR for each row
    der_records = []
    for _, row in df.iterrows():
        # Use raw input fields: Dividends, Net Income, Avg Total Assets
        dividends = row.get("Dividends")
        net_income = row.get("Net Income")
        total_assets = row.get("Avg Total Assets")

        # Convert numpy types to plain python numbers for computation
        if isinstance(dividends, (np.generic,)):
            dividends = dividends.item()
        if isinstance(net_income, (np.generic,)):
            net_income = net_income.item()
        if isinstance(total_assets, (np.generic,)):
            total_assets = total_assets.item()

        igr_value = calculate_igr(dividends, net_income, total_assets)

        rec = {}
        # include year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_plain_python(row["Fiscal Year"])
        rec[INDICATOR_NAME] = to_plain_python(igr_value)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()