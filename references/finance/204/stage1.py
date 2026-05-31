#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,8901000000,1467000000,2541000000,2509000000
2017,9452000000,1798000000,2228000000,2451000000
2018,3587000000,2025000000,8837000000,2785000000
2019,11083000000,2082000000,1185000000,2919000000
2020,10135000000,1995000000,1928000000,2968000000
2021,13746000000,2496000000,747000000,2916000000
2022,6717000000,2755000000,932000000,3122000000
2023,8503000000,3505000000,623000000,6108000000
2024,10467000000,3514000000,1274000000,6139000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_native(v):
    # Convert numpy types to native python types for JSON serialization
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if pd.isna(v):
        return None
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculate EBITDA per row:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
    # Ensure numeric types
    cols_needed = ["Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for c in cols_needed:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["EBITDA"] = df["Net Income"] + df["Interest Expense"] + df["Income Tax"] + df["Depreciation & Amortization"]

    # Prepare scr_data: original rows as list of dicts with original column headers
    scr_records = df.drop(columns=["EBITDA"]).to_dict(orient="records")
    # Convert numpy types to native Python types
    scr_records_native = []
    for rec in scr_records:
        newrec = {}
        for k, v in rec.items():
            newrec[k] = to_native(v)
        scr_records_native.append(newrec)

    # Prepare der_data: each dict contains Fiscal Year and calculated indicator
    der_records = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(row["EBITDA"])
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records_native,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()