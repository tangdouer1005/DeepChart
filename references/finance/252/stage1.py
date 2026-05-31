#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,7017000000,9795000000,-2778000000,117031000000.0
2017,10558000000,13596000000,-3038000000,130868000000.0
2018,11986000000,15713000000,-3727000000,145639000000.0
2019,13839000000,18463000000,-4624000000,163055000000.0
2020,15403000000,22174000000,-6771000000,185589000000.0
2021,17285000000,22343000000,-5058000000,204747500000.0
2022,20120000000,26206000000,-6086000000,228955500000.0
2023,22381000000,29068000000,-6687000000,259712500000.0
2024,14405000000,24204000000,-9799000000,285999000000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def to_python_native(val):
    # Convert pandas/numpy scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # convert to plain Python float
        return float(val)
    # For plain python types (int, float, str) return as-is
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)

    out_path = sys.argv[1]

    # Load the CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure expected columns exist
    required_cols = ["Fiscal Year", "Net Income", "Operating Cashflow", "Avg Total Assets"]
    for c in required_cols:
        if c not in df.columns:
            raise ValueError(f"Expected column '{c}' in input data")

    # Calculate accruals using the definition: Accruals = Net Income - Operating Cashflow
    # (Do not rely on the provided 'Accruals' column for the calculation; compute dynamically)
    df["Accruals_Calc"] = df["Net Income"] - df["Operating Cashflow"]

    # Calculate Sloan Ratio = Accruals / Avg Total Assets
    df["Sloan_Ratio"] = df["Accruals_Calc"] / df["Avg Total Assets"]

    # Prepare scr_data: mirror the original CSV columns (use the original column names)
    scr_records = []
    orig_columns = list(df.columns)
    # But we only want to include the original CSV headers in scr_data (not the calculated helper columns)
    original_headers = ["Fiscal Year", "Net Income", "Operating Cashflow", "Accruals", "Avg Total Assets"]
    for _, row in df.iterrows():
        rec = {}
        for col in original_headers:
            # Some columns may be missing if input changed; handle gracefully
            if col in df.columns:
                rec[col] = to_python_native(row[col])
            else:
                rec[col] = None
        scr_records.append(rec)

    # Prepare der_data: each entry contains Fiscal Year and the computed indicator value
    der_records = []
    for _, row in df.iterrows():
        fy = to_python_native(row["Fiscal Year"])
        sloan_value = to_python_native(row["Sloan_Ratio"])
        der_records.append({
            "Fiscal Year": fy,
            INDICATOR_NAME: sloan_value
        })

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()