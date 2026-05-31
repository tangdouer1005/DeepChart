#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,16187000000.0,61463000000.0,1631000000,-45276000000.0
2017,21223000000.0,65689000000.0,1603000000,-44466000000.0
2018,16945000000.0,67798000000.0,1546000000,-50853000000.0
2019,49519000000.0,97287000000.0,1484000000,-47768000000.0
2020,24173000000.0,137468000000.0,1673000000,-113295000000.0
2021,27928000000.0,131093000000.0,1777000000,-103165000000.0
2022,28463000000.0,121518000000.0,1778000000,-93055000000.0
2023,33002000000.0,124314000000.0,1773000000,-91312000000.0
2024,25582000000.0,131797000000.0,1773000000,-106215000000.0
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'
PER_SHARE_NAME = '每股清算价值 (Per-Share Net-Net Value)'

def to_native(v):
    # Convert numpy and pandas scalar types to native python types for json serialization
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    if hasattr(v, "item"):
        try:
            return v.item()
        except Exception:
            pass
    # Fallback: return as-is
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data as a list of dicts mirroring input CSV (with native python types)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate NNWC and per-share liquidation value for each row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row['Fiscal Year'])
        current_assets = row['Current Assets']
        total_liabilities = row['Total Liabilities']
        shares = row['Shares']

        # Calculation per reference:
        # Net-Net Value = Total Current Assets - Total Liabilities
        net_net_value = current_assets - total_liabilities

        # Per-share clearing value = Net-Net Value / Shares (guard against zero)
        per_share = None
        try:
            if shares != 0 and not pd.isna(shares):
                per_share = net_net_value / shares
        except Exception:
            per_share = None

        rec = {
            'Fiscal Year': to_native(fiscal_year),
            INDICATOR_NAME: to_native(net_net_value),
            PER_SHARE_NAME: to_native(per_share)
        }
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()