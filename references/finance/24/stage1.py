#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,4111892000,6844493500.0,1438138000,0.6007591357928823,0.6502490824175343
2017,3445149000,8252369500.0,1567578000,0.4174739146132514,0.5449897812837703
2018,4059907000,9657115000.0,1708724000,0.4204057837149086,0.5791223789116351
2019,4779112000,12386880500.0,1861725000,0.3858204654513297,0.6104454132901678
2020,5107839000,15704772000.0,2037733000,0.325241206940158,0.6010577075745731
2021,5906809000,18264995000.0,2236094000,0.3233950515726941,0.6214379032740012
2022,6877169000,20817775500.0,2457306000,0.3303508100565308,0.6426864019191618
2023,6871557000,23899468000.0,2827394000,0.2875192451982613,0.5885366300534216
2024,7264787000,26990742500.0,3241479000,0.2691584716500481,0.5538094922810538
"""

def to_native(val):
    if pd.isna(val):
        return None
    # numpy integer/floats to python native
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    scr_data = []
    der_data = []

    for _, row in df.iterrows():
        # Build scr_data row with original columns, converted to native types
        scr_row = {}
        for col in df.columns:
            scr_row[col] = to_native(row[col])
        scr_data.append(scr_row)

        # Extract raw inputs for SGR calculation
        # Using Net Income, Avg Total Equity, Dividends as raw inputs.
        net_income = row.get("Net Income")
        avg_total_equity = row.get("Avg Total Equity")
        dividends = row.get("Dividends")

        # Safely convert to python floats/ints or handle missing
        try:
            ni = float(net_income) if not pd.isna(net_income) else None
        except Exception:
            ni = None
        try:
            equity = float(avg_total_equity) if not pd.isna(avg_total_equity) else None
        except Exception:
            equity = None
        try:
            div = float(dividends) if not pd.isna(dividends) else None
        except Exception:
            div = None

        # Calculate Retention Ratio = 1 - (Dividends / Net Income)
        if ni is None or ni == 0 or div is None:
            retention = None
        else:
            retention = 1.0 - (div / ni)

        # Calculate ROE = Net Income / Avg Total Equity
        if ni is None or equity is None or equity == 0:
            roe = None
        else:
            roe = ni / equity

        # SGR = ROE * Retention Ratio
        if roe is None or retention is None:
            sgr = None
        else:
            sgr = roe * retention

        der_row = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            "可持续增长率 (Sustainable Growth Rate, SGR)": to_native(sgr)
        }
        der_data.append(der_row)

    out_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()