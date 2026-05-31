#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2018,4480000000,1263000000,4442000000,0.2843313822602431,3206195407.4741106,13109500000.0
2019,4737000000,1061000000,4765000000,0.2226652675760755,3682234627.49213,13505000000.0
2020,5435000000,1308000000,5367000000,0.2437115707098938,4110427613.191727,13649000000.0
2021,6708000000,1601000000,6680000000,0.2396706586826347,5100289221.556887,13706500000.0
2022,7793000000,1925000000,7840000000,0.2455357142857142,5879540178.571428,15396500000.0
2023,8114000000,2195000000,8487000000,0.2586308471780369,6015469305.997408,17406000000.0
2024,9285000000,2373000000,9740000000,0.2436344969199178,7022853696.098562,18714500000.0
"""

INDICATOR_KEY = "投入资本回报率 (Return on Invested Capital, ROIC)"

def to_native(val):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val

def compute_roic_row(row):
    # Compute NOPAT = Operating Income * (1 - Effective Tax Rate)
    # Invested Capital = Avg Invested Capital (using provided raw data column)
    # ROIC = NOPAT / Invested Capital
    op_income = row.get("Operating Income")
    eff_tax = row.get("Effective Tax Rate")
    invested_cap = row.get("Avg Invested Capital")

    # Safeguard conversions
    try:
        op_income_f = float(op_income) if op_income is not None else None
    except Exception:
        op_income_f = None
    try:
        eff_tax_f = float(eff_tax) if eff_tax is not None else None
    except Exception:
        eff_tax_f = None
    try:
        invested_cap_f = float(invested_cap) if invested_cap is not None else None
    except Exception:
        invested_cap_f = None

    roic = None
    if op_income_f is not None and eff_tax_f is not None and invested_cap_f not in (None, 0):
        nopat = op_income_f * (1.0 - eff_tax_f)
        # If invested capital is zero or negative, avoid division error; return None in that case
        if invested_cap_f != 0:
            roic = nopat / invested_cap_f
    return roic

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: original rows, converting values to native Python types
    scr_records = []
    for _, r in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(r[col])
        scr_records.append(rec)

    # Build der_data: compute ROIC per row
    der_records = []
    for _, r in df.iterrows():
        row_dict = {col: to_native(r[col]) for col in df.columns}
        roic_val = compute_roic_row(row_dict)
        der_rec = {}
        # include Fiscal Year if present
        if "Fiscal Year" in row_dict:
            der_rec["Fiscal Year"] = row_dict["Fiscal Year"]
        der_rec[INDICATOR_KEY] = to_native(roic_val)
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()