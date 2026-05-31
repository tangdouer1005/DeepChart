#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,13570000000,10739000000,121652000000,117512500000.0,0.115477076906712,0.0913860227635357
2017,13876000000,9609000000,129818000000,125735000000.0,0.1103590885592714,0.0764226349067483
2018,13666000000,110000000,108784000000,119301000000.0,0.1145505905231305,0.0009220375353098
2019,15831000000,11621000000,97793000000,103288500000.0,0.1532697250904021,0.1125101051908005
2020,15426000000,11214000000,94853000000,96323000000.0,0.1601486664659531,0.1164207925417605
2021,15454000000,10591000000,97497000000,96175000000.0,0.1606862490252144,0.1101221731219131
2022,13226000000,11812000000,94002000000,95749500000.0,0.1381312696149849,0.1233635684781643
2023,19886000000,12613000000,101852000000,97927000000.0,0.2030696335025069,0.1288000245080519
2024,10880000000,10320000000,124413000000,113132500000.0,0.0961704196406868,0.0912204715709455
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_json_friendly(val):
    # Convert numpy/pandas numeric types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    # For plain Python numeric types
    if isinstance(val, (int, float, str, bool)) or val is None:
        return val
    # Fallback to string
    return str(val)

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: preserve original columns/values
    scr_records_raw = df.to_dict(orient="records")
    scr_records = []
    for rec in scr_records_raw:
        converted = {k: to_json_friendly(v) for k, v in rec.items()}
        scr_records.append(converted)

    # Calculate Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_records = []
    for _, row in df.iterrows():
        # Extract raw inputs
        cfo = row.get("CFO")
        net_income = row.get("Net Income")
        total_assets = row.get("Total Assets")

        # Safely handle missing or zero total assets
        spread = None
        try:
            if pd.notna(total_assets) and total_assets != 0:
                spread = (float(cfo) / float(total_assets)) - (float(net_income) / float(total_assets))
            else:
                spread = None
        except Exception:
            spread = None

        der_rec = {}
        # Include Fiscal Year if present in input
        if "Fiscal Year" in df.columns:
            der_rec["Fiscal Year"] = to_json_friendly(row["Fiscal Year"])
        der_rec[INDICATOR_NAME] = to_json_friendly(spread)
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()