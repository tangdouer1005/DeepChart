#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,2629824695.6958213,204880000000.0,0.1,20488000000.0
2017,12950224911.641855,215362500000.0,0.1,21536250000.0
2018,15310897295.900234,225382500000.0,0.1,22538250000.0
2019,9403913242.919825,229528000000.0,0.1,22952800000.0
2020,-29448000000.0,226278500000.0,0.1,22627850000.0
2021,18146902798.232697,213232000000.0,0.1,21323200000.0
2022,47413478013.71008,207160000000.0,0.1,20716000000.0
2023,31464604020.233784,208800000000.0,0.1,20880000000.0
2024,28447569741.984325,244716500000.0,0.1,24471650000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_native_py(val):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required columns exist
    required_cols = ["Fiscal Year", "NOPAT", "Avg Invested Capital", "WACC"]
    for c in required_cols:
        if c not in df.columns:
            raise KeyError(f"Required column '{c}' not found in input data")

    # Calculation:
    # EVA = NOPAT - (Invested Capital * WACC)
    # Here we use "Avg Invested Capital" as Invested Capital per provided data.
    df_calc = df.copy()
    df_calc["EVA"] = df_calc["NOPAT"] - (df_calc["Avg Invested Capital"] * df_calc["WACC"])

    # Prepare scr_data: original rows as list of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native_py(row[col])
        scr_records.append(rec)

    # Prepare der_data: list of dicts with Fiscal Year and computed EVA under required indicator name
    der_records = []
    for _, row in df_calc.iterrows():
        rec = {
            "Fiscal Year": to_native_py(row["Fiscal Year"]),
            INDICATOR_NAME: to_native_py(row["EVA"])
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()