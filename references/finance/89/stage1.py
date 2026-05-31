#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,11893307353.150335,283310000000.0,0.1,28331000000.0
2017,-2739000000.0,185716000000.0,0.1,18571600000.0
2018,6761000000.0,157818500000.0,0.1,15781850000.0
2019,5151000000.0,136047000000.0,0.1,13604700000.0
2020,375636013.400335,88567000000.0,0.1,8856700000.0
2021,1058000000.0,66874000000.0,0.1,6687400000.0
2022,1858000000.0,54971500000.0,0.1,5497150000.0
2023,4267934010.152284,41772000000.0,0.1,4177200000.0
2024,5907445931.758531,29302500000.0,0.1,2930250000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_native_value(v):
    # Convert numpy types and pandas NA to native python types for JSON serialization
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if pd.isna(v):
        return None
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required columns exist
    required_cols = ["NOPAT", "Avg Invested Capital", "WACC"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' not found in input data")

    # Calculate EVA for each row using the simplified formula:
    # EVA = NOPAT - (Invested Capital * WACC)
    # Here Invested Capital is given as "Avg Invested Capital"
    eva_series = df["NOPAT"].astype(float) - (df["Avg Invested Capital"].astype(float) * df["WACC"].astype(float))

    # Build scr_data preserving original headers and converting types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native_value(row[col])
        scr_records.append(rec)

    # Build der_data with Fiscal Year (if present) and calculated EVA
    der_records = []
    year_col = None
    # Try to detect a year-like column name
    for candidate in ["Fiscal Year", "Year", "FY", "fiscal_year"]:
        if candidate in df.columns:
            year_col = candidate
            break

    for idx, eva_val in enumerate(eva_series):
        rec = {}
        if year_col is not None:
            rec[year_col] = to_native_value(df.at[idx, year_col])
        rec[INDICATOR_NAME] = to_native_value(eva_val)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file (ensure non-ASCII characters preserved)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()