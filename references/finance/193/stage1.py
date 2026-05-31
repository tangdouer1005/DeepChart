#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,614000000,47000000,129000000,197000000
2017,1666000000,58000000,239000000,187000000
2018,3047000000,61000000,149000000,199000000
2019,4141000000,58000000,245000000,262000000
2020,2796000000,52000000,174000000,381000000
2021,4332000000,184000000,77000000,1098000000
2022,9752000000,236000000,189000000,1174000000
2023,4368000000,262000000,187000000,1543000000
2024,29760000000,257000000,4058000000,1508000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_python_scalar(v):
    # Convert pandas / numpy scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.generic,)):
        return v.item()
    # For plain Python types or strings
    return v

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric columns to numeric types where possible
    # This helps ensure arithmetic works correctly
    numeric_cols = ["Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Prepare scr_data: original rows as list of dicts with Python native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_scalar(row[col])
        scr_records.append(rec)

    # Calculate EBITDA for each row dynamically
    der_records = []
    for _, row in df.iterrows():
        # Safely extract numeric components; treat missing as 0 for calculation if necessary
        net_income = row.get("Net Income", 0)
        interest = row.get("Interest Expense", 0)
        income_tax = row.get("Income Tax", 0)
        da = row.get("Depreciation & Amortization", 0)

        # Ensure numeric types (NaN -> 0)
        net_income = 0 if pd.isna(net_income) else int(net_income)
        interest = 0 if pd.isna(interest) else int(interest)
        income_tax = 0 if pd.isna(income_tax) else int(income_tax)
        da = 0 if pd.isna(da) else int(da)

        # EBITDA calculation (dynamic, not hardcoded)
        ebitda = net_income + interest + income_tax + da

        der_rec = {
            "Fiscal Year": int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None,
            INDICATOR_NAME: ebitda
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()