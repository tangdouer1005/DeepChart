#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,20539000000,76040000000.0,11006000000,0.2701078379800105,0.4641413895515848
2017,25489000000,72195500000.0,11845000000,0.3530552458255708,0.535289732825925
2018,16571000000,77556000000.0,12699000000,0.2136649646706895,0.2336612153762597
2019,39240000000,92524000000.0,13811000000,0.4241061778565561,0.6480377166156983
2020,44281000000,110317000000.0,15137000000,0.4013977900051669,0.6581603848151578
2021,61271000000,130146000000.0,16521000000,0.4707866549874756,0.730361835125916
2022,72738000000,154265000000.0,18135000000,0.4715133050270638,0.7506805246226181
2023,72361000000,186382500000.0,19800000000,0.3882392391989591,0.7263719406862813
2024,88136000000,237350000000.0,21771000000,0.3713334737729092,0.7529840246891168
"""

INDICATOR_NAME = "可持续增长率 (Sustainable Growth Rate, SGR)"

def to_python_native(val):
    """Convert numpy/pandas scalar types to native Python types for JSON serialization."""
    if val is None:
        return None
    # pandas NA
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    # numpy integer
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    # Python int/float/bool/str
    if isinstance(val, (int, float, bool, str)):
        return val
    # For numpy arrays or other types, convert to string fallback
    return str(val)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate SGR for each row using formulas:
    # Retention Ratio = 1 - (Dividends / Net Income)
    # ROE = Net Income / Avg Total Equity
    # SGR = ROE * Retention Ratio
    der_records = []
    for _, row in df.iterrows():
        net_income = row.get("Net Income")
        avg_total_equity = row.get("Avg Total Equity")
        dividends = row.get("Dividends")

        # Defensive handling for zero or missing denominators
        retention = None
        roe = None
        sgr = None

        # Calculate retention ratio if possible
        try:
            if (net_income is not None) and (not pd.isna(net_income)) and (net_income != 0):
                retention = 1.0 - (dividends / net_income)
            else:
                retention = None
        except Exception:
            retention = None

        # Calculate ROE if possible
        try:
            if (avg_total_equity is not None) and (not pd.isna(avg_total_equity)) and (avg_total_equity != 0):
                roe = net_income / avg_total_equity
            else:
                roe = None
        except Exception:
            roe = None

        # Calculate SGR if both components available
        try:
            if (retention is not None) and (roe is not None):
                sgr = roe * retention
            else:
                sgr = None
        except Exception:
            sgr = None

        der_rec = {
            "Fiscal Year": to_python_native(row.get("Fiscal Year")),
            INDICATOR_NAME: to_python_native(sgr)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output file with UTF-8 encoding
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()