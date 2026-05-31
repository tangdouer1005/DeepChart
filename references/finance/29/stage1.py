#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,3733962194.70991,2238638500.0,0.1,223863850.0
2017,4088011793.389648,3762285000.0,0.1,376228500.0
2018,4280399535.7384944,5088046500.0,0.1,508804650.0
2019,4887540034.78264,6816609500.0,0.1,681660950.0
2020,4985773932.595264,8853974000.0,0.1,885397400.0
2021,5882802478.832297,10787066000.0,0.1,1078706600.0
2022,7118928279.766994,13574963500.0,0.1,1357496350.0
2023,6751075670.319231,16232528500.0,0.1,1623252850.0
2024,7340046235.686655,21260681500.0,0.1,2126068150.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_native_value(v):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # convert NaN checked above
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw data rows as dictionaries with native types
    raw_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native_value(row[col])
        raw_records.append(rec)

    # Calculate EVA for each row using formula:
    # EVA = NOPAT - (Invested Capital * WACC)
    der_records = []
    for _, row in df.iterrows():
        # Read inputs, ensuring numeric python types
        nopat = float(row["NOPAT"]) if not pd.isna(row["NOPAT"]) else None
        invested_capital = float(row["Avg Invested Capital"]) if not pd.isna(row["Avg Invested Capital"]) else None
        wacc = float(row["WACC"]) if not pd.isna(row["WACC"]) else None

        # Only compute when all inputs present
        if nopat is None or invested_capital is None or wacc is None:
            eva = None
        else:
            eva = nopat - (invested_capital * wacc)

        rec = {
            "Fiscal Year": to_native_value(row["Fiscal Year"]),
            INDICATOR_NAME: to_native_value(eva)
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": raw_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()