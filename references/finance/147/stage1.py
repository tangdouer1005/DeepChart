#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,4484000000,4059000000,18675000000,17472000000.0,0.2566391941391941,0.2323145604395604
2017,5555000000,3915000000,21329000000,20002000000.0,0.2777222277772223,0.1957304269573042
2018,6223000000,5859000000,24860000000,23094500000.0,0.2694580960834831,0.2536967676286562
2019,8183000000,8118000000,29236000000,27048000000.0,0.302536231884058,0.3001330967169476
2020,7224000000,6411000000,33584000000,31410000000.0,0.2299904489016236,0.2041069723018147
2021,9463000000,8687000000,37669000000,35626500000.0,0.2656168863065414,0.2438353472836231
2022,11195000000,9930000000,38724000000,38196500000.0,0.2930896809917139,0.2599714633539722
2023,11980000000,11195000000,42448000000,40586000000.0,0.2951756763415956,0.2758340314394126
2024,14780000000,12874000000,48081000000,45264500000.0,0.3265252018690143,0.2844171480961902
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_py(v):
    # Convert numpy and pandas types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts with original columns, converting types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py(row[col])
        scr_records.append(rec)

    # Calculate Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_records = []
    for _, row in df.iterrows():
        cfo = row["CFO"]
        ni = row["Net Income"]
        total_assets = row["Total Assets"]

        # Defensive handling for zero or missing total assets
        if pd.isna(total_assets) or total_assets == 0:
            spread = None
        else:
            spread = (cfo / total_assets) - (ni / total_assets)

        rec = {}
        # include the fiscal year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_py(row["Fiscal Year"])
        rec[INDICATOR_NAME] = to_py(spread) if spread is not None else None
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()