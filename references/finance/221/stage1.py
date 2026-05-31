#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,238400000.0,2021800000,43371150000.0,0.0466162414416034,0.8820852705509942
2017,237000000.0,2225000000,51288500000.0,0.0433820447078779,0.8934831460674157
2018,266000000.0,2938000000,56450500000.0,0.0520455974703501,0.9094622191967324
2019,297000000.0,3696000000,57306500000.0,0.0644953015800999,0.9196428571428572
2020,337000000.0,6375000000,63716500000.0,0.1000525766481209,0.9471372549019608
2021,395000000.0,7725000000,82087500000.0,0.0941068981269986,0.9488673139158575
2022,455000000.0,6950000000,96138500000.0,0.0722915377294216,0.9345323741007194
2023,523000000.0,5995000000,97940000000.0,0.0612109454768225,0.9127606338615512
2024,583000000.0,6335000000,98023500000.0,0.0646273597657704,0.907971586424625
"""

def to_python_native(value):
    # Convert numpy types and pandas NA to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.generic,)):
        return value.item()
    return value

def compute_igr(net_income, dividends, avg_total_assets):
    # Retention ratio b = 1 - (dividends / net_income)
    # ROA = net_income / avg_total_assets
    # IGR = (ROA * b) / (1 - (ROA * b))
    try:
        if net_income == 0 or avg_total_assets == 0:
            return None
        b = 1.0 - (dividends / net_income)
        roa = net_income / avg_total_assets
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

    # Prepare scr_data: original rows converted to native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Compute IGR for each row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_python_native(row["Fiscal Year"])
        dividends = to_python_native(row["Dividends"])
        net_income = to_python_native(row["Net Income"])
        avg_assets = to_python_native(row["Avg Total Assets"])

        igr_value = compute_igr(net_income=net_income, dividends=dividends, avg_total_assets=avg_assets)

        der_rec = {
            "Fiscal Year": fiscal_year,
            "内部增长率 (Internal Growth Rate, IGR)": igr_value
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file with UTF-8 and ensure Chinese characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()