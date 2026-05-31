#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,7017000000,1067000000,4790000000,2055000000
2017,10558000000,1186000000,3200000000,2245000000
2018,11986000000,1400000000,3562000000,2428000000
2019,13839000000,1704000000,3742000000,2720000000
2020,15403000000,1663000000,4973000000,2891000000
2021,17285000000,1660000000,4578000000,3103000000
2022,20120000000,2092000000,5704000000,3400000000
2023,22381000000,3246000000,5968000000,3972000000
2024,14405000000,3906000000,4829000000,4099000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_python_scalar(value):
    # Convert numpy / pandas scalar types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    try:
        if hasattr(value, 'item'):
            return value.item()
    except Exception:
        pass
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculate EBITDA per reference:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
    # Use column names exactly as in the CSV.
    required_cols = ["Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required column missing from CSV data: {col}")

    df[INDICATOR_NAME] = (
        df["Net Income"]
        + df["Interest Expense"]
        + df["Income Tax"]
        + df["Depreciation & Amortization"]
    )

    # Prepare scr_data: original input rows (preserve original column names)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in ["Fiscal Year"] + required_cols:
            # convert to native types
            rec[col] = to_python_scalar(row[col])
        scr_records.append(rec)

    # Prepare der_data: one dict per row with Fiscal Year and calculated indicator
    der_records = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": to_python_scalar(row["Fiscal Year"]),
            INDICATOR_NAME: to_python_scalar(row[INDICATOR_NAME]),
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()