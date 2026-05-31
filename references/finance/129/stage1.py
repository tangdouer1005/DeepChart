#!/usr/bin/env python3
"""
Calculate "经济增加值 (Economic Value Added, EVA) - 简化版" from embedded CSV data and write JSON output.

Usage:
    python this.py output.json
"""
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,6969438298.918387,61336500000.0,0.1,6133650000.0
2017,1444073294.629898,59483500000.0,0.1,5948350000.0
2018,7205878662.613981,55428500000.0,0.1,5542850000.0
2019,8401882996.476914,53825500000.0,0.1,5382550000.0
2020,7168806646.835572,55582000000.0,0.1,5558200000.0
2021,8133571991.951711,56002500000.0,0.1,5600250000.0
2022,8934625962.6904,55231000000.0,0.1,5523100000.0
2023,9346945105.003088,56538000000.0,0.1,5653800000.0
2024,8131194253.400581,58920000000.0,0.1,5892000000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_python_native(value):
    """
    Convert numpy / pandas scalar types to native Python types for JSON serialization.
    """
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.ndarray, list)):
        return value.tolist()
    if pd.isna(value):
        return None
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: mirror of input rows
    scr_records = df.to_dict(orient="records")
    # Convert any numpy/pandas scalars to native python types
    scr_data = []
    for rec in scr_records:
        new_rec = {}
        for k, v in rec.items():
            new_rec[k] = to_python_native(v)
        scr_data.append(new_rec)

    # Compute EVA for each row dynamically using formula:
    # EVA = NOPAT - (Invested Capital * WACC)
    # We'll use 'Avg Invested Capital' as Invested Capital per provided data.
    eva_values = []
    for _, row in df.iterrows():
        # Ensure we access the correct columns; handle missing columns defensively
        nopat = row.get("NOPAT") if "NOPAT" in row else row.get("NOPAT", 0)
        invested_capital = row.get("Avg Invested Capital") if "Avg Invested Capital" in row else row.get("Avg Invested Capital", 0)
        wacc = row.get("WACC") if "WACC" in row else row.get("WACC", 0.0)

        # Convert to numeric Python types
        nopat_f = float(nopat) if not pd.isna(nopat) else 0.0
        invested_cap_f = float(invested_capital) if not pd.isna(invested_capital) else 0.0
        wacc_f = float(wacc) if not pd.isna(wacc) else 0.0

        eva = nopat_f - (invested_cap_f * wacc_f)

        eva_values.append(eva)

    # Prepare der_data: each entry contains Fiscal Year and the computed EVA
    der_data = []
    for idx, rec in enumerate(scr_data):
        year_key = "Fiscal Year" if "Fiscal Year" in rec else None
        entry = {}
        if year_key is not None:
            entry[year_key] = rec[year_key]
        entry[INDICATOR_NAME] = to_python_native(eva_values[idx])
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()