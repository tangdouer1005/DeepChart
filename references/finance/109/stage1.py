#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,9373000000,11774000000,1863000000,13637000000
2017,9783000000,13427000000,1973000000,15400000000
2018,12031000000,14681000000,2062000000,16743000000
2019,13165000000,15530000000,2152000000,17682000000
2020,13723000000,15843000000,2296000000,18139000000
2021,18839000000,18278000000,2519000000,20797000000
2022,16571000000,23040000000,2862000000,25902000000
2023,14615000000,24039000000,2975000000,27014000000
2024,21172000000,21689000000,3247000000,24936000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def scalar_to_builtin(v):
    """Convert numpy scalars to native Python types for JSON serialization."""
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required columns exist
    required_cols = ["Fiscal Year", "CFO", "Operating Income", "D&A"]
    for col in required_cols:
        if col not in df.columns:
            print(f"Missing required column in CSV: {col}", file=sys.stderr)
            sys.exit(1)

    # Compute denominator dynamically as (Operating Income + D&A)
    df["Computed Denominator"] = df["Operating Income"] + df["D&A"]

    # Compute the Quality of Income Ratio = CFO / (Operating Income + D&A)
    # If denominator is zero or missing, set ratio as None
    def compute_ratio(row):
        denom = row["Computed Denominator"]
        cfo = row["CFO"]
        try:
            if pd.isna(denom) or denom == 0:
                return None
            return float(cfo) / float(denom)
        except Exception:
            return None

    df[INDICATOR_NAME] = df.apply(compute_ratio, axis=1)

    # Prepare scr_data: original CSV rows (use original headers)
    scr_records = []
    for rec in df[["Fiscal Year", "CFO", "Operating Income", "D&A", "Denominator (OpInc+D&A)"]].to_dict(orient="records"):
        converted = {k: scalar_to_builtin(v) for k, v in rec.items()}
        scr_records.append(converted)

    # Prepare der_data: one dict per row with Fiscal Year and the calculated indicator
    der_records = []
    for rec in df[["Fiscal Year", INDICATOR_NAME]].to_dict(orient="records"):
        # Convert values to native types
        fiscal = scalar_to_builtin(rec.get("Fiscal Year"))
        val = scalar_to_builtin(rec.get(INDICATOR_NAME))
        der_entry = {"Fiscal Year": fiscal, INDICATOR_NAME: val}
        der_records.append(der_entry)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()