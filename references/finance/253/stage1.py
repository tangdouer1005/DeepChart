#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,7017000000,36061000000.0,2261000000,0.1945869498904633,0.6777825281459313
2017,10558000000,44115000000.0,2773000000,0.2393290264082511,0.737355559765107
2018,11986000000,50764500000.0,3320000000,0.2361098799357819,0.7230101785416319
2019,13839000000,54656000000.0,3932000000,0.2532018442622951,0.7158754245248935
2020,15403000000,61553500000.0,4584000000,0.2502375981869431,0.7023956372135298
2021,17285000000,68625500000.0,5280000000,0.2518743032837647,0.694532831935204
2022,20120000000,74766000000.0,5991000000,0.2691062782548217,0.7022365805168986
2023,22381000000,83264000000.0,6761000000,0.2687956379707917,0.6979134086948751
2024,14405000000,90707000000.0,7533000000,0.1588080302512485,0.4770565775772301
"""

def to_python_value(v):
    # Convert numpy / pandas types to native Python types, and NaN -> None
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    # For plain Python numeric types
    if isinstance(v, (int, float, str, bool)):
        return v
    # Fallback: try to convert
    try:
        return int(v)
    except Exception:
        try:
            return float(v)
        except Exception:
            return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dictionaries preserving original headers and values
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_value(row[col])
        scr_records.append(rec)

    # Calculate Sustainable Growth Rate (SGR) for each row
    der_records = []
    for _, row in df.iterrows():
        # Extract raw inputs
        net_income = row.get("Net Income", np.nan)
        dividends = row.get("Dividends", np.nan)
        avg_total_equity = row.get("Avg Total Equity", np.nan)

        # Safe numeric conversions / checks
        try:
            ni = float(net_income) if not pd.isna(net_income) else None
        except Exception:
            ni = None
        try:
            div = float(dividends) if not pd.isna(dividends) else None
        except Exception:
            div = None
        try:
            equity = float(avg_total_equity) if not pd.isna(avg_total_equity) else None
        except Exception:
            equity = None

        # Retention ratio: 1 - (Dividends / Net Income)
        retention = None
        if ni is None or ni == 0 or div is None:
            retention = None
        else:
            retention = 1.0 - (div / ni)

        # ROE: Net Income / Avg Total Equity
        roe = None
        if ni is None or equity is None or equity == 0:
            roe = None
        else:
            roe = ni / equity

        # SGR = ROE * retention
        sgr = None
        if (roe is None) or (retention is None):
            sgr = None
        else:
            sgr = roe * retention

        # Build output record. Include Fiscal Year if present.
        rec = {}
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_python_value(row["Fiscal Year"])
        rec["可持续增长率 (Sustainable Growth Rate, SGR)"] = to_python_value(sgr)
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()