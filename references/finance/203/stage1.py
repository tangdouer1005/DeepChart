#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,8901000000,47976000000.0,2541000000.0,0.1855302651325663,0.7145264577013819
2017,9452000000,50574500000.0,2631000000.0,0.1868926039802667,0.7216462124418113
2018,3587000000,50042000000.0,3140000000.0,0.0716797889772591,0.1246166713130749
2019,11083000000,34004500000.0,2932000000.0,0.3259274507785734,0.7354506902463231
2020,10135000000,16929500000.0,3070000000.0,0.5986591452789509,0.697089294523927
2021,13746000000,8656000000.0,3063000000.0,1.5880314232902033,0.7771715408118726
2022,6717000000,-491000000.0,3457000000.0,-13.680244399185336,0.4853357153491142
2023,8503000000,-2573500000.0,3668000000.0,-3.304060617835632,0.5686228389980007
2024,10467000000,4888500000.0,4391000000.0,2.1411475912856703,0.5804910671634662
"""

INDICATOR_NAME = "可持续增长率 (Sustainable Growth Rate, SGR)"

def to_python_native(val):
    """Convert numpy / pandas scalar types to native Python types for JSON serialization."""
    if val is None:
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # convert NaN to None
        if np.isnan(val):
            return None
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return val

def dataframe_to_records_native(df):
    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    # Convert numpy types to native Python types
    native_records = []
    for rec in records:
        native_rec = {}
        for k, v in rec.items():
            native_rec[k] = to_python_native(v)
        native_records.append(native_rec)
    return native_records

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["Net Income", "Avg Total Equity", "Dividends"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate SGR per reference: Retention Ratio = 1 - (Dividends / Net Income)
    # ROE = Net Income / Avg Total Equity
    sgr_list = []
    for idx, row in df.iterrows():
        fiscal_year = row.get("Fiscal Year")
        net_income = row.get("Net Income")
        dividends = row.get("Dividends")
        avg_equity = row.get("Avg Total Equity")

        # Compute retention ratio safely
        retention = None
        try:
            if net_income is not None and net_income != 0:
                retention = 1.0 - (dividends / net_income)
            else:
                retention = None
        except Exception:
            retention = None

        # Compute ROE safely
        roe = None
        try:
            if avg_equity is not None and avg_equity != 0:
                roe = net_income / avg_equity
            else:
                roe = None
        except Exception:
            roe = None

        # Compute SGR = ROE * retention
        sgr = None
        if retention is not None and roe is not None:
            sgr = roe * retention
            # If result is NaN or infinite, set to None
            if isinstance(sgr, float) and (np.isnan(sgr) or np.isinf(sgr)):
                sgr = None

        sgr_record = {
            "Fiscal Year": to_python_native(fiscal_year),
            INDICATOR_NAME: to_python_native(sgr)
        }
        sgr_list.append(sgr_record)

    output = {
        "scr_data": dataframe_to_records_native(df),
        "der_data": sgr_list
    }

    # Write JSON to output path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()