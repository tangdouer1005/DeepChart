#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2018,3206195407.4741106,13109500000.0,0.1,1310950000.0
2019,3682234627.49213,13505000000.0,0.1,1350500000.0
2020,4110427613.191727,13649000000.0,0.1,1364900000.0
2021,5100289221.556887,13706500000.0,0.1,1370650000.0
2022,5879540178.571428,15396500000.0,0.1,1539650000.0
2023,6015469305.997408,17406000000.0,0.1,1740600000.0
2024,7022853696.098562,18714500000.0,0.1,1871450000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_native(val):
    """
    Convert numpy/pandas scalar types to native Python types for JSON serialization.
    """
    if pd.isna(val):
        return None
    # numpy scalar
    if isinstance(val, (np.generic,)):
        return val.item()
    # pandas Timestamp
    if isinstance(val, pd.Timestamp):
        return val.isoformat()
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original data rows with native Python types
    scr_data = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            record[col] = to_native(row[col])
        scr_data.append(record)

    # Calculate EVA (simplified) for each row:
    # EVA = NOPAT - (Invested Capital * WACC)
    der_data = []
    for _, row in df.iterrows():
        # Extract required raw inputs (ensure they are treated as floats)
        nopat = float(row["NOPAT"])
        invested_capital = float(row["Avg Invested Capital"])
        wacc = float(row["WACC"])
        eva = nopat - (invested_capital * wacc)

        entry = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(eva)
        }
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with UTF-8 and preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()