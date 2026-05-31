#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,1460000000,1730000000,867000000,6243000000
2017,4536000000,1671000000,1375000000,5984000000
2018,2888000000,1357000000,1029000000,6486000000
2019,3468000000,1135000000,1135000000,6616000000
2020,3064000000,2701000000,786000000,14151000000
2021,3024000000,3342000000,327000000,16383000000
2022,2590000000,3364000000,556000000,13651000000
2023,8317000000,3335000000,2682000000,12818000000
2024,11339000000,3411000000,3373000000,12919000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_native(x):
    """Convert numpy/pandas scalars to native Python types for JSON serialization."""
    if pd.isna(x):
        return None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        # If it's integer-valued float, return int
        if float(x).is_integer():
            return int(x)
        return float(x)
    return x

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: original rows with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate EBITDA per row dynamically:
    der_records = []
    for _, row in df.iterrows():
        # Extract components (assume present and numeric)
        ni = row["Net Income"]
        ie = row["Interest Expense"]
        tax = row["Income Tax"]
        da = row["Depreciation & Amortization"]

        # Ensure numeric types (cast to int when possible)
        # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
        ebitda = ni + ie + tax + da

        der_rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(ebitda)
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, separators=(",", ":"))

if __name__ == "__main__":
    main()