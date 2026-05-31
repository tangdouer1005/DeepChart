#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,3333000000.0,20853000000,2516500000.0,9609000000,1129500000.0,58.33908790102143,95.58981163492558,42.90430846081799
2017,4248500000.0,27390000000,3017500000.0,14324000000,1790000000.0,56.61564439576488,76.89105696732757,45.612259145490086
2018,5215500000.0,30578000000,3698500000.0,14755000000,2688500000.0,62.25578847537445,91.49118942731278,66.50643849542529
2019,5303500000.0,31904000000,4056000000.0,15211000000,3113500000.0,60.67507209127382,97.32693445532836,74.71090000657419
2020,5919500000.0,34608000000,4664000000.0,17231000000,3599000000.0,62.43115753582987,98.7963554059544,76.23672450815391
2021,6450500000.0,43075000000,5084500000.0,19861000000,4177000000.0,54.65890887986071,93.44154372891596,76.76375811892653
2022,6352500000.0,43653000000,5665000000.0,21330000000,4507500000.0,53.11576523950244,96.93975621190812,77.13255977496483
2023,6391500000.0,40109000000,6371500000.0,20072000000,4451000000.0,58.16394076142511,115.86276903148664,80.93936827421282
2024,6745000000.0,41950000000,6382000000.0,20625000000,4245000000.0,58.68712753277712,112.94206060606062,75.12363636363636
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"

def to_native(value):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if value is None:
        return None
    # pandas uses numpy types; handle them
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    # NaN handling
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    # fallback
    return value

def df_records_to_native(records):
    native_records = []
    for rec in records:
        nr = {}
        for k, v in rec.items():
            nr[k] = to_native(v)
        native_records.append(nr)
    return native_records

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required columns exist
    required_cols = ["Fiscal Year", "Avg Receivables", "Revenue", "Avg Inventory", "Cost of Revenue", "Avg Payables"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required column missing: {col}")

    # Calculate components according to reference formulas:
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO

    # Use float conversion to avoid integer division surprises
    df["DSO_calc"] = (df["Avg Receivables"].astype(float) / df["Revenue"].astype(float)) * 365.0
    df["DIO_calc"] = (df["Avg Inventory"].astype(float) / df["Cost of Revenue"].astype(float)) * 365.0
    df["DPO_calc"] = (df["Avg Payables"].astype(float) / df["Cost of Revenue"].astype(float)) * 365.0
    df["CCC_calc"] = df["DSO_calc"] + df["DIO_calc"] - df["DPO_calc"]

    # Prepare scr_data: original CSV rows as list of dicts (preserve original column names)
    scr_records = df[[
        "Fiscal Year", "Avg Receivables", "Revenue", "Avg Inventory", "Cost of Revenue",
        "Avg Payables", "DSO", "DIO", "DPO"
    ]].to_dict(orient="records")
    scr_native = df_records_to_native(scr_records)

    # Prepare der_data: list of dicts with Fiscal Year and calculated CCC
    der_records = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(row["CCC_calc"])
        }
        der_records.append(rec)

    output = {
        "scr_data": scr_native,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()