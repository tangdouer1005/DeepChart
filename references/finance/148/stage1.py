#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,4141675345.377258,8065500000.0,0.1,806550000.0
2017,3975027598.8960447,9839000000.0,0.1,983900000.0
2018,5922437257.0794,7715000000.0,0.1,771500000.0
2019,8062105847.292159,6924500000.0,0.1,692450000.0
2020,6676197293.814432,8876000000.0,0.1,887600000.0
2021,8497364315.513729,11371000000.0,0.1,1137100000.0
2022,10380286396.181383,13552500000.0,0.1,1355250000.0
2023,11497878143.55891,13667500000.0,0.1,1366750000.0
2024,13150823915.038675,15145500000.0,0.1,1514550000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_python_value(v):
    """Convert numpy/pandas types to native python types for JSON serialization."""
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_ , bool)):
        return bool(v)
    # For other types (e.g., Python int/float/str) return as-is
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts mirroring the input CSV (with native python types)
    scr_data = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            row_dict[col] = to_python_value(row[col])
        scr_data.append(row_dict)

    # Calculate EVA for each row:
    # EVA = NOPAT - (Invested Capital * WACC)
    # Use columns: "NOPAT", "Avg Invested Capital", "WACC"
    der_data = []
    for _, row in df.iterrows():
        nopat = row.get("NOPAT")
        invested_capital = row.get("Avg Invested Capital")
        wacc = row.get("WACC")

        # Ensure numeric types for calculation; handle missing gracefully
        try:
            nopat_val = float(nopat) if not pd.isna(nopat) else None
        except Exception:
            nopat_val = None
        try:
            invested_val = float(invested_capital) if not pd.isna(invested_capital) else None
        except Exception:
            invested_val = None
        try:
            wacc_val = float(wacc) if not pd.isna(wacc) else None
        except Exception:
            wacc_val = None

        eva_value = None
        if (nopat_val is not None) and (invested_val is not None) and (wacc_val is not None):
            eva_value = nopat_val - (invested_val * wacc_val)

        entry = {}
        # include the year if present
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = to_python_value(row["Fiscal Year"])
        entry[INDICATOR_NAME] = to_python_value(eva_value)
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified output file with ensure_ascii=False to keep Chinese characters readable
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()