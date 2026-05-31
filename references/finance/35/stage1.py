#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,45781000000,64117000000,9680000000,-18336000000
2017,60197000000,103601000000,9860000000,-43404000000
2018,75101000000,119099000000,10000000000,-43998000000
2019,96334000000,163188000000,10080000000,-66854000000
2020,132733000000,227791000000,10200000000,-95058000000
2021,161580000000,282304000000,10300000000,-120724000000
2022,146791000000,316632000000,10189000000,-169841000000
2023,172351000000,325979000000,10492000000,-153628000000
2024,190867000000,338924000000,10721000000,-148057000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def to_py(v):
    # Convert numpy/pandas scalar to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if hasattr(v, 'item'):
        return v.item()
    return v

def compute_nnwc_per_share(current_assets, total_liabilities, shares):
    # Net-Net Value = Total Current Assets - Total Liabilities
    net_net_value = current_assets - total_liabilities
    # 每股清算价值 = Net-Net Value / Shares
    # Handle division by zero defensively
    if shares == 0 or pd.isna(shares):
        per_share = None
    else:
        per_share = net_net_value / shares
    return net_net_value, per_share

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculate per-row Net-Net and per-share liquidation value
    computed = []
    for _, row in df.iterrows():
        ca = row.get('Current Assets')
        tl = row.get('Total Liabilities')
        sh = row.get('Shares')
        net_net, per_share = compute_nnwc_per_share(ca, tl, sh)
        computed.append({
            'Fiscal Year': to_py(row.get('Fiscal Year')),
            INDICATOR_NAME: to_py(per_share)
        })

    # Prepare scr_data (original scraped data) with native Python types
    scr_data = []
    for rec in df.to_dict(orient='records'):
        pyrec = {k: to_py(v) for k, v in rec.items()}
        scr_data.append(pyrec)

    output = {
        "scr_data": scr_data,
        "der_data": computed
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()