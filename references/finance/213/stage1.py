#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,33782000000,69153000000,2844400000,-35371000000
2017,26494000000,64628000000,2740400000,-38134000000
2018,23320000000,65427000000,2656700000,-42107000000
2019,22473000000,67516000000,2539500000,-45043000000
2020,27987000000,73822000000,2625800000,-45835000000
2021,23091000000,72653000000,2601000000,-49562000000
2022,21653000000,70354000000,2539100000,-48701000000
2023,22648000000,73764000000,2483900000,-51116000000
2024,24709000000,71812000000,2471900000,-47103000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert DataFrame rows to native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None,
            "Current Assets": int(row["Current Assets"]) if not pd.isna(row["Current Assets"]) else None,
            "Total Liabilities": int(row["Total Liabilities"]) if not pd.isna(row["Total Liabilities"]) else None,
            "Shares": int(row["Shares"]) if not pd.isna(row["Shares"]) else None,
            "Net-Net Value": int(row["Net-Net Value"]) if not pd.isna(row["Net-Net Value"]) else None
        }
        scr_data.append(rec)

    # Calculate the indicator for each row using the formula:
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares
    der_data = []
    for rec in scr_data:
        ca = rec["Current Assets"]
        tl = rec["Total Liabilities"]
        shares = rec["Shares"]

        # Compute Net-Net Value dynamically
        if ca is None or tl is None:
            net_net = None
        else:
            net_net = ca - tl  # integer

        # Compute per-share liquidation value dynamically; protect divide-by-zero
        if net_net is None or shares in (None, 0):
            per_share = None
        else:
            per_share = net_net / shares  # float

        der_rec = {
            "Fiscal Year": rec["Fiscal Year"],
            INDICATOR_NAME: per_share
        }
        der_data.append(der_rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()