#!/usr/bin/env python3
import sys
import io
import pandas as pd
import json
import numbers

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,1160000000,14178000000,7070000000,21248000000
2017,6554000000,-2739000000,6194000000,3455000000
2018,4978000000,6761000000,6582000000,13343000000
2019,8772000000,5151000000,3541000000,8692000000
2020,3597000000,409000000,3464000000,3873000000
2021,3332000000,1058000000,2360000000,3418000000
2022,5916000000,1858000000,2902000000,4760000000
2023,5179000000,4717000000,1179000000,5896000000
2024,4710000000,6761000000,1184000000,7945000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_native(val):
    if pd.isna(val):
        return None
    if isinstance(val, (pd.Timestamp,)):
        return str(val)
    if isinstance(val, numbers.Integral):
        return int(val)
    if isinstance(val, numbers.Real):
        return float(val)
    # fallback
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    # We'll compute denominator as Operating Income + D&A per specification.
    # Use the explicit columns from CSV.
    # If Operating Income or D&A are missing, fallback to using the provided Denominator column.
    denom_col = "Denominator (OpInc+D&A)"
    opinc_col = "Operating Income"
    da_col = "D&A"

    # Compute denominator robustly
    if opinc_col in df.columns and da_col in df.columns:
        df["_computed_denominator"] = df[opinc_col].astype(float) + df[da_col].astype(float)
    else:
        # fallback to provided denominator column if available
        if denom_col in df.columns:
            df["_computed_denominator"] = df[denom_col].astype(float)
        else:
            # If none available, set denominator to NaN
            df["_computed_denominator"] = float("nan")

    # Compute the Quality of Income Ratio: CFO / (Operating Income + D&A)
    df["_quality_ratio"] = df["CFO"].astype(float) / df["_computed_denominator"]

    # Prepare scr_data: raw rows as in CSV (use original column names)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            # Exclude internal computed columns from scr_data
            if col.startswith("_"):
                continue
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Prepare der_data: one entry per row with Fiscal Year (if present) and the calculated indicator
    der_records = []
    for _, row in df.iterrows():
        rec = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        # include the dynamically computed value (must not be hardcoded)
        rec[INDICATOR_NAME] = to_native(row["_quality_ratio"])
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()