#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,4851000000,3871300000,1496600000,5367900000
2017,5615600000,4249800000,1567300000,5817100000
2018,5524500000,6025800000,1609000000,7634800000
2019,4836600000,5999400000,1232600000,7232000000
2020,6499600000,7210800000,1323900000,8534700000
2021,7260700000,7933000000,1547600000,9480600000
2022,7084400000,8653300000,1522500000,10175800000
2023,4240100000,10787300000,1527300000,12314600000
2024,8817900000,17501700000,1766600000,19268300000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_python_primitive(val):
    """Convert numpy / pandas scalars to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    # fallback for other types (including Python native int/float/str)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original data as list of dicts, converting types to Python primitives
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_primitive(row[col])
        scr_records.append(rec)

    # Calculate the indicator for each row:
    # Quality of Income Ratio = CFO / (Operating Income + D&A)
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_python_primitive(row.get("Fiscal Year"))
        cfo = row.get("CFO")
        operating_income = row.get("Operating Income")
        da = row.get("D&A")

        # Compute denominator as Operating Income + D&A per reference formula.
        # If D&A is missing or NaN, fall back to Operating Income only.
        if pd.isna(operating_income) and pd.isna(da):
            denominator = None
        else:
            if pd.isna(operating_income):
                operating_income = 0.0
            if pd.isna(da):
                da = 0.0
            denominator = operating_income + da

        # Compute ratio, guard against zero or missing denominator
        if denominator is None or denominator == 0 or pd.isna(cfo):
            ratio_value = None
        else:
            ratio_value = float(cfo) / float(denominator)

        der_rec = {
            "Fiscal Year": fiscal_year,
            INDICATOR_NAME: to_python_primitive(ratio_value)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()