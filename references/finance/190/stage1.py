#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,-1473984000,379793000,4924978000,5304771000
2017,-1785948000,838679000,6269728000,7108407000
2018,-2680479000,1605226000,7615245000,9220471000
2019,-2887322000,2604254000,9319826000,11924080000
2020,2427077000,4585289000,10922622000,15507911000
2021,392610000,6194509000,12438779000,18633288000
2022,2026257000,5632831000,14362814000,19995645000
2023,7274301000,6954003000,14554384000,21508387000
2024,7361364000,10417614000,15630431000,26048045000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_native(val):
    """Convert numpy/pandas types to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    for col in ["CFO", "Operating Income", "D&A"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Build scr_data: raw input rows as list of dicts with native types
    raw_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        raw_records.append(rec)

    # Calculate the Quality of Income Ratio for each row:
    # Ratio = CFO / (Operating Income + D&A)
    der_records = []
    for _, row in df.iterrows():
        fy_key = "Fiscal Year"
        fy_val = to_native(row.get(fy_key)) if fy_key in df.columns else None

        op_inc = row.get("Operating Income", None)
        da = row.get("D&A", None)
        cfo = row.get("CFO", None)

        # Compute denominator dynamically (do not rely solely on provided Denominator column)
        denom = None
        if pd.notna(op_inc) and pd.notna(da):
            denom = op_inc + da
        elif "Denominator (OpInc+D&A)" in df.columns and pd.notna(row.get("Denominator (OpInc+D&A)")):
            denom = row.get("Denominator (OpInc+D&A)")

        ratio = None
        # Only compute when CFO and denominator are valid numbers and denominator is non-zero
        if pd.notna(cfo) and denom is not None and denom != 0:
            ratio = float(cfo) / float(denom)
        else:
            ratio = None

        entry = {}
        if fy_val is not None:
            entry[fy_key] = fy_val
        entry[INDICATOR_NAME] = to_native(ratio)
        der_records.append(entry)

    output_obj = {
        "scr_data": raw_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()