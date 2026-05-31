#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,12846000000,-5471000000,16011000000,10540000000
2017,20338000000,3128000000,17858000000,20986000000
2018,30618000000,14446000000,18717000000,33163000000
2019,27300000000,100000000,17965000000,18065000000
2020,10600000000,-6942000000,17192000000,10250000000
2021,29200000000,16104000000,17013000000,33117000000
2022,49600000000,50190000000,16300000000,66490000000
2023,35609000000,33790000000,17762000000,51552000000
2024,31492000000,29099000000,17711000000,46810000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_native_value(v):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # convert to regular float
        return float(v)
    # pandas may use numpy types for booleans as well
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def df_to_native_records(df):
    records = []
    for row in df.to_dict(orient="records"):
        native_row = {}
        for k, v in row.items():
            native_row[k] = to_native_value(v)
        records.append(native_row)
    return records

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["CFO", "Operating Income", "D&A", "Denominator (OpInc+D&A)"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate the Quality of Income Ratio for each row:
    # Ratio = CFO / (Operating Income + D&A)
    # We'll compute denominator dynamically as Operating Income + D&A to follow the formula.
    denom_computed = df["Operating Income"] + df["D&A"]
    # Avoid division by zero; where denominator is zero or NaN, result will be None (null in JSON)
    ratios = []
    for idx, row in df.iterrows():
        cfo = row["CFO"]
        opinc = row["Operating Income"]
        da = row["D&A"]
        denom = denom_computed.iloc[idx]
        if pd.isna(cfo) or pd.isna(denom) or denom == 0:
            ratio = None
        else:
            # compute as float
            ratio = float(cfo) / float(denom)
        ratios.append(ratio)

    # Prepare scr_data (original data) and der_data (derived indicator)
    scr_data = df_to_native_records(df)

    der_data = []
    for idx, row in df.iterrows():
        entry = {}
        # Include Year if present
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = to_native_value(row["Fiscal Year"])
        entry[INDICATOR_NAME] = to_native_value(ratios[idx])
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified output path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()