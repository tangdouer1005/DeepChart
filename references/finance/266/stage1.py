#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,5574000000,5991000000,64035000000,51701000000.0,0.1078122280033268,0.1158778360186456
2017,9208000000,6699000000,67977000000,66006000000.0,0.1395024694724722,0.1014907735660394
2018,12713000000,10301000000,69225000000,68601000000.0,0.1853179982799084,0.1501581609597527
2019,12784000000,12080000000,72574000000,70899500000.0,0.1803115677825654,0.1703820196193203
2020,10440000000,10866000000,80919000000,76746500000.0,0.1360322620575531,0.1415830037851889
2021,15227000000,12311000000,82896000000,81907500000.0,0.1859048316698715,0.1503036962427128
2022,18849000000,14957000000,85501000000,84198500000.0,0.2238638455554434,0.1776397441759651
2023,20755000000,17273000000,90499000000,88000000000.0,0.2358522727272727,0.1962840909090909
2024,19950000000,19743000000,94511000000,92505000000.0,0.2156640181611804,0.2134263012810118
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def to_native(value):
    if pd.isnull(value):
        return None
    # numpy integer types
    if isinstance(value, (np.integer,)):
        return int(value)
    # numpy floating types
    if isinstance(value, (np.floating,)):
        return float(value)
    # pandas Timestamps etc -> string
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data from input CSV (convert to native python types)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate Earnings Quality Spread per row:
    # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
    der_records = []
    for _, row in df.iterrows():
        total_assets = row.get("Total Assets", None)
        cfo = row.get("CFO", None)
        ni = row.get("Net Income", None)

        spread_value = None
        try:
            if total_assets is not None and total_assets != 0:
                spread_value = (float(cfo) / float(total_assets)) - (float(ni) / float(total_assets))
            else:
                spread_value = None
        except Exception:
            spread_value = None

        rec = {}
        # include the year field if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        rec[INDICATOR_NAME] = to_native(spread_value)
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()