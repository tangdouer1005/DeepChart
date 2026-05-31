#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,11976222000,12419628000,667770274,-443406000
2017,12097289000,12979690000,660463227,-882401000
2018,13585559000,13724495000,655296150,-138936000
2019,15450601000,14962189000,650204873,488412000
2020,17749756000,19579420000,647797003,-1829664000
2021,19666511000,23078729000,645909042,-3412218000
2022,21610871000,24516302000,642839181,-2905431000
2023,23381931000,24786712000,638591616,-1404781000
2024,20857781000,26764115000,635940000,-5906334000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def to_py_value(v):
    # Convert numpy / pandas scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return float(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: preserve original CSV columns and values (converted to native python types)
    scr_data = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            record[col] = to_py_value(row[col])
        scr_data.append(record)

    # Calculate NNWC and per-share liquidation value for each row
    der_data = []
    for _, row in df.iterrows():
        # Read raw inputs (must come from the CSV data; no hardcoded results)
        curr_assets = float(row['Current Assets'])
        total_liab = float(row['Total Liabilities'])
        shares = float(row['Shares'])

        # Net-Net Value = Total Current Assets - Total Liabilities
        net_net_value = curr_assets - total_liab

        # 每股清算价值 = Net-Net Value / Shares
        per_share_value = None
        if shares != 0:
            per_share_value = net_net_value / shares

        der_record = {
            'Fiscal Year': to_py_value(row['Fiscal Year']),
            # Main indicator value (total Net-Net Working Capital)
            INDICATOR_NAME: to_py_value(int(net_net_value) if float(net_net_value).is_integer() else float(net_net_value)),
            # Also include per-share liquidation value for clarity
            '每股清算价值': to_py_value(per_share_value)
        }
        der_data.append(der_record)

    output = {
        'scr_data': scr_data,
        'der_data': der_data
    }

    # Write JSON with UTF-8 and keep Chinese characters readable
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()