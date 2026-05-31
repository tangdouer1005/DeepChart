#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,617305518.1695827,5460914500.0,0.1,546091450.0
2017,1691361679.7900262,6133000000.0,0.1,613300000.0
2018,3060347309.13642,6137500000.0,0.1,613750000.0
2019,3564785420.944558,8054000000.0,0.1,805400000.0
2020,2679264646.4646463,7014500000.0,0.1,701450000.0
2021,4452851893.853481,13199500000.0,0.1,1319950000.0
2022,9850098782.81863,29360500000.0,0.1,2936050000.0
2023,4035076775.890936,32688500000.0,0.1,3268850000.0
2024,29015515997.397835,37650000000.0,0.1,3765000000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_python_native(value):
    """Convert pandas/numpy scalar to native Python types for JSON serialization."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.generic,)):
        return value.item()
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert each row to plain Python types
    scr_data = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            record[col] = to_python_native(row[col])
        scr_data.append(record)

    # Calculate EVA for each row using the simplified formula:
    # EVA = NOPAT - (Invested Capital * WACC)
    # Here we use "Avg Invested Capital" from the CSV as Invested Capital.
    der_data = []
    for _, row in df.iterrows():
        nopat = float(row["NOPAT"]) if not pd.isna(row["NOPAT"]) else None
        invested_capital = float(row["Avg Invested Capital"]) if not pd.isna(row["Avg Invested Capital"]) else None
        wacc = float(row["WACC"]) if not pd.isna(row["WACC"]) else None

        # Compute EVA only if necessary inputs are present
        if nopat is None or invested_capital is None or wacc is None:
            eva = None
        else:
            eva = nopat - (invested_capital * wacc)

        entry = {}
        # Include Year if present
        if "Fiscal Year" in df.columns:
            # Ensure it's a native Python int if possible
            fy = to_python_native(row["Fiscal Year"])
            entry["Fiscal Year"] = fy
        entry[INDICATOR_NAME] = to_python_native(eva)
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON output
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()