#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,2021800000,21444750000.0,238400000.0,0.0942794856549971,0.8820852705509942
2017,2225000000,23476150000.0,237000000.0,0.0947770396764375,0.8934831460674157
2018,2938000000,26499500000.0,266000000.0,0.110870016415404,0.9094622191967324
2019,3696000000,28630500000.0,297000000.0,0.1290931000157175,0.9196428571428572
2020,6375000000,32091000000.0,337000000.0,0.1986538281761241,0.9471372549019608
2021,7725000000,37650000000.0,395000000.0,0.2051792828685259,0.9488673139158575
2022,6950000000,42385500000.0,455000000.0,0.1639711693857569,0.9345323741007194
2023,5995000000,45356500000.0,523000000.0,0.1321751016943547,0.9127606338615512
2024,6335000000,48159500000.0,583000000.0,0.1315420633519866,0.907971586424625
"""

INDICATOR_NAME = "可持续增长率 (Sustainable Growth Rate, SGR)"

def to_py_scalar(val):
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    # try to convert numeric-like strings
    try:
        if isinstance(val, str):
            if val.isdigit():
                return int(val)
            f = float(val)
            return f
    except Exception:
        pass
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA), skipinitialspace=True)

    # Prepare scr_data as list of dicts with Python native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_scalar(row[col])
        scr_records.append(rec)

    # Calculate SGR for each row using the referenced formulas:
    # Retention Ratio = 1 - (Dividends / Net Income)
    # ROE = Net Income / Avg Total Equity
    # SGR = ROE * Retention Ratio
    der_records = []
    for _, row in df.iterrows():
        ni = row.get("Net Income")
        div = row.get("Dividends")
        equity = row.get("Avg Total Equity")
        fiscal = row.get("Fiscal Year")

        # Guard against zero or missing values
        retention = None
        roe_calc = None
        sgr = None

        # compute retention
        try:
            if pd.notna(ni) and pd.notna(div) and float(ni) != 0.0:
                retention = 1.0 - (float(div) / float(ni))
        except Exception:
            retention = None

        # compute ROE from raw data (Net Income / Avg Total Equity)
        try:
            if pd.notna(ni) and pd.notna(equity) and float(equity) != 0.0:
                roe_calc = float(ni) / float(equity)
        except Exception:
            roe_calc = None

        # compute SGR
        try:
            if (retention is not None) and (roe_calc is not None):
                sgr = roe_calc * retention
        except Exception:
            sgr = None

        der_rec = {
            "Fiscal Year": to_py_scalar(fiscal),
            INDICATOR_NAME: to_py_scalar(sgr) if sgr is not None else None
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()