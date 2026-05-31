#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,105408000000,28461000000,13987786146,76947000000
2017,124308000000,44793000000,14068883261,79515000000
2018,135676000000,55164000000,14066813595,80512000000
2019,152578000000,74467000000,13971114411,78111000000
2020,174296000000,97072000000,13740560000,77224000000
2021,188143000000,107633000000,13553473900,80510000000
2022,164795000000,109120000000,13242420000,55675000000
2023,171530000000,119013000000,12722000000,52517000000
2024,163711000000,125172000000,12447000000,38539000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def to_python_type(val):
    # Convert pandas/numpy scalar types to native python types for JSON serialization
    if pd.isna(val):
        return None
    # Pandas / numpy numeric types support int() and float()
    try:
        if isinstance(val, (int, float, str, bool)):
            return val
        # try convert numpy integers/floats
        return int(val) if float(val).is_integer() else float(val)
    except Exception:
        try:
            return float(val)
        except Exception:
            return str(val)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure necessary columns exist
    required_cols = ['Fiscal Year', 'Current Assets', 'Total Liabilities', 'Shares']
    for c in required_cols:
        if c not in df.columns:
            raise KeyError(f"Required column missing in CSV data: {c}")

    # Calculate NNWC (Net-Net Value) and per-share liquidation value dynamically
    # NNWC (total) = Current Assets - Total Liabilities
    # Per-share liquidation value = NNWC / Shares
    nnwc_total_series = df['Current Assets'] - df['Total Liabilities']
    per_share_series = nnwc_total_series / df['Shares']

    # Build scr_data: original scraped data rows
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_type(row[col])
        scr_records.append(rec)

    # Build der_data: derived indicator values per row
    der_records = []
    for idx, row in df.iterrows():
        year_value = to_python_type(row['Fiscal Year'])
        nnwc_total = to_python_type(nnwc_total_series.iloc[idx])
        per_share = to_python_type(per_share_series.iloc[idx])
        rec = {
            'Fiscal Year': year_value,
            # The required indicator key must be present and its value MUST be computed, not hardcoded.
            INDICATOR_NAME: nnwc_total,
            # Additionally provide per-share liquidation value for clarity (also computed).
            '每股清算价值 (Per-Share Liquidation Value)': per_share
        }
        der_records.append(rec)

    out_obj = {
        'scr_data': scr_records,
        'der_data': der_records
    }

    # Write JSON to output file with UTF-8 and keep Chinese characters
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()