#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2017,15873827974.825584,113462500000.0,0.1,11346250000.0
2018,14220627587.118958,110843000000.0,0.1,11084300000.0
2019,13754738481.675394,113472000000.0,0.1,11347200000.0
2020,15542561543.05031,116641500000.0,0.1,11664150000.0
2021,15028345069.052711,113603000000.0,0.1,11360300000.0
2022,19342719298.245613,109305500000.0,0.1,10930550000.0
2023,13556239774.330042,108812000000.0,0.1,10881200000.0
2024,20115582204.320763,112422500000.0,0.1,11242250000.0
"""

def to_python_scalar(val):
    # Convert numpy / pandas scalars to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    # pandas Timestamp etc.
    if isinstance(val, (pd.Timestamp,)):
        return val.isoformat()
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: mirror input rows with proper Python-native scalars
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_scalar(row[col])
        scr_data.append(rec)

    # Calculation: 经济增加值 (Economic Value Added, EVA) - 简化版
    # EVA = NOPAT - (Invested Capital * WACC)
    # Here we use "Avg Invested Capital" as Invested Capital from the provided data.
    indicator_name = "经济增加值 (Economic Value Added, EVA) - 简化版"

    der_data = []
    for _, row in df.iterrows():
        nopat = float(row["NOPAT"]) if not pd.isna(row["NOPAT"]) else None
        invested_capital = float(row["Avg Invested Capital"]) if not pd.isna(row["Avg Invested Capital"]) else None
        wacc = float(row["WACC"]) if not pd.isna(row["WACC"]) else None

        # Compute capital charge as invested_capital * wacc (derived, not taken from CSV directly)
        capital_charge_derived = None
        eva = None
        if (nopat is not None) and (invested_capital is not None) and (wacc is not None):
            capital_charge_derived = invested_capital * wacc
            eva = nopat - capital_charge_derived

        rec = {
            "Fiscal Year": to_python_scalar(row["Fiscal Year"]),
            indicator_name: to_python_scalar(eva)
        }
        # Optionally include the derived capital charge for transparency (not required)
        # but per requirements, der_data should contain the calculated indicator value.
        der_data.append(rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()