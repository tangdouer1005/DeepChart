#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,20539000000,1243000000,5100000000,6622000000
2017,25489000000,2222000000,4412000000,8778000000
2018,16571000000,2733000000,19903000000,10261000000
2019,39240000000,2686000000,4448000000,11682000000
2020,44281000000,2591000000,8755000000,12796000000
2021,61271000000,2346000000,9831000000,11686000000
2022,72738000000,2063000000,10978000000,14460000000
2023,72361000000,1968000000,16950000000,13861000000
2024,88136000000,2935000000,19651000000,22287000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def scalar_to_python(val):
    # Convert pandas / numpy scalars to native Python types for JSON serialization
    try:
        # numpy scalars and pandas scalars have .item()
        return val.item()
    except Exception:
        # fallback: return as-is (strings etc.)
        return val

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: mirror input rows
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            v = row[col]
            if pd.isna(v):
                rec[col] = None
            else:
                rec[col] = scalar_to_python(v)
        scr_data.append(rec)

    # Calculate EBITDA per provided formula:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
    der_data = []
    for _, row in df.iterrows():
        ni = row["Net Income"]
        interest = row["Interest Expense"]
        tax = row["Income Tax"]
        da = row["Depreciation & Amortization"]

        # Ensure numeric addition (pandas/numpy scalars are fine)
        ebitda = ni + interest + tax + da

        # Build output record. Include Fiscal Year to link rows.
        rec = {
            "Fiscal Year": scalar_to_python(row["Fiscal Year"]),
            INDICATOR_NAME: scalar_to_python(ebitda)
        }
        der_data.append(rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()