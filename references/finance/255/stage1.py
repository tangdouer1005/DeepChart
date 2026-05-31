#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    csv_data = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,33748000000,82270000000,968000000,-48522000000
2017,37084000000,87035000000,985000000,-49951000000
2018,38692000000,95994000000,983000000,-57302000000
2019,42634000000,111727000000,966000000,-69093000000
2020,53718000000,126750000000,961000000,-73032000000
2021,61758000000,135727000000,956000000,-73969000000
2022,69069000000,159358000000,950000000,-90289000000
2023,78437000000,174801000000,938000000,-96364000000
2024,85779000000,195687000000,929000000,-109908000000
"""

    df = pd.read_csv(io.StringIO(csv_data))

    # Calculation for 格雷厄姆“烟蒂股”净值 (Graham's Net-Net Working Capital, NNWC)
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value (optional, not required) = Net-Net Value / Shares
    net_net_series = df['Current Assets'] - df['Total Liabilities']
    per_share_series = net_net_series / df['Shares']

    indicator_key = "格雷厄姆“烟蒂股”净值 (Graham's Net-Net Working Capital, NNWC)"

    # Prepare scr_data: original CSV rows as list of dicts, converting numpy types to native python types
    raw_records = df.to_dict(orient='records')
    scr_data = []
    for rec in raw_records:
        cleaned = {}
        for k, v in rec.items():
            if pd.isna(v):
                cleaned[k] = None
            elif isinstance(v, (np.integer,)):
                cleaned[k] = int(v)
            elif isinstance(v, (np.floating,)):
                cleaned[k] = float(v)
            else:
                cleaned[k] = v
        scr_data.append(cleaned)

    # Prepare der_data: calculated indicator for each row (include Fiscal Year)
    der_data = []
    for idx, row in df.iterrows():
        year = row.get('Fiscal Year')
        net_net_value = net_net_series.iloc[idx]
        # Convert to native types
        if pd.isna(net_net_value):
            nn_value_out = None
        elif isinstance(net_net_value, (np.integer,)):
            nn_value_out = int(net_net_value)
        elif isinstance(net_net_value, (np.floating,)):
            # if it's integer-valued float, cast to int for cleaner output when appropriate
            if net_net_value.is_integer():
                nn_value_out = int(net_net_value)
            else:
                nn_value_out = float(net_net_value)
        else:
            nn_value_out = net_net_value

        der_record = {
            "Fiscal Year": int(year) if not pd.isna(year) else None,
            indicator_key: nn_value_out
        }
        der_data.append(der_record)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()