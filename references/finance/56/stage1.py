#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2016,1672081000,-47426000,12762920000,11727951000.0,0.1425723044033864,-0.0040438436347491
2017,2162198000,323000000,17584923000,15173921500.0,0.1424943446557305,0.0212865210881709
2018,2737965000,127478000,21009802000,19297362500.0,0.1418828609350112,0.0066059804804931
2019,3398000000,1110000000,30737000000,25873401000.0,0.1313317874213753,0.0429012018945634
2020,4331000000,126000000,55126000000,42931500000.0,0.1008816370264258,0.0029349079347332
2021,4801000000,4072000000,66301000000,60713500000.0,0.0790763174582259,0.0670691032472184
2022,6000000000,1444000000,95209000000,80755000000.0,0.0742988050275524,0.0178812457432976
2023,7111000000,208000000,98849000000,97029000000.0,0.0732873676941945,0.0021436890001958
2024,10234000000,4136000000,99823000000,99336000000.0,0.1030240798904727,0.0416364661351373
"""

def to_native(value):
    if pd.isna(value):
        return None
    # Convert numpy types to native Python types
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (int, float, str, bool)):
        return value
    # fallback
    try:
        return int(value)
    except Exception:
        try:
            return float(value)
        except Exception:
            return value

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: original rows with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate 盈余-现金质量剪刀差 (Earnings Quality Spread)
    metric_name = "盈余-现金质量剪刀差 (Earnings Quality Spread)"
    der_records = []
    for _, row in df.iterrows():
        # Ensure we use float division
        cfo = float(row["CFO"])
        ni = float(row["Net Income"])
        total_assets = float(row["Total Assets"])
        # Avoid division by zero
        if total_assets == 0:
            spread = None
        else:
            spread = (cfo / total_assets) - (ni / total_assets)
        rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            metric_name: to_native(spread) if spread is not None else None
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()