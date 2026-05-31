#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,13561000000,8901000000,112180000000,111541500000.0,0.1215780673560961,0.0797998951063057
2017,14126000000,9452000000,134991000000,123585500000.0,0.1143014350389002,0.0764814642494467
2018,15386000000,3587000000,137264000000,136127500000.0,0.1130263906998953,0.0263502965969403
2019,14551000000,11083000000,108709000000,122986500000.0,0.1183137986689596,0.0901155817914974
2020,13139000000,10135000000,115438000000,112073500000.0,0.1172355641610193,0.0904317256086407
2021,15887000000,13746000000,131107000000,123272500000.0,0.1288770812630554,0.1115090551420633
2022,9539000000,6717000000,109297000000,120202000000.0,0.0793580805643832,0.0558809337615014
2023,17165000000,8503000000,134384000000,121840500000.0,0.1408809057743525,0.0697879604893282
2024,18673000000,10467000000,140976000000,137680000000.0,0.1356260894828588,0.0760241138872748
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_native(value):
    """Convert numpy/pandas scalar types to native Python types for JSON serialization."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    # For other types (e.g., python int/float/str) return as-is
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows as JSON-serializable dicts
    scr_data = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            row_dict[col] = to_native(row[col])
        scr_data.append(row_dict)

    # Calculate Earnings Quality Spread for each row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_data = []
    for _, row in df.iterrows():
        cfo = row["CFO"]
        net_income = row["Net Income"]
        total_assets = row["Total Assets"]

        # Guard against division by zero
        if total_assets == 0 or pd.isna(total_assets):
            spread = None
        else:
            spread = (float(cfo) / float(total_assets)) - (float(net_income) / float(total_assets))

        entry = {}
        # include year if present
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = to_native(row["Fiscal Year"])
        entry[INDICATOR_NAME] = to_native(spread)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file with UTF-8 and Chinese preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()