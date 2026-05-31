#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,15101400000,24725400000,1100875000,-9624000000
2017,19202100000,33313100000,1052023000,-14111000000
2018,20549600000,32999300000,1033667000,-12449700000
2019,13709600000,36587000000,957526000,-22877400000
2020,17462100000,40807900000,956590000,-23345800000
2021,18452400000,39651200000,953653000,-21198800000
2022,18034500000,38714400000,950182000,-20679900000
2023,25727000000,53142600000,903284000,-27415600000
2024,32739700000,64443300000,904059000,-31703600000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def to_native(v):
    # Convert pandas / numpy types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # Convert floats but if integral, still keep as float type
        return float(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data by converting dataframe rows to native Python types
    scr_records = []
    for rec in df.to_dict(orient='records'):
        native_rec = {k: to_native(v) for k, v in rec.items()}
        scr_records.append(native_rec)

    # Calculate Graham's Net-Net Working Capital (NNWC) for each row
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row['Fiscal Year']) if 'Fiscal Year' in row else None
        current_assets = row['Current Assets']
        total_liabilities = row['Total Liabilities']
        shares = row['Shares']

        # Perform calculations using raw input fields (do not hardcode results)
        net_net_value = None
        per_share_value = None
        try:
            # compute Net-Net Value (absolute)
            if pd.notna(current_assets) and pd.notna(total_liabilities):
                net_net_value = current_assets - total_liabilities
            # compute per-share liquidation value if shares available and non-zero
            if pd.notna(net_net_value) and pd.notna(shares) and shares != 0:
                per_share_value = net_net_value / shares
        except Exception:
            net_net_value = None
            per_share_value = None

        # Convert to native types
        net_net_value_native = to_native(net_net_value)
        per_share_value_native = to_native(per_share_value)

        # The indicator value is represented as a nested object containing both absolute and per-share values
        der_entry = {}
        if fiscal_year is not None:
            der_entry['Fiscal Year'] = fiscal_year
        der_entry[INDICATOR_NAME] = {
            "Net-Net Value": net_net_value_native,
            "Per-Share Liquidation Value": per_share_value_native
        }
        der_records.append(der_entry)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output file with utf-8 encoding to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()