#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,34010000000,64050000000,4367000000,-30040000000
2017,36545000000,68919000000,4324000000,-32374000000
2018,24930000000,64158000000,4299000000,-39228000000
2019,20411000000,65283000000,4314000000,-44872000000
2020,19240000000,66012000000,4323000000,-46772000000
2021,22545000000,69494000000,4340000000,-46949000000
2022,22591000000,66937000000,4350000000,-44346000000
2023,26732000000,70223000000,4339000000,-43491000000
2024,25997000000,74177000000,4320000000,-48180000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'
PER_SHARE_NAME = '每股清算价值 (Per Share Liquidation Value)'

def load_data(csv_text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(csv_text))

def calculate_nnwc(df: pd.DataFrame):
    results = []
    for _, row in df.iterrows():
        # Ensure numeric Python native types
        fiscal_year = int(row['Fiscal Year'])
        current_assets = float(row['Current Assets'])
        total_liabilities = float(row['Total Liabilities'])
        shares = float(row['Shares'])

        # Net-Net Value = Total Current Assets - Total Liabilities
        net_net_value = current_assets - total_liabilities

        # Per-share liquidation value
        per_share_value = None
        if shares != 0:
            per_share_value = net_net_value / shares
        else:
            per_share_value = None

        # Use Python native numeric types (int for year, floats for values)
        item = {
            'Fiscal Year': fiscal_year,
            INDICATOR_NAME: float(net_net_value),
            PER_SHARE_NAME: (float(per_share_value) if per_share_value is not None else None)
        }
        results.append(item)
    return results

def build_scr_data(df: pd.DataFrame):
    records = []
    for _, row in df.iterrows():
        rec = {
            'Fiscal Year': int(row['Fiscal Year']),
            'Current Assets': int(row['Current Assets']),
            'Total Liabilities': int(row['Total Liabilities']),
            'Shares': int(row['Shares']),
            # include the provided Net-Net Value column from the source CSV as-is
            'Net-Net Value': int(row['Net-Net Value'])
        }
        records.append(rec)
    return records

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = load_data(CSV_DATA)
    scr_data = build_scr_data(df)
    der_data = calculate_nnwc(df)

    out_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()