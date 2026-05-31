#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,16108000000,12427000000,2342000000.0,14769000000.0
2017,24216000000,20203000000,3025000000.0,23228000000.0
2018,29274000000,24913000000,4315000000.0,29228000000.0
2019,36314000000,23986000000,5741000000.0,29727000000.0
2020,38747000000,32671000000,6862000000.0,39533000000.0
2021,57683000000,46753000000,7967000000.0,54720000000.0
2022,50475000000,28944000000,8686000000.0,37630000000.0
2023,71113000000,46751000000,10382000000.0,57133000000.0
2024,91328000000,69380000000,15498000000.0,84878000000.0
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_python_native(val):
    # Convert numpy/pandas numeric types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    # attempt to cast plain Python numeric strings
    try:
        if isinstance(val, (int, float, str, bool)):
            return val
    except Exception:
        pass
    return val

def main(argv):
    if len(argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data by converting dataframe rows to native Python types
    scr_records = []
    for rec in df.to_dict(orient="records"):
        native_rec = {k: to_python_native(v) for k, v in rec.items()}
        scr_records.append(native_rec)

    # Calculate the indicator for each row dynamically
    der_records = []
    for idx, row in df.iterrows():
        # Read raw inputs (ensure numeric)
        cfo = row.get("CFO")
        op_inc = row.get("Operating Income")
        da = row.get("D&A")

        # Compute denominator as Operating Income + D&A (dynamic, do not rely on provided Denominator column)
        try:
            denom = float(op_inc) + float(da)
        except Exception:
            denom = None

        # Compute ratio: CFO / (Operating Income + D&A)
        if denom is None or denom == 0:
            ratio = None
        else:
            ratio = float(cfo) / denom

        der_record = {
            "Fiscal Year": to_python_native(row.get("Fiscal Year")),
            INDICATOR_NAME: to_python_native(ratio)
        }
        der_records.append(der_record)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file (ensure Chinese characters preserved)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main(sys.argv)