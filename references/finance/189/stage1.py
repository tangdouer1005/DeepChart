#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,272157744.91280466,3850007000.0,0.1,385000700.0
2017,711477655.257036,6173911000.0,0.1,617391100.0
2018,1585310830.6130335,9927677000.0,0.1,992767700.0
2019,2357603712.0303206,15223861000.0,0.1,1522386100.0
2020,3957615789.385591,18667343000.0,0.1,1866734300.0
2021,5426705726.260651,22191501000.0,0.1,2219150100.0
2022,4806723030.809116,27598820000.0,0.1,2759882000.0
2023,6060390689.079923,29190637000.0,0.1,2919063700.0
2024,9106716101.952335,30459805500.0,0.1,3045980550.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def to_native(val):
    """
    Convert numpy/pandas scalar types to native Python types for JSON serialization.
    """
    try:
        # numpy types often have .item()
        return val.item()
    except Exception:
        return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(2)

    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw rows from CSV as list of dictionaries with native Python types
    scr_data = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            record[col] = to_native(row[col])
        scr_data.append(record)

    # Calculate EVA for each row using the simplified formula:
    # EVA = NOPAT - (Invested Capital * WACC)
    der_data = []
    for _, row in df.iterrows():
        nopat = float(row["NOPAT"])
        invested_capital = float(row["Avg Invested Capital"])
        wacc = float(row["WACC"])
        eva = nopat - (invested_capital * wacc)

        # Include Year if present in input (use "Year" as a simple key)
        fiscal_year = to_native(row["Fiscal Year"])
        der_record = {
            "Year": fiscal_year,
            INDICATOR_NAME: to_native(eva)
        }
        der_data.append(der_record)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()