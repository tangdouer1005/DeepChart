#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

def to_native(x):
    if pd.isna(x):
        return None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    # bools, strs, ints, floats pass through
    return x

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    csv_data = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,5574000000,7883000000,502000000,8385000000
2017,9208000000,12144000000,556000000,12700000000
2018,12713000000,12954000000,613000000,13567000000
2019,12784000000,15001000000,656000000,15657000000
2020,10440000000,14081000000,767000000,14848000000
2021,15227000000,15804000000,804000000,16608000000
2022,18849000000,18813000000,861000000,19674000000
2023,20755000000,21000000000,943000000,21943000000
2024,19950000000,23595000000,1034000000,24629000000
"""

    df = pd.read_csv(io.StringIO(csv_data))

    # Calculate denominator as Operating Income + D&A (more robust than using provided Denominator column)
    # and then compute Quality of Income Ratio = CFO / (Operating Income + D&A)
    # Handle division by zero by returning None (which becomes null in JSON)
    op_inc_col = "Operating Income"
    da_col = "D&A"
    cfo_col = "CFO"
    year_col = "Fiscal Year"
    indicator_name = "自由现金流收益质量 (Quality of Income Ratio)"

    # Ensure numeric types
    df[cfo_col] = pd.to_numeric(df[cfo_col], errors="coerce")
    df[op_inc_col] = pd.to_numeric(df[op_inc_col], errors="coerce")
    df[da_col] = pd.to_numeric(df[da_col], errors="coerce")

    denom = df[op_inc_col] + df[da_col]

    ratios = []
    for idx, row in df.iterrows():
        cfo = row[cfo_col]
        d = denom.iloc[idx]
        if pd.isna(cfo) or pd.isna(d) or d == 0:
            val = None
        else:
            # compute as float
            val = float(cfo) / float(d)
        ratios.append(val)

    # Build scr_data from original CSV rows, converting numpy types to native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        # Also include the provided Denominator column if present in CSV (it is)
        scr_data.append(rec)

    # Build der_data aligned with scr_data rows
    der_data = []
    for i, row in df.iterrows():
        entry = {
            year_col: to_native(row[year_col]),
            indicator_name: to_native(ratios[i])
        }
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output path with UTF-8 and preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()