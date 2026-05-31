#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,7009000000,9373000000,-2364000000,41247500000.0
2017,7957000000,9783000000,-1826000000,42757500000.0
2018,8630000000,12031000000,-3401000000,43747500000.0
2019,11121000000,13165000000,-2044000000,44266000000.0
2020,11242000000,13723000000,-2481000000,47619500000.0
2021,12866000000,18839000000,-5973000000,60908500000.0
2022,16433000000,16571000000,-138000000,71228500000.0
2023,17105000000,14615000000,2490000000,74160500000.0
2024,15143000000,21172000000,-6029000000,76487500000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def to_native(val):
    """Convert pandas/numpy scalars to native Python types for JSON serialization."""
    if val is None:
        return None
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (int, float, str, bool)):
        return val
    # Fallback: try to convert to float or string
    try:
        return float(val)
    except Exception:
        return str(val)

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: list of dicts representing the original rows,
    # ensuring values are native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate Sloan Ratio for each row dynamically:
    # Accruals = Net Income - Operating Cashflow
    # Sloan Ratio = Accruals / Avg Total Assets
    der_records = []
    for _, row in df.iterrows():
        year = to_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # Extract required raw inputs dynamically
        net_income = row.get("Net Income") if "Net Income" in df.columns else None
        cfo = row.get("Operating Cashflow") if "Operating Cashflow" in df.columns else None
        total_assets = row.get("Avg Total Assets") if "Avg Total Assets" in df.columns else None

        # Convert to native numeric where possible
        try:
            ni = None if pd.isna(net_income) else float(net_income)
        except Exception:
            ni = None
        try:
            c = None if pd.isna(cfo) else float(cfo)
        except Exception:
            c = None
        try:
            ta = None if pd.isna(total_assets) else float(total_assets)
        except Exception:
            ta = None

        # Compute accruals from raw inputs (do not rely on precomputed column)
        accruals = None
        if (ni is not None) and (c is not None):
            accruals = ni - c

        # Compute Sloan Ratio, guard against division by zero / missing data
        sloan = None
        if (accruals is not None) and (ta not in (None, 0)):
            sloan = accruals / ta

        rec = {}
        if year is not None:
            rec["Fiscal Year"] = to_native(year)
        rec[INDICATOR_NAME] = to_native(sloan)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output file (ensure Chinese keys are preserved)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()