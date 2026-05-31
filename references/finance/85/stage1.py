#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,7500000000,5024000000,1133000000,7070000000
2017,-8484000000,4655000000,2808000000,6194000000
2018,-22355000000,4766000000,93000000,6582000000
2019,-4979000000,2927000000,552000000,3541000000
2020,5704000000,3515000000,487000000,3464000000
2021,-6337000000,1790000000,757000000,2360000000
2022,292000000,1477000000,476000000,2902000000
2023,9482000000,1029000000,994000000,1179000000
2024,6556000000,986000000,962000000,1184000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_python_scalar(val):
    """Convert numpy/pandas scalar to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # If the float is actually an integer value, return int to avoid decimals like 1.0
        if float(val).is_integer():
            return int(val)
        return float(val)
    if isinstance(val, (int, float, str, bool)):
        return val
    # Fallback: try to convert
    try:
        return int(val)
    except Exception:
        try:
            return float(val)
        except Exception:
            return str(val)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts reflecting the original CSV rows
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_scalar(row[col])
        scr_records.append(rec)

    # Calculate EBITDA per row dynamically using the provided formula:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
    der_records = []
    for _, row in df.iterrows():
        # Retrieve raw components; use 0 if missing (though CSV has values)
        ni = row.get("Net Income", 0)
        interest = row.get("Interest Expense", 0)
        tax = row.get("Income Tax", 0)
        da = row.get("Depreciation & Amortization", 0)

        # Ensure numeric computation using numpy/pandas types; result will be converted
        ebitda_val = ni + interest + tax + da

        der_rec = {
            "Fiscal Year": to_python_scalar(row.get("Fiscal Year")),
            INDICATOR_NAME: to_python_scalar(ebitda_val)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified file path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()