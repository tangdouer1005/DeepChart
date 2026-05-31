#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,7009000000,919000000,4012000000,1863000000
2017,7957000000,972000000,4534000000,1973000000
2018,8630000000,1057000000,5068000000,2062000000
2019,11121000000,1051000000,3435000000,2152000000
2020,11242000000,1201000000,3473000000,2296000000
2021,12866000000,1347000000,4112000000,2519000000
2022,16433000000,1347000000,5304000000,2862000000
2023,17105000000,1617000000,5372000000,2975000000
2024,15143000000,1943000000,4781000000,3247000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_native(value):
    """
    Convert numpy / pandas types to native Python types for JSON serialization.
    """
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        # If it's a whole number, keep as int to match original precision
        if value.is_integer():
            return int(value)
        return float(value)
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype={
        "Fiscal Year": int,
        "Net Income": np.float64,
        "Interest Expense": np.float64,
        "Income Tax": np.float64,
        "Depreciation & Amortization": np.float64
    })

    # Prepare scr_data: raw rows as list of dicts with native Python types
    raw_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        raw_records.append(rec)

    # Calculate EBITDA for each row dynamically
    derived_records = []
    for _, row in df.iterrows():
        net_income = row["Net Income"]
        interest = row["Interest Expense"]
        income_tax = row["Income Tax"]
        da = row["Depreciation & Amortization"]

        # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation + Amortization
        ebitda = net_income + interest + income_tax + da

        derived_rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(ebitda)
        }
        derived_records.append(derived_rec)

    output_obj = {
        "scr_data": raw_records,
        "der_data": derived_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()