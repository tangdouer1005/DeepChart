#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,16540000000,726000000,3263000000,3754000000
2017,1300000000,934000000,16373000000,5642000000
2018,15297000000,1005000000,2702000000,6929000000
2019,15119000000,318000000,2209000000,7009000000
2020,14714000000,201000000,1783000000,7231000000
2021,20878000000,183000000,1377000000,7390000000
2022,17941000000,276000000,2989000000,6970000000
2023,35153000000,1247000000,1736000000,7486000000
2024,14066000000,755000000,2621000000,7339000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def convert_numpy(v):
    # Convert numpy types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # if it's a whole number, cast to int to be tidy, else float
        if float(v).is_integer():
            return int(v)
        return float(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows with native Python types
    raw_records = df.to_dict(orient="records")
    scr_data = []
    for rec in raw_records:
        cleaned = {}
        for k, v in rec.items():
            cleaned[k] = convert_numpy(v)
        scr_data.append(cleaned)

    # Calculate EBITDA per row:
    der_data = []
    for idx, row in df.iterrows():
        # Extract required fields using header names from CSV
        ni = row["Net Income"]
        interest = row["Interest Expense"]
        tax = row["Income Tax"]
        da = row["Depreciation & Amortization"]

        # Ensure numeric and handle missing gracefully
        def to_num(x):
            if pd.isna(x):
                return 0
            return int(x) if float(x).is_integer() else float(x)

        ni_n = to_num(ni)
        interest_n = to_num(interest)
        tax_n = to_num(tax)
        da_n = to_num(da)

        ebitda = ni_n + interest_n + tax_n + da_n

        entry = {
            "Fiscal Year": convert_numpy(row["Fiscal Year"]),
            INDICATOR_NAME: convert_numpy(ebitda)
        }
        der_data.append(entry)

    out_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()