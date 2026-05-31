#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,19127960579.710144,119804500000.0,0.1,11980450000.0
2017,12189380943.625198,146538500000.0,0.1,14653850000.0
2018,24231021797.038357,163708000000.0,0.1,16370800000.0
2019,29668018498.42271,176523500000.0,0.1,17652350000.0
2020,34525378644.8151,199903000000.0,0.1,19990300000.0
2021,65960517138.007805,229700500000.0,0.1,22970050000.0
2022,62926542507.85105,248647500000.0,0.1,24864750000.0
2023,72569057888.16687,261795500000.0,0.1,26179550000.0
2024,93913633685.2648,294690000000.0,0.1,29469000000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_json_safe_value(v):
    """Convert pandas/numpy scalars to JSON-serializable Python types, map NaN to None."""
    if pd.isna(v):
        return None
    # numpy scalars
    if isinstance(v, (np.generic,)):
        return v.item()
    # pandas Timestamps etc.
    if isinstance(v, pd.Timestamp):
        return v.isoformat()
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Read CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: mirror input rows with JSON-serializable values
    scr_data = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            record[col] = to_json_safe_value(row[col])
        scr_data.append(record)

    # Calculate EVA for each row:
    # EVA = NOPAT - (Invested Capital * WACC)
    der_data = []
    for _, row in df.iterrows():
        # Extract values safely
        nopat = row.get("NOPAT")
        invested_capital = row.get("Avg Invested Capital")
        wacc = row.get("WACC")

        # Convert to native python numeric types for calculation
        nopat_val = None if pd.isna(nopat) else float(np.array(nopat).item())
        invested_cap_val = None if pd.isna(invested_capital) else float(np.array(invested_capital).item())
        wacc_val = None if pd.isna(wacc) else float(np.array(wacc).item())

        if (nopat_val is None) or (invested_cap_val is None) or (wacc_val is None):
            eva = None
        else:
            eva = nopat_val - (invested_cap_val * wacc_val)

        entry = {
            "Fiscal Year": to_json_safe_value(row["Fiscal Year"]),
            INDICATOR_NAME: to_json_safe_value(eva)
        }
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()