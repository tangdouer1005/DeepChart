#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,78719000000,58067000000,5088000000,20652000000
2017,83703000000,63681000000,5049000000,20022000000
2018,61837000000,65580000000,4881000000,-3743000000
2019,47755000000,64222000000,4453000000,-16467000000
2020,43573000000,56933000000,4254000000,-13360000000
2021,39112000000,56222000000,4236000000,-17110000000
2022,36717000000,54229000000,4192000000,-17512000000
2023,43348000000,57499000000,4105000000,-14151000000
2024,36862000000,78956000000,4062000000,-42094000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype={
        'Fiscal Year': int,
        'Current Assets': float,
        'Total Liabilities': float,
        'Shares': float,
        'Net-Net Value': float
    })

    # Prepare scr_data: mirror input rows (use original headers)
    scr_records = []
    for rec in df.to_dict(orient='records'):
        # Ensure numeric types are JSON serializable (convert numpy types)
        scr_records.append({
            'Fiscal Year': int(rec['Fiscal Year']),
            'Current Assets': float(rec['Current Assets']),
            'Total Liabilities': float(rec['Total Liabilities']),
            'Shares': float(rec['Shares']),
            'Net-Net Value': float(rec['Net-Net Value'])
        })

    # Calculate NNWC according to reference:
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = int(row['Fiscal Year'])
        current_assets = float(row['Current Assets'])
        total_liabilities = float(row['Total Liabilities'])
        shares = float(row['Shares'])

        net_net_value = current_assets - total_liabilities
        # Avoid division by zero
        per_share_value = net_net_value / shares if shares != 0 else None

        # Use numeric types friendly to JSON
        entry = {
            'Fiscal Year': fiscal_year,
            INDICATOR_NAME: {
                'Net-Net Value': float(net_net_value),
                'Per-Share Liquidation Value': (float(per_share_value) if per_share_value is not None else None)
            }
        }
        der_records.append(entry)

    output_obj = {
        'scr_data': scr_records,
        'der_data': der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()