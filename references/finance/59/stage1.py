#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,0.0,5293163500.0,0.1,529316350.0
2017,42625698.32402234,6537709000.0,0.1,653770900.0
2018,148708775.03117144,8296239500.0,0.1,829623950.0
2019,465879959.30824006,12391458000.0,0.1,1239145800.0
2020,36050991.50141644,24637500000.0,0.1,2463750000.0
2021,-703143303.3971106,35950000000.0,0.1,3595000000.0
2022,-624916449.0861619,51341000000.0,0.1,5134100000.0
2023,921818181.818182,63239500000.0,0.1,6323950000.0
2024,4186968888.888889,61826000000.0,0.1,6182600000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_native(val):
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of native-python-typed dicts
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate EVA (simplified) for each row:
    # EVA = NOPAT - (Invested Capital * WACC)
    der_records = []
    for _, row in df.iterrows():
        # Use the provided raw data columns dynamically
        nopat = float(row["NOPAT"])
        invested_capital = float(row["Avg Invested Capital"])
        wacc = float(row["WACC"])
        eva = nopat - (invested_capital * wacc)

        rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(eva)
        }
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write to output JSON file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()