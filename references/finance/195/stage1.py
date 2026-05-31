#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,6053000000,2901000000,22760000000,3152000000
2017,8536000000,4079000000,25960000000,4457000000
2018,9255000000,3770000000,25280000000,5485000000
2019,10557000000,3950000000,25000000000,6607000000
2020,13690000000,5111000000,24720000000,8579000000
2021,16055000000,11898000000,25120000000,4157000000
2022,28829000000,17575000000,25350000000,11254000000
2023,23073000000,19081000000,25070000000,3992000000
2024,44345000000,22750000000,24940000000,21595000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def to_builtin_types(obj):
    """
    Convert pandas / numpy scalar types to native Python types for JSON serialization.
    """
    try:
        # numpy scalars have .item()
        return obj.item()
    except Exception:
        return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation (do NOT hardcode results)
    # Net-Net Value (total) = Total Current Assets - Total Liabilities
    df['Computed_NetNet_Total'] = df['Current Assets'] - df['Total Liabilities']

    # Per-share liquidation value = Net-Net Value / Shares
    # Ensure float division
    df['Computed_NetNet_PerShare'] = df['Computed_NetNet_Total'] / df['Shares']

    # Prepare scr_data: original CSV rows (preserve original columns)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        # Use original CSV columns only (not the computed ones)
        for col in ['Fiscal Year', 'Current Assets', 'Total Liabilities', 'Shares', 'Net-Net Value']:
            rec[col] = to_builtin_types(row[col])
        scr_records.append(rec)

    # Prepare der_data: calculated indicator per row
    der_records = []
    for _, row in df.iterrows():
        rec = {}
        # include Year
        rec['Fiscal Year'] = to_builtin_types(row['Fiscal Year'])
        # The indicator value: we put the per-share liquidation value under the required indicator name
        rec[INDICATOR_NAME] = to_builtin_types(row['Computed_NetNet_PerShare'])
        # Optionally include the total Net-Net value as supporting info (not the main indicator key)
        rec['Computed Net-Net Value (Total)'] = to_builtin_types(row['Computed_NetNet_Total'])
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file with utf-8 and keep Chinese characters
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()