#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np
import numbers

def to_python_value(v):
    # Convert pandas/numpy scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, bytes):
        try:
            return v.decode()
        except Exception:
            return str(v)
    if isinstance(v, str):
        return v
    if isinstance(v, bool):
        return v
    if isinstance(v, numbers.Integral):
        return int(v)
    if isinstance(v, numbers.Real):
        return float(v)
    # Fallback
    try:
        return int(v)
    except Exception:
        try:
            return float(v)
        except Exception:
            return str(v)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    csv_data = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,7631000000,10119000000,18300000000,18287000000,17750000000,100238356.16438356
2017,11708000000,10002000000,18251000000,17781000000,21710000000,98717808.21917808
2018,8934000000,10503000000,18297000000,18724000000,19437000000,101427397.26027398
2019,11750000000,10586000000,18447000000,19238000000,22336000000,103246575.34246576
2020,11809000000,10523000000,18063000000,17618000000,22332000000,97756164.38356164
2021,9175000000,10146000000,19061000000,17924000000,19321000000,101328767.12328768
2022,7079000000,10527000000,18279000000,19309000000,17606000000,102980821.91780822
2023,10123000000,9206000000,20722000000,21245000000,19329000000,114978082.19178082
2024,9023000000,10023000000,22647000000,18975000000,19046000000,114032876.71232876
"""

    df = pd.read_csv(io.StringIO(csv_data))

    # Calculation for Defensive Interval Ratio (DIR)
    # Quick Assets is provided in CSV as 'Quick Assets'. Use that directly.
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption

    # Ensure numeric columns are numeric
    numeric_cols = ['Cash & Equiv', 'Receivables', 'Operating Expenses', 'Cost of Revenue', 'Quick Assets', 'Daily Burn']
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    daily_cash_consumption = (df['Operating Expenses'] + df['Cost of Revenue']) / 365.0
    # Use Quick Assets column; if missing or NaN, fallback to Cash & Equiv + Receivables
    if 'Quick Assets' in df.columns:
        quick_assets = df['Quick Assets'].copy()
        # where Quick Assets is NaN, try to compute from Cash & Equiv + Receivables
        mask_na_q = quick_assets.isna()
        if mask_na_q.any():
            fallback = df['Cash & Equiv'].fillna(0) + df['Receivables'].fillna(0)
            quick_assets.loc[mask_na_q] = fallback.loc[mask_na_q]
    else:
        quick_assets = df['Cash & Equiv'].fillna(0) + df['Receivables'].fillna(0)

    # Avoid division by zero: if daily_cash_consumption is zero or NaN, set DIR to None
    dir_values = []
    for qa, dcc in zip(quick_assets, daily_cash_consumption):
        if pd.isna(qa) or pd.isna(dcc) or dcc == 0:
            dir_values.append(None)
        else:
            dir_values.append(float(qa) / float(dcc))

    # Prepare scr_data: original CSV rows as list of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_value(row[col])
        scr_records.append(rec)

    # Prepare der_data: each record contains Fiscal Year and calculated DIR
    der_records = []
    for idx, row in df.iterrows():
        fy = to_python_value(row['Fiscal Year']) if 'Fiscal Year' in df.columns else None
        dir_val = dir_values[idx]
        # Use the exact indicator name as key
        rec = {}
        if fy is not None:
            rec['Fiscal Year'] = fy
        rec['防御区间比率 (Defensive Interval Ratio, DIR)'] = to_python_value(dir_val) if dir_val is not None else None
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()