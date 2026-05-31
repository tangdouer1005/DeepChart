#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,1460000000,17396500000.0,55000000.0,0.0839249274279309,0.9623287671232876
2017,4536000000,20397500000.0,55000000.0,0.2223801936511827,0.9878747795414462
2018,2888000000,23638500000.0,0.0,0.1221735727732301,1.0
2019,3468000000,26753500000.0,0.0,0.1296278991533818,1.0
2020,3064000000,47066500000.0,54080000000.0,0.0650993806635292,-16.650130548302872
2021,3024000000,67223000000.0,0.0,0.0449846034839266,1.0
2022,2590000000,69379000000.0,0.0,0.0373311809048847,1.0
2023,8317000000,67185500000.0,747000000.0,0.1237915919357599,0.9101839605627028
2024,11339000000,63228000000.0,3300000000.0,0.1793351047004491,0.70896904488932
"""

INDICATOR_NAME = "可持续增长率 (Sustainable Growth Rate, SGR)"

def to_json_compatible(value):
    # Convert pandas/numpy types and NaN to JSON serializable Python types
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.ndarray, list, tuple)):
        return [to_json_compatible(v) for v in value]
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with JSON-serializable values
    scr_records_raw = df.to_dict(orient='records')
    scr_records = []
    for rec in scr_records_raw:
        conv = {}
        for k, v in rec.items():
            conv[k] = to_json_compatible(v)
        scr_records.append(conv)

    # Calculate SGR per row dynamically
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = row.get("Fiscal Year")
        net_income = row.get("Net Income")
        avg_equity = row.get("Avg Total Equity")
        dividends = row.get("Dividends")

        # Retention Ratio = 1 - (Dividends / Net Income)
        if pd.isna(net_income) or net_income == 0:
            retention = None
        else:
            retention = 1.0 - (dividends / net_income)

        # ROE = Net Income / Avg Total Equity
        if pd.isna(avg_equity) or avg_equity == 0:
            roe = None
        else:
            roe = net_income / avg_equity

        # SGR = ROE * Retention Ratio
        if (retention is None) or (roe is None):
            sgr = None
        else:
            sgr = roe * retention

        der_rec = {
            "Fiscal Year": to_json_compatible(fiscal_year),
            INDICATOR_NAME: to_json_compatible(sgr)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()