#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,14217000000,47655000000,833054545,-33438000000
2017,8915000000,48004000000,871787000,-39089000000
2018,8281000000,47750000000,858290000,-39469000000
2019,9305000000,58132000000,863434000,-48827000000
2020,23885000000,134818000000,1154749000,-110933000000
2021,20891000000,137461000000,1254770000,-116570000000
2022,19067000000,141682000000,1255377000,-122615000000
2023,19015000000,142967000000,1200286000,-123952000000
2024,18404000000,146294000000,1173214000,-127890000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def to_native(obj):
    # convert numpy/pandas scalar types to native Python types for JSON serialization
    try:
        # for numpy/pandas scalars
        return obj.item()
    except Exception:
        return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))
    # Build scr_data from the original CSV (ensure native Python types)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Compute Graham's Net-Net Working Capital (NNWC) per reference:
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares
    der_records = []
    for _, row in df.iterrows():
        fiscal = to_native(row['Fiscal Year'])
        current_assets = to_native(row['Current Assets'])
        total_liabilities = to_native(row['Total Liabilities'])
        shares = to_native(row['Shares'])

        # ensure numeric operations use Python numeric types
        try:
            net_net_value = int(current_assets) - int(total_liabilities)
        except Exception:
            net_net_value = float(current_assets) - float(total_liabilities)

        # avoid division by zero
        per_share = None
        if shares:
            per_share = float(net_net_value) / float(shares)

        der_rec = {
            'Fiscal Year': fiscal,
            INDICATOR_NAME: {
                'Net-Net Value': to_native(net_net_value),
                'Per Share': to_native(per_share)
            }
        }
        der_records.append(der_rec)

    output_obj = {
        'scr_data': scr_records,
        'der_data': der_records
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_obj, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == '__main__':
    main()