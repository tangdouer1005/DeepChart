#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Operating Income,Income Tax,Pretax Income,Effective Tax Rate,NOPAT,Avg Invested Capital
2016,7883000000,2021000000,8012000000,0.2522466300549176,5894539815.277085,37338500000.0
2017,12144000000,4995000000,11694000000,0.4271421241662391,6956786044.125193,43256000000.0
2018,12954000000,2505000000,12806000000,0.1956114321411838,10420049508.043104,42947500000.0
2019,15001000000,2804000000,14884000000,0.1883902176834184,12174958344.53104,46103500000.0
2020,14081000000,2924000000,13790000000,0.212037708484409,11095297026.831038,45832000000.0
2021,15804000000,3752000000,16063000000,0.2335802776567266,12112497291.913092,43089000000.0
2022,18813000000,3179000000,18136000000,0.1752867225408028,15515330888.839876,42210500000.0
2023,21000000000,3764000000,21037000000,0.1789228502162856,17242620145.458,42679000000.0
2024,23595000000,4173000000,23916000000,0.1744856999498243,19478009909.68389,45507000000.0
"""

def to_py_value(x):
    if pd.isna(x):
        return None
    t = type(x)
    # numpy integer/float handling
    if np.issubdtype(t, np.integer):
        return int(x)
    if np.issubdtype(t, np.floating):
        return float(x)
    return x

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation for 投入资本回报率 (Return on Invested Capital, ROIC)
    # Using provided raw parameters: NOPAT and Avg Invested Capital
    # ROIC = NOPAT / Avg Invested Capital
    # Respect division by zero
    roic_series = []
    for idx, row in df.iterrows():
        nopat = row.get("NOPAT")
        invested = row.get("Avg Invested Capital")
        try:
            if pd.isna(nopat) or pd.isna(invested) or invested == 0:
                roic = None
            else:
                roic = float(nopat) / float(invested)
        except Exception:
            roic = None
        roic_series.append(roic)

    # Prepare scr_data: original rows as list of dicts with native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_value(row[col])
        scr_data.append(rec)

    # Prepare der_data: calculated ROIC per corresponding row
    roic_key = "投入资本回报率 (Return on Invested Capital, ROIC)"
    der_data = []
    for i, row in df.iterrows():
        entry = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = to_py_value(row["Fiscal Year"])
        # include the calculated ROIC (derived dynamically)
        entry[roic_key] = to_py_value(roic_series[i])
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()