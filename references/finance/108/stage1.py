#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,16993000000,36233000000,1283000000,-19240000000
2017,17724000000,38633000000,1234000000,-20909000000
2018,18933000000,43075000000,1184000000,-24142000000
2019,18529000000,45881000000,1143000000,-27352000000
2020,19810000000,54352000000,1097000000,-34542000000
2021,28477000000,67282000000,1078000000,-38805000000
2022,29055000000,73572000000,1058000000,-44517000000
2023,32471000000,74883000000,1025000000,-42412000000
2024,29775000000,75486000000,1002000000,-45711000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'
PER_SHARE_NAME = '每股清算价值 (Per-Share Liquidation Value)'

def safe_number(x):
    # Convert numpy types to native Python types for JSON serialization
    if pd.isna(x):
        return None
    if isinstance(x, (int,)):
        return x
    try:
        # Try int if no fractional part
        if float(x).is_integer():
            return int(float(x))
    except Exception:
        pass
    try:
        return float(x)
    except Exception:
        return x

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the hardcoded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA), dtype={
        'Fiscal Year': int,
        'Current Assets': float,
        'Total Liabilities': float,
        'Shares': float,
        'Net-Net Value': float
    })

    # Build scr_data: original scraped data as list of dicts
    scr_data = []
    for _, row in df.iterrows():
        rec = {
            'Fiscal Year': safe_number(row['Fiscal Year']),
            'Current Assets': safe_number(row['Current Assets']),
            'Total Liabilities': safe_number(row['Total Liabilities']),
            'Shares': safe_number(row['Shares']),
            'Net-Net Value': safe_number(row['Net-Net Value'])
        }
        scr_data.append(rec)

    # Derive the Graham Net-Net Working Capital (NNWC) dynamically:
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares
    der_data = []
    for _, row in df.iterrows():
        current_assets = row['Current Assets']
        total_liabilities = row['Total Liabilities']
        shares = row['Shares']

        net_net_value = current_assets - total_liabilities  # dynamic computation
        per_share = None
        try:
            if shares != 0 and not pd.isna(shares):
                per_share = net_net_value / shares
        except Exception:
            per_share = None

        der_rec = {
            'Fiscal Year': safe_number(row['Fiscal Year']),
            INDICATOR_NAME: safe_number(net_net_value),
            PER_SHARE_NAME: safe_number(per_share)
        }
        der_data.append(der_rec)

    output = {
        'scr_data': scr_data,
        'der_data': der_data
    }

    # Write JSON to the specified output file
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()