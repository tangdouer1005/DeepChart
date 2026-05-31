#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,-123829000,-667340000,947099000,279759000
2017,-61000000,-1632000000,1636000000,4000000
2018,2098000000,-388000000,1901000000,1513000000
2019,2405000000,-69000000,2154000000,2085000000
2020,5943000000,1994000000,2322000000,4316000000
2021,11497000000,6687000000,2911000000,9598000000
2022,14724000000,13656000000,3543000000,17199000000
2023,13256000000,8891000000,4667000000,13558000000
2024,14923000000,7076000000,5368000000,12444000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_native(val):
    """Convert numpy/pandas scalar types to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # convert to float but avoid NaN/inf
        f = float(val)
        if np.isinf(f) or np.isnan(f):
            return None
        return f
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure expected columns exist
    # Denominator should be Operating Income + D&A. Use provided Denominator if present, otherwise compute.
    denom_col = None
    if "Denominator (OpInc+D&A)" in df.columns:
        denom_col = "Denominator (OpInc+D&A)"
    else:
        # fallback: compute denominator
        df["Denominator (OpInc+D&A)"] = df["Operating Income"] + df["D&A"]
        denom_col = "Denominator (OpInc+D&A)"

    # Calculate the Quality of Income Ratio for each row:
    # Ratio = CFO / (Operating Income + D&A)
    ratios = []
    for _, row in df.iterrows():
        cfo = row.get("CFO", None)
        denom = row.get(denom_col, None)

        # Handle missing or zero denominator safely
        if pd.isna(cfo) or pd.isna(denom) or denom == 0:
            ratio = None
        else:
            try:
                ratio = float(cfo) / float(denom)
                if np.isinf(ratio) or np.isnan(ratio):
                    ratio = None
            except Exception:
                ratio = None

        ratios.append(ratio)

    # Prepare scr_data (raw input rows) converting numpy types to native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Prepare der_data with calculated indicator values. Include Fiscal Year if present.
    der_records = []
    for idx, ratio in enumerate(ratios):
        rec = {}
        # include year if present in input
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(df.at[idx, "Fiscal Year"])
        rec[INDICATOR_NAME] = to_native(ratio)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()