#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,10522890092.879255,81386500000.0,0.1,8138650000.0
2017,9363437535.60674,86372000000.0,0.1,8637200000.0
2018,103841552.26627818,73992500000.0,0.1,7399250000.0
2019,11340264841.122778,53163000000.0,0.1,5316300000.0
2020,10933047959.9141,43590500000.0,0.1,4359050000.0
2021,10248401673.955664,42160000000.0,0.1,4216000000.0
2022,11397515231.056158,43078500000.0,0.1,4307850000.0
2023,12376681224.702965,42576000000.0,0.1,4257600000.0
2024,10275291809.710644,55190500000.0,0.1,5519050000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_native(o):
    # Convert numpy and pandas types to native Python types for JSON serialization
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.ndarray,)):
        return o.tolist()
    if pd.isna(o):
        return None
    return o

def row_to_native_dict(row):
    d = {}
    for k, v in row.items():
        d[k] = to_native(v)
    return d

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are proper types
    # Columns expected: NOPAT, Avg Invested Capital, WACC
    # We'll compute: EVA = NOPAT - (Avg Invested Capital * WACC)
    # Do not hardcode results; compute dynamically row by row.
    required_cols = ["NOPAT", "Avg Invested Capital", "WACC"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' not found in input data")

    # Calculate EVA per row
    eva_values = []
    for idx, row in df.iterrows():
        # Safely extract values as floats
        nopat = float(row["NOPAT"]) if not pd.isna(row["NOPAT"]) else None
        invested_cap = float(row["Avg Invested Capital"]) if not pd.isna(row["Avg Invested Capital"]) else None
        wacc = float(row["WACC"]) if not pd.isna(row["WACC"]) else None

        if nopat is None or invested_cap is None or wacc is None:
            eva = None
        else:
            eva = nopat - (invested_cap * wacc)

        eva_values.append(eva)

    # Prepare scr_data (original rows) converting types to native Python types
    scr_records = [row_to_native_dict(r) for r in df.to_dict(orient="records")]

    # Prepare der_data with calculated EVA; include Fiscal Year if present
    der_records = []
    year_col = None
    # Detect a year-like column name present in CSV (prefer "Fiscal Year" if present)
    if "Fiscal Year" in df.columns:
        year_col = "Fiscal Year"
    else:
        # fallback: find first column that looks like a year (integers >=1900 and <=2100)
        for col in df.columns:
            sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
            try:
                if sample is not None and float(sample).is_integer():
                    ival = int(float(sample))
                    if 1900 <= ival <= 2100:
                        year_col = col
                        break
            except Exception:
                continue

    for idx, eva in enumerate(eva_values):
        rec = {}
        if year_col is not None:
            rec[year_col] = to_native(df.iloc[idx][year_col])
        rec[INDICATOR_NAME] = to_native(eva)
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file with UTF-8 encoding and ensure non-ASCII is preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()