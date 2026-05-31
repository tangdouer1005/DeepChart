#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,6259796000.0,16758951000.0,2163180000,-10499155000.0
2017,6570520000.0,23023050000.0,2486370000,-16452530000.0
2018,8307000000.0,23427000000.0,2559000000,-15120000000.0
2019,12103000000.0,26199000000.0,2655000000,-14096000000.0
2020,26717000000.0,28469000000.0,3249000000,-1752000000.0
2021,27100000000.0,31116000000.0,3100522833,-4016000000.0
2022,40917000000.0,36440000000.0,3475000000,4477000000.0
2023,49616000000.0,43009000000.0,3482750000,6607000000.0
2024,58360000000.0,48390000000.0,3498000000,9970000000.0
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'
PER_SHARE_NAME = '每股清算价值 (Per-Share Liquidation Value)'

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric types
    for col in ['Current Assets', 'Total Liabilities', 'Shares']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculation: Net-Net Value = Total Current Assets - Total Liabilities
    df['Calculated_NetNet'] = df['Current Assets'] - df['Total Liabilities']

    # Per-share liquidation value = Net-Net Value / Shares
    # Avoid division by zero
    df['Calculated_PerShare'] = df.apply(
        lambda r: (r['Calculated_NetNet'] / r['Shares']) if (pd.notnull(r['Shares']) and r['Shares'] != 0) else None,
        axis=1
    )

    # Prepare scr_data: original CSV rows as list of dicts
    scr_data = df.drop(columns=['Calculated_NetNet', 'Calculated_PerShare']).to_dict(orient='records')

    # Prepare der_data: calculated indicator per row
    der_data = []
    for _, row in df.iterrows():
        entry = {}
        # Preserve fiscal year key if present
        if 'Fiscal Year' in row and not pd.isnull(row['Fiscal Year']):
            # Convert to int if it's a whole number
            fy = int(row['Fiscal Year']) if float(row['Fiscal Year']).is_integer() else row['Fiscal Year']
            entry['Fiscal Year'] = fy
        # Main indicator: Net-Net Value (calculated)
        # Use native Python types for JSON serialization
        netnet = row['Calculated_NetNet']
        pershare = row['Calculated_PerShare']
        entry[INDICATOR_NAME] = (None if pd.isnull(netnet) else float(netnet))
        # Also include per-share liquidation value as supplementary derived data
        entry[PER_SHARE_NAME] = (None if pd.isnull(pershare) else float(pershare))
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to specified output path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()