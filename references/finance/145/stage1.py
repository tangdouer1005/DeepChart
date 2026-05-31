#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,4059000000,95000000,1587000000,373000000
2017,3915000000,154000000,2607000000,437000000
2018,5859000000,186000000,1345000000,459000000
2019,8118000000,224000000,1613000000,522000000
2020,6411000000,380000000,1349000000,580000000
2021,8687000000,431000000,1620000000,726000000
2022,9930000000,471000000,1802000000,750000000
2023,11195000000,575000000,2444000000,799000000
2024,12874000000,646000000,2380000000,897000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_python_native(value):
    """
    Convert numpy / pandas scalar types to native Python types for JSON serialization.
    """
    if pd.isna(value):
        return None
    if isinstance(value, (np.generic,)):
        return value.item()
    # builtin types (int, float, str, bool)
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculate EBITDA per formula:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
    # Ensure columns exist
    required_cols = ["Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required column missing: {col}")

    df["EBITDA"] = (
        df["Net Income"].astype(float)
        + df["Interest Expense"].astype(float)
        + df["Income Tax"].astype(float)
        + df["Depreciation & Amortization"].astype(float)
    )

    # Prepare scr_data: original rows as dictionaries with original column names
    scr_data = []
    for _, row in df.drop(columns=["EBITDA"]).iterrows():
        row_dict = {}
        for col in df.drop(columns=["EBITDA"]).columns:
            row_dict[col] = to_python_native(row[col])
        scr_data.append(row_dict)

    # Prepare der_data: calculated indicator per row. Include Fiscal Year if present.
    der_data = []
    year_col = None
    # Detect a year-like column (prefer "Fiscal Year" if present)
    if "Fiscal Year" in df.columns:
        year_col = "Fiscal Year"
    else:
        # fallback: first column
        year_col = df.columns[0]

    for _, row in df.iterrows():
        entry = {}
        # include year using the original column name
        entry[year_col] = to_python_native(row[year_col])
        entry[INDICATOR_NAME] = to_python_native(row["EBITDA"])
        der_data.append(entry)

    output = {"scr_data": scr_data, "der_data": der_data}

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()