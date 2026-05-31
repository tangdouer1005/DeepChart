#!/usr/bin/env python3
"""
Calculate Cash Conversion Cycle (现金循环周期, CCC) from embedded CSV data and write results to a JSON file.

Usage:
    python this.py output.json
"""

import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2016,1238000000.0,118719000000,8938500000.0,102901000000,8311500000.0,3.8062146749888393,31.705741440802324,29.48171057618488
2017,1342000000.0,129025000000,9401500000.0,111882000000,8610000000.0,3.7963960472776592,30.67113119179135,28.08896873491715
2018,1550500000.0,141576000000,10437000000.0,123152000000,10422500000.0,3.9973759676781375,30.933358776146548,30.890383428608548
2019,1602000000.0,152703000000,11217500000.0,132886000000,11458000000.0,3.829197854659044,30.81127808798519,31.47186310070286
2020,1542500000.0,166761000000,11818500000.0,144939000000,12925500000.0,3.376164091124424,29.76253803324157,32.5502970215056
2021,1676500000.0,195929000000,13228500000.0,170684000000,15225000000.0,3.12318492923457,28.28854784279721,32.55797262778
2022,2022000000.0,226954000000,16061000000.0,199382000000,17063000000.0,3.2518924539774576,29.402177729183176,31.23649577193528
2023,2263000000.0,242290000000,17279000000.0,212586000000,17665500000.0,3.4091171736349,29.667217032165805,30.330819056758205
2024,2503000000.0,254453000000,17649000000.0,222358000000,18452000000.0,3.5904273087760807,28.97078135259357,30.288903479973737
"""

INDICATOR_NAME = "现金循环周期 (Cash Conversion Cycle, CCC)"

def to_python_native(val):
    """Convert numpy / pandas scalar types to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    # strings and other built-ins
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required columns exist
    required = ["Fiscal Year", "Avg Receivables", "Revenue", "Avg Inventory", "Cost of Revenue", "Avg Payables"]
    for col in required:
        if col not in df.columns:
            raise KeyError(f"Required column missing from CSV data: {col}")

    # Compute components from raw data (do not use any precomputed DSO/DIO/DPO columns)
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO
    def compute_ccc(row):
        # protect against division by zero
        revenue = row["Revenue"]
        cost = row["Cost of Revenue"]
        dso = (row["Avg Receivables"] / revenue) * 365.0 if revenue else None
        dio = (row["Avg Inventory"] / cost) * 365.0 if cost else None
        dpo = (row["Avg Payables"] / cost) * 365.0 if cost else None
        if dso is None or dio is None or dpo is None:
            return None
        return dso + dio - dpo

    # Build scr_data: original rows as list of dicts with native types
    scr_records = []
    for _, r in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(r[col])
        scr_records.append(rec)

    # Build der_data: one dict per row with Fiscal Year and CCC value
    der_records = []
    for _, r in df.iterrows():
        ccc_value = compute_ccc(r)
        der_rec = {"Fiscal Year": to_python_native(r["Fiscal Year"]),
                   INDICATOR_NAME: to_python_native(ccc_value)}
        der_records.append(der_rec)

    output = {"scr_data": scr_records, "der_data": der_records}

    # Write JSON with ensure_ascii=False to keep Chinese characters readable
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()