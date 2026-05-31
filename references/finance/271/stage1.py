#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np
import numbers

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2017,6216000000,13643000000,199203000000.0,0.0684879243786489,0.5443817342226782
2018,6124000000,9862000000,201673500000.0,0.0489008223688288,0.3790306225917663
2019,6102000000,6670000000,211908500000.0,0.0314758492462548,0.0851574212893553
2020,6048000000,14881000000,227895000000.0,0.0652976151297746,0.5935757005577582
2021,6116000000,13510000000,244495500000.0,0.0552566407152687,0.5472982975573649
2022,6152000000,13673000000,248678000000.0,0.0549827487755249,0.550062166313172
2023,6114000000,11680000000,244158500000.0,0.0478377775092818,0.4765410958904109
2024,6140000000,15511000000,247928000000.0,0.0625625181504307,0.6041518922055316
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def py_value(x):
    """Convert numpy/pandas scalars to native Python types for JSON serialization."""
    if pd.isna(x):
        return None
    if isinstance(x, (np.integer, int)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        # Convert to python float; keep full precision
        return float(x)
    if isinstance(x, numbers.Number):
        return float(x)
    return x

def compute_igr(dividends, net_income, avg_total_assets):
    """
    Compute Internal Growth Rate (IGR) based on:
      b = 1 - (dividends / net_income)
      ROA = net_income / avg_total_assets
      IGR = (ROA * b) / (1 - (ROA * b))
    Returns None if computation impossible (e.g., division by zero).
    """
    try:
        # Ensure inputs are floats
        d = float(dividends)
        ni = float(net_income)
        assets = float(avg_total_assets)
    except Exception:
        return None

    # Protect against zero or near-zero denominators
    if ni == 0 or assets == 0:
        return None

    b = 1.0 - (d / ni)
    roa = ni / assets

    product = roa * b
    denom = 1.0 - product

    # If denom is zero (or extremely close), return None to indicate undefined/inf
    if abs(denom) < 1e-12:
        return None

    igr = product / denom
    return igr

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: raw input rows as list of dicts with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = py_value(row[col])
        scr_records.append(rec)

    # Build der_data: compute IGR per row
    der_records = []
    for _, row in df.iterrows():
        dividends = row.get("Dividends")
        net_income = row.get("Net Income")
        avg_total_assets = row.get("Avg Total Assets")

        igr_value = compute_igr(dividends, net_income, avg_total_assets)
        # Convert to native Python type
        igr_py = py_value(igr_value)

        der_rec = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            der_rec["Fiscal Year"] = py_value(row["Fiscal Year"])
        der_rec[INDICATOR_NAME] = igr_py
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()