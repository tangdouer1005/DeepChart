#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,186678000,150114000,73829000,4924978000
2017,558929000,353358000,73608000,6269728000
2018,1211242000,420493000,15216000,7615245000
2019,1866916000,626023000,195315000,9319826000
2020,2761395000,1385940000,437954000,10922622000
2021,5116228000,765620000,723875000,12438779000
2022,4491924000,706212000,772005000,14362814000
2023,5407990000,699826000,797415000,14554384000
2024,8711631000,718733000,1254026000,15630431000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_native(val):
    """
    Convert pandas / numpy scalar types to native Python types safe for JSON serialization.
    """
    # Handle missing values
    if pd.isna(val):
        return None
    # If it's a numpy/pandas scalar, .item() will produce a native python type
    try:
        if hasattr(val, "item"):
            val = val.item()
    except Exception:
        pass
    # If it's a float that's actually an integer value, convert to int
    if isinstance(val, float):
        if val.is_integer():
            return int(val)
        return float(val)
    # Other types (int, str, etc.) are fine
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(2)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure columns we need exist
    required_cols = ["Fiscal Year", "Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for col in required_cols:
        if col not in df.columns:
            print(f"Missing required column in CSV: {col}", file=sys.stderr)
            sys.exit(3)

    # Prepare scr_data: original rows with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate EBITDA for each row dynamically
    der_records = []
    for _, row in df.iterrows():
        ni = row["Net Income"]
        interest = row["Interest Expense"]
        tax = row["Income Tax"]
        da = row["Depreciation & Amortization"]

        # Compute EBITDA according to reference:
        # EBITDA = Net Income + Interest Expense + Income Tax Expense + Depreciation + Amortization
        ebitda = ni + interest + tax + da

        der_rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(ebitda)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output file path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()