#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,13228000000,12991000000,1101000016,237000000
2017,13797000000,15761000000,1072000016,-1964000000
2018,16171000000,19371000000,1047000015,-3200000000
2019,16902000000,23245000000,1022000000,-6343000000
2020,19113000000,27067000000,1006000000,-7954000000
2021,16949000000,30257000000,992000000,-13308000000
2022,16606000000,32347000000,971000000,-15741000000
2023,18961000000,35451000000,946000000,-16490000000
2024,19724000000,41566000000,927000000,-21842000000
"""

INDICATOR_NAME = '格雷厄姆“烟蒂股”净值 (Graham\'s Net-Net Working Capital, NNWC)'

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA), sep=",")

    # Prepare scr_data: mirror the original CSV rows (with native Python types)
    scr_data = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": int(row["Fiscal Year"]),
            "Current Assets": int(row["Current Assets"]),
            "Total Liabilities": int(row["Total Liabilities"]),
            "Shares": int(row["Shares"]),
            # Include provided Net-Net Value column as part of raw scraped data,
            # but we will compute our own values in der_data dynamically.
            "Net-Net Value": int(row["Net-Net Value"])
        }
        scr_data.append(rec)

    # Compute the NNWC indicator for each row:
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares Outstanding
    der_data = []
    for row in scr_data:
        current_assets = row["Current Assets"]
        total_liabilities = row["Total Liabilities"]
        shares = row["Shares"]

        net_net_value = current_assets - total_liabilities  # may be negative
        per_share_value = None
        if shares and shares != 0:
            per_share_value = net_net_value / shares
        else:
            per_share_value = None

        der_rec = {
            "Fiscal Year": row["Fiscal Year"],
            INDICATOR_NAME: per_share_value
        }
        der_data.append(der_rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with Unicode characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()