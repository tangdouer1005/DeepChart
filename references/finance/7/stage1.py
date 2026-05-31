#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,7041000000,5953000000,66099000000.0,59574500000.0,0.1181881509706334,0.0999253036114445
2017,9960000000,5309000000,70786000000.0,68442500000.0,0.1455236147130803,0.0775687620995726
2018,13427000000,5687000000,59352000000.0,65069000000.0,0.2063501821143709,0.0873995297299789
2019,13324000000,7882000000,89115000000.0,74233500000.0,0.1794876976028343,0.1061784773720759
2020,17588000000,4616000000,150565000000.0,119840000000.0,0.146762349799733,0.0385180240320427
2021,22777000000,11542000000,146529000000.0,148547000000.0,0.1533319420789379,0.0776993140218247
2022,24943000000,11836000000,138805000000.0,142667000000.0,0.1748337036595708,0.082962422984993
2023,22839000000,4863000000,134711000000.0,136758000000.0,0.1670030272452068,0.0355591629008906
2024,18806000000,4278000000,135161000000.0,134936000000.0,0.1393697753008833,0.0317039188948835
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_native(value):
    """
    Convert numpy/pandas scalar types to native Python types for JSON serialization.
    """
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    # fallback for Python built-in numeric types and strings
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    # attempt conversion
    try:
        return int(value)
    except Exception:
        try:
            return float(value)
        except Exception:
            return str(value)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)

    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows as dictionaries with native types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_data = []
    for _, row in df.iterrows():
        # Get raw numeric values (use float to ensure true division)
        cfo = float(row["CFO"]) if not pd.isna(row["CFO"]) else None
        ni = float(row["Net Income"]) if not pd.isna(row["Net Income"]) else None
        total_assets = float(row["Total Assets"]) if not pd.isna(row["Total Assets"]) else None

        if total_assets in (None, 0):
            spread = None
        else:
            # compute spread dynamically
            spread = (cfo / total_assets) - (ni / total_assets)

        entry = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(spread) if spread is not None else None
        }
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()