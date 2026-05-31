#!/usr/bin/env python3
import sys
import io
import json
import math
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,0.0,-47426000,11727951000.0,-0.0040438436347491,1.0
2017,0.0,323000000,15173921500.0,0.0212865210881709,1.0
2018,0.0,127478000,19297362500.0,0.0066059804804931,1.0
2023,861000000.0,208000000,97029000000.0,0.0021436890001958,-3.1394230769230766
2024,772000000.0,4136000000,99336000000.0,0.0416364661351373,0.8133462282398453
"""

def normalize_value(v):
    # Convert numpy types to native Python types and NaN to None
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # convert to regular float
        fv = float(v)
        # handle infinities
        if math.isfinite(fv):
            return fv
        return None
    return v

def safe_float(x):
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except Exception:
        pass
    try:
        return float(x)
    except Exception:
        return None

def compute_igr(dividends, net_income, total_assets):
    """
    Compute Internal Growth Rate (IGR) using:
      b = 1 - (Dividends / Net Income)
      ROA = Net Income / Total Assets
      IGR = (ROA * b) / (1 - (ROA * b))
    Return None if calculation is not possible (e.g., division by zero).
    """
    d = safe_float(dividends)
    ni = safe_float(net_income)
    ta = safe_float(total_assets)

    # Need net income and total assets to compute; if missing, return None
    if ni is None or ta is None:
        return None

    # retention ratio b: handle net income == 0
    if ni == 0.0:
        # undefined retention ratio when dividing by zero; treat as None
        return None
    b = 1.0 - (d / ni if d is not None else 0.0)

    # ROA
    if ta == 0.0:
        return None
    roa = ni / ta

    numerator = roa * b
    denom = 1.0 - numerator

    # protect against division by zero or non-finite results
    if denom == 0.0 or not math.isfinite(numerator) or not math.isfinite(denom):
        return None

    igr = numerator / denom
    if not math.isfinite(igr):
        return None
    return igr

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows with native python types
    scr_records = df.to_dict(orient="records")
    scr_data = []
    for r in scr_records:
        cleaned = {k: normalize_value(v) for k, v in r.items()}
        scr_data.append(cleaned)

    # Compute IGR for each row
    igr_key = "内部增长率 (Internal Growth Rate, IGR)"
    der_data = []
    for r in scr_records:
        fy = r.get("Fiscal Year", None)
        dividends = r.get("Dividends", None)
        net_income = r.get("Net Income", None)
        avg_assets = r.get("Avg Total Assets", None)

        igr_value = compute_igr(dividends, net_income, avg_assets)
        entry = {}
        # include year if present
        if fy is not None and not pd.isna(fy):
            # convert to int if it's integer-like
            try:
                entry["Year"] = int(fy)
            except Exception:
                entry["Year"] = normalize_value(fy)
        # normalized igr value (None will be serialized as null)
        entry[igr_key] = normalize_value(igr_value)
        der_data.append(entry)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()