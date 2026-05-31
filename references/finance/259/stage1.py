#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,9795000000,12930000000,2055000000,14985000000
2017,13596000000,15209000000,2245000000,17454000000
2018,15713000000,17344000000,2428000000,19772000000
2019,18463000000,19685000000,2720000000,22405000000
2020,22174000000,22405000000,2891000000,25296000000
2021,22343000000,23970000000,3103000000,27073000000
2022,26206000000,28435000000,3400000000,31835000000
2023,29068000000,32358000000,3972000000,36330000000
2024,24204000000,32287000000,4099000000,36386000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_native(val):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if pd.isna(val):
        return None
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    output_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["CFO", "Operating Income", "D&A", "Denominator (OpInc+D&A)"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate denominator as Operating Income + D&A to follow the formula.
    # Although a Denominator column exists, compute it to ensure correctness.
    df["computed_denominator"] = df["Operating Income"] + df["D&A"]

    # Calculate the Quality of Income Ratio: CFO / (Operating Income + D&A)
    def compute_ratio(row):
        denom = row["computed_denominator"]
        cfo = row["CFO"]
        if pd.isna(denom) or denom == 0 or pd.isna(cfo):
            return None
        return float(cfo) / float(denom)

    df["quality_of_income_ratio"] = df.apply(compute_ratio, axis=1)

    # Prepare scr_data: mirror input CSV rows (convert types to native)
    scr_data = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            "CFO": to_native(row["CFO"]),
            "Operating Income": to_native(row["Operating Income"]),
            "D&A": to_native(row["D&A"]),
            "Denominator (OpInc+D&A)": to_native(row["Denominator (OpInc+D&A)"]),
        }
        scr_data.append(rec)

    # Prepare der_data: calculated indicator per row
    der_data = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(row["quality_of_income_ratio"]),
        }
        der_data.append(rec)

    out_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()