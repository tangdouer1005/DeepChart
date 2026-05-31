#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,30614000000,55069000000,2787000000,-24455000000
2017,24766000000,53303000000,2748000000,-28537000000
2018,25875000000,55755000000,2679000000,-29880000000
2019,27483000000,58396000000,2580000000,-30913000000
2020,27764000000,66184000000,2541000000,-38420000000
2021,30266000000,67437000000,2538000000,-37171000000
2022,35722000000,63102000000,2542000000,-27380000000
2023,32168000000,69040000000,2547000000,-36872000000
2024,38782000000,70734000000,2541000000,-31952000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def to_py_val(v):
    # Convert numpy / pandas scalar types to native Python types for JSON serialization
    if v is None:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # if it's an integer-valued float, convert to int for cleaner JSON
        if float(v).is_integer():
            return int(v)
        return float(v)
    if pd.isna(v):
        return None
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw rows as dictionaries with original headers
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_val(row[col])
        scr_records.append(rec)

    # Calculate NNWC for each row:
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares Outstanding
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_py_val(row['Fiscal Year'])
        current_assets = row['Current Assets']
        total_liabilities = row['Total Liabilities']
        shares = row['Shares']

        # Compute Net-Net Value dynamically (do NOT rely on the provided Net-Net Value column)
        net_net_value = current_assets - total_liabilities  # may be negative
        # Per-share liquidation value; guard divide-by-zero
        per_share = None
        try:
            if shares == 0 or pd.isna(shares):
                per_share = None
            else:
                per_share = float(net_net_value) / float(shares)
        except Exception:
            per_share = None

        # Build the indicator value object. The top-level key must be the indicator name.
        indicator_value = {
            "Net-Net Value": to_py_val(int(net_net_value) if not pd.isna(net_net_value) else None),
            "Per-Share Value": to_py_val(per_share)
        }

        der_rec = {
            "Fiscal Year": fiscal_year,
            INDICATOR_NAME: indicator_value
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()