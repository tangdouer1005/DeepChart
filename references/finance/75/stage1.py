#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import math

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,-497000000,149136000000.0,8032000000,-0.0033325286986374,17.16096579476861
2017,9195000000,146840000000.0,8132000000,0.0626191773358757,0.1156063077759651
2018,14824000000,151339000000.0,8500000000,0.0979522793199373,0.4266055045871559
2019,2924000000,149383500000.0,9000000000,0.019573781575609,-2.0779753761969904
2020,-5543000000,137950500000.0,9700000000,-0.0401810794451633,2.749954898069637
2021,15625000000,149533000000.0,10200000000,0.1044919850467789,0.3471999999999999
2022,35465000000,163330000000.0,11000000000,0.2171370844302945,0.6898350486395037
2023,21369000000,160119500000.0,11336000000,0.13345657462083,0.4695119097758435
2024,17661000000,156637500000.0,11800000000,0.1127507780703854,0.3318611630145518
"""

def to_native(val):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if val is None:
        return None
    if isinstance(val, (float, int, str, bool)):
        # handle NaN
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return None
        return val
    try:
        # numpy types
        if pd.isna(val):
            return None
    except Exception:
        pass
    try:
        return int(val)
    except Exception:
        try:
            return float(val)
        except Exception:
            return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA), dtype={
        "Fiscal Year": object,
        "Net Income": float,
        "Avg Total Equity": float,
        "Dividends": float,
        "ROE(Avg)": float,
        "Retention Ratio": float
    })

    # Prepare scr_data: raw rows as dictionaries with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            "Net Income": to_native(row["Net Income"]),
            "Avg Total Equity": to_native(row["Avg Total Equity"]),
            "Dividends": to_native(row["Dividends"]),
            "ROE(Avg)": to_native(row["ROE(Avg)"]),
            "Retention Ratio": to_native(row["Retention Ratio"])
        }
        scr_records.append(rec)

    # Calculate 可持续增长率 (Sustainable Growth Rate, SGR) for each row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native(row["Fiscal Year"])
        net_income = row["Net Income"]
        dividends = row["Dividends"]
        avg_equity = row["Avg Total Equity"]

        # Compute retention ratio safely: 1 - (Dividends / Net Income)
        if net_income is None or pd.isna(net_income) or net_income == 0:
            retention = None
        else:
            retention = 1.0 - (dividends / net_income)

        # Compute ROE = Net Income / Avg Total Equity
        if avg_equity is None or pd.isna(avg_equity) or avg_equity == 0:
            roe = None
        else:
            roe = net_income / avg_equity

        # SGR = ROE * retention
        if retention is None or roe is None:
            sgr = None
        else:
            sgr = roe * retention

        der_rec = {
            "Fiscal Year": fiscal_year,
            "可持续增长率 (Sustainable Growth Rate, SGR)": to_native(sgr)
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()