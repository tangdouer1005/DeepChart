#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,9795000000,7017000000,122679000000,117031000000.0,0.0836957729148687,0.0599584725414633
2017,13596000000,10558000000,139057000000,130868000000.0,0.1038909435461686,0.0806767124125072
2018,15713000000,11986000000,152221000000,145639000000.0,0.1078900569215663,0.0822993840935463
2019,18463000000,13839000000,173889000000,163055000000.0,0.1132317316242985,0.0848732022937045
2020,22174000000,15403000000,197289000000,185589000000.0,0.1194790639531437,0.0829952206219118
2021,22343000000,17285000000,212206000000,204747500000.0,0.1091246535366732,0.0844210552021392
2022,26206000000,20120000000,245705000000,228955500000.0,0.1144589232405423,0.0878773386094677
2023,29068000000,22381000000,273720000000,259712500000.0,0.1119237618520479,0.0861760600664196
2024,24204000000,14405000000,298278000000,285999000000.0,0.0846296665372955,0.0503673089766048
"""

def to_py_type(val):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data as list of dicts with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_type(row[col])
        scr_records.append(rec)

    # Calculate 盈余-现金质量剪刀差 (Earnings Quality Spread)
    indicator_name = "盈余-现金质量剪刀差 (Earnings Quality Spread)"
    der_records = []
    for _, row in df.iterrows():
        # Use CFO and Total Assets and Net Income per the definition:
        # Spread = (CFO / Total Assets) - (Net Income / Total Assets)
        # Compute in a numerically stable way: (CFO - Net Income) / Total Assets
        cfo = float(row["CFO"]) if not pd.isna(row["CFO"]) else None
        ni = float(row["Net Income"]) if not pd.isna(row["Net Income"]) else None
        ta = float(row["Total Assets"]) if not pd.isna(row["Total Assets"]) else None

        if (cfo is None) or (ni is None) or (ta is None) or ta == 0:
            spread = None
        else:
            spread = (cfo - ni) / ta

        rec = {
            "Fiscal Year": to_py_type(row["Fiscal Year"]),
            indicator_name: to_py_type(spread)
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with non-ASCII characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()