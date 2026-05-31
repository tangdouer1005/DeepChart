#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Avg Receivables,Revenue,Avg Inventory,Cost of Revenue,Avg Payables,DSO,DIO,DPO
2019,3246483000.0,20156447000,179916000.0,12440213000,618666000.0,58.788450911016206,5.278795467569567,18.151866853083625
2020,794943500.0,24996056000,192020500.0,15276319000,665265000.0,11.608006379086364,4.587982386332729,15.895303377731247
2021,707569500.0,29697844000,263430000.0,17332683000,746833000.0,8.696350735090398,5.547436020147602,15.727169590535985
2022,1195609000.0,31615550000,358276500.0,19168285000,754498000.0,13.803248243348603,6.822254703537641,14.367053181857427
2023,1714476000.0,33723297000,400835500.0,19715368000,709462500.0,18.55642228575693,7.420858565764534,13.134617243766384
"""

def to_python_native(obj):
    # convert numpy types to native python types for json serialization
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if pd.isna(obj):
        return None
    return obj

def record_to_native(rec):
    return {k: to_python_native(v) for k, v in rec.items()}

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["Avg Receivables", "Revenue", "Avg Inventory", "Cost of Revenue", "Avg Payables"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Calculate CCC components and CCC for each row
    # DSO = (Avg Receivables / Revenue) * 365
    # DIO = (Avg Inventory / Cost of Revenue) * 365
    # DPO = (Avg Payables / Cost of Revenue) * 365
    # CCC = DSO + DIO - DPO

    # Compute using vectorized operations
    df["Computed_DSO"] = (df["Avg Receivables"] / df["Revenue"]) * 365
    df["Computed_DIO"] = (df["Avg Inventory"] / df["Cost of Revenue"]) * 365
    df["Computed_DPO"] = (df["Avg Payables"] / df["Cost of Revenue"]) * 365
    df["Computed_CCC"] = df["Computed_DSO"] + df["Computed_DIO"] - df["Computed_DPO"]

    # Prepare scr_data: original input rows as dictionaries (preserve original columns)
    scr_records = df[["Fiscal Year", "Avg Receivables", "Revenue", "Avg Inventory", "Cost of Revenue", "Avg Payables", "DSO", "DIO", "DPO"]].to_dict(orient="records")
    scr_records_native = [record_to_native(r) for r in scr_records]

    # Prepare der_data: each row's calculated CCC (include Fiscal Year)
    der_records = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": to_python_native(row["Fiscal Year"]),
            "现金循环周期 (Cash Conversion Cycle, CCC)": to_python_native(row["Computed_CCC"])
        }
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records_native,
        "der_data": der_records
    }

    # Write JSON to output path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()