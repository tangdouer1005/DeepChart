#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Avg Total Equity,Dividends,ROE(Avg),Retention Ratio
2016,3920000000,42382000000.0,5124000000,0.0924920957010051,-0.3071428571428571
2017,2394000000,37212000000.0,5167000000,0.064334085778781,-1.1583124477861322
2018,6220000000,30518500000.0,5172000000,0.2038108032832544,0.1684887459807074
2019,9843000000,26304000000.0,5695000000,0.3742016423357664,0.4214162348877375
2020,7067000000,25612000000.0,6215000000,0.2759253474933625,0.120560350926843
2021,13049000000,31750500000.0,6610000000,0.4109856537692319,0.4934477737757682
2022,14519000000,42087500000.0,7012000000,0.344971784971785,0.5170466285556856
2023,365000000,41786000000.0,7445000000,0.0087349830086631,-19.3972602739726
2024,17117000000,41947000000.0,7840000000,0.4080625551290914,0.541975813518724
"""

INDICATOR_NAME = "可持续增长率 (Sustainable Growth Rate, SGR)"

def to_py(val):
    """Convert numpy / pandas scalars to native Python types; convert NaN to None."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    # for plain Python numeric types or strings
    return val

def compute_sgr(net_income, dividends, avg_total_equity):
    """
    SGR = ROE * Retention Ratio
    Retention Ratio = 1 - (Dividends / Net Income)
    ROE = Net Income / Avg Total Equity
    Handle division by zero by returning None for invalid computations.
    """
    # Validate inputs
    if net_income is None or avg_total_equity is None or dividends is None:
        return None
    # Protect against zero denominators
    try:
        if net_income == 0:
            return None
        retention = 1.0 - (dividends / net_income)
    except Exception:
        return None
    try:
        if avg_total_equity == 0:
            return None
        roe = net_income / avg_total_equity
    except Exception:
        return None
    # Final SGR
    try:
        sgr = roe * retention
    except Exception:
        return None
    return sgr

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows as list of dicts with native types
    raw_records = []
    for rec in df.to_dict(orient="records"):
        cleaned = {k: to_py(v) for k, v in rec.items()}
        raw_records.append(cleaned)

    # Prepare der_data: compute SGR for each row
    der_records = []
    for row in raw_records:
        # Extract needed fields with safe handling
        net_income = row.get("Net Income")
        dividends = row.get("Dividends")
        avg_eq = row.get("Avg Total Equity")
        sgr_val = compute_sgr(net_income, dividends, avg_eq)
        # Convert to native python type (float) or None
        sgr_val = to_py(sgr_val)
        entry = {}
        # If Fiscal Year present, include it
        if "Fiscal Year" in row:
            entry["Fiscal Year"] = row["Fiscal Year"]
        entry[INDICATOR_NAME] = sgr_val
        der_records.append(entry)

    output = {
        "scr_data": raw_records,
        "der_data": der_records
    }

    # Write JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()