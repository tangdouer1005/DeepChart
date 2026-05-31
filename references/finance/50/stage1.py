#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,3292000000,3672000000,1255000000,4927000000
2017,6726000000,4111000000,1370000000,5481000000
2018,5774000000,4480000000,1437000000,5917000000
2019,6356000000,4737000000,1492000000,6229000000
2020,8861000000,5435000000,1839000000,7274000000
2021,8958000000,6708000000,2067000000,8775000000
2022,7392000000,7793000000,2277000000,10070000000
2023,11068000000,8114000000,2489000000,10603000000
2024,11339000000,9285000000,2237000000,11522000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_native(v):
    # Convert pandas/numpy scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (int, float, str, bool)):
        return v
    # For any other types (e.g., numpy types), try direct cast
    try:
        return int(v)
    except Exception:
        try:
            return float(v)
        except Exception:
            return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    for col in ["CFO", "Operating Income", "D&A"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculation:
    # Ratio = CFO / (Operating Income + D&A)
    # If denominator is zero or NaN, result will be set to None
    denom = df["Operating Income"] + df["D&A"]
    ratio_series = []
    for cfo, d in zip(df["CFO"], denom):
        if pd.isna(cfo) or pd.isna(d) or d == 0:
            ratio_series.append(None)
        else:
            # Compute as float
            ratio_series.append(float(cfo) / float(d))

    # Prepare scr_data (raw input rows) ensuring native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Prepare der_data with calculated indicator per row; include Fiscal Year if present
    der_records = []
    for idx, ratio in enumerate(ratio_series):
        rec = {}
        # include year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(df.at[idx, "Fiscal Year"])
        # add the calculated indicator value
        rec[INDICATOR_NAME] = to_native(ratio)
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output file with ensure_ascii=False to keep Chinese text readable
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()