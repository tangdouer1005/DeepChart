#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,2444222929.936306,24567500000.0,0.1,2456750000.0
2017,312019722.09771395,36669000000.0,0.1,3666900000.0
2018,3122831883.049078,47830000000.0,0.1,4783000000.0
2019,4151831493.7454014,45909000000.0,0.1,4590900000.0
2020,4761686996.779388,45253000000.0,0.1,4525300000.0
2021,7922689075.630252,44616000000.0,0.1,4461600000.0
2022,6979743077.293523,44052500000.0,0.1,4405250000.0
2023,5526336284.513805,45219000000.0,0.1,4521900000.0
2024,607272208.7551686,50529000000.0,0.1,5052900000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_python_scalar(x):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    if pd.isna(x):
        return None
    # direct native types
    if isinstance(x, (str, bool, int, float)):
        return x
    # try .item() for numpy scalars
    try:
        return x.item()
    except Exception:
        # fallback conversions
        try:
            return int(x)
        except Exception:
            try:
                return float(x)
            except Exception:
                return str(x)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation: EVA = NOPAT - (Invested Capital * WACC)
    # Using columns: 'NOPAT', 'Avg Invested Capital' as Invested Capital, 'WACC'
    df["EVA_Calculated"] = df["NOPAT"] - (df["Avg Invested Capital"] * df["WACC"])

    # Prepare scr_data: mirror of input CSV rows with native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            if col == "EVA_Calculated":
                # This column is derived; we only want original CSV columns in scr_data
                continue
            rec[col] = to_python_scalar(row[col])
        scr_data.append(rec)

    # Prepare der_data: one dictionary per input row with Year (if present) and calculated EVA
    der_data = []
    for _, row in df.iterrows():
        rec = {}
        # Include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_python_scalar(row["Fiscal Year"])
        # Include calculated EVA under the exact required indicator name
        rec[INDICATOR_NAME] = to_python_scalar(row["EVA_Calculated"])
        der_data.append(rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()