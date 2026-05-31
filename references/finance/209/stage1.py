#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,13561000000,12604000000,2509000000,15113000000
2017,14126000000,12913000000,2451000000,15364000000
2018,15386000000,13264000000,2785000000,16049000000
2019,14551000000,13535000000,2919000000,16454000000
2020,13139000000,13896000000,2968000000,16864000000
2021,15887000000,15213000000,2916000000,18129000000
2022,9539000000,10926000000,3122000000,14048000000
2023,17165000000,13093000000,6108000000,19201000000
2024,18673000000,15353000000,6139000000,21492000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_native(val):
    # Convert numpy / pandas scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    # for python built-in numeric types or strings
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required columns exist
    required_cols = ["Fiscal Year", "CFO", "Operating Income", "D&A"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' not found in input data")

    # Calculate denominator as Operating Income + D&A (do not use precomputed Denominator column)
    df["Calculated_Denominator"] = df["Operating Income"] + df["D&A"]

    # Calculate the Quality of Income Ratio per provided formula:
    # Ratio = CFO / (Operating Income + D&A)
    def compute_ratio(cfo, denom):
        try:
            if pd.isna(cfo) or pd.isna(denom):
                return None
            denom_val = float(denom)
            if denom_val == 0:
                return None
            return float(cfo) / denom_val
        except Exception:
            return None

    df["Quality_of_Income_Ratio"] = df.apply(
        lambda row: compute_ratio(row["CFO"], row["Calculated_Denominator"]), axis=1
    )

    # Prepare scr_data: original CSV rows (keep original columns)
    scr_data = []
    for _, row in df.iterrows():
        entry = {}
        for col in ["Fiscal Year", "CFO", "Operating Income", "D&A", "Denominator (OpInc+D&A)"]:
            # Some rows may not have the 'Denominator (OpInc+D&A)' if CSV changed; handle gracefully
            if col in df.columns:
                entry[col] = to_native(row[col])
        scr_data.append(entry)

    # Prepare der_data: each entry contains Fiscal Year and the calculated indicator
    der_data = []
    for _, row in df.iterrows():
        yr = to_native(row["Fiscal Year"])
        ratio = row["Quality_of_Income_Ratio"]
        # Optionally round ratio to a reasonable number of decimals for readability
        ratio_native = None if ratio is None else float(round(ratio, 6))
        der_entry = {
            "Fiscal Year": yr,
            INDICATOR_NAME: ratio_native
        }
        der_data.append(der_entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()