#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,6527000000,8796000000,-2269000000,88633000000.0
2017,1248000000,7106000000,-5858000000,87583000000.0
2018,6434000000,7627000000,-1193000000,85556000000.0
2019,8920000000,10471000000,-1551000000,84798500000.0
2020,7747000000,9844000000,-2097000000,86838500000.0
2021,9771000000,12625000000,-2854000000,90825000000.0
2022,9542000000,11018000000,-1476000000,93558500000.0
2023,10714000000,11599000000,-885000000,95233000000.0
2024,10631000000,6805000000,3826000000,99126000000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def to_python_types(value):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        # Convert NaN to None
        if np.isnan(value):
            return None
        return float(value)
    if pd.isna(value):
        return None
    return value

def safe_div(numer, denom):
    try:
        if denom is None:
            return None
        if denom == 0:
            return None
        return numer / denom
    except Exception:
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data by converting values to native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_types(row[col])
        scr_records.append(rec)

    # Calculate Sloan Ratio dynamically:
    # Accruals = Net Income - Operating Cashflow
    # Sloan Ratio = Accruals / Avg Total Assets  (use Avg Total Assets if provided)
    der_records = []
    for _, row in df.iterrows():
        net_income = to_python_types(row["Net Income"])
        op_cfo = to_python_types(row["Operating Cashflow"])
        # Compute accruals from raw inputs to ensure dynamic calculation
        if (net_income is None) or (op_cfo is None):
            accruals_calc = None
        else:
            accruals_calc = net_income - op_cfo

        avg_total_assets = to_python_types(row.get("Avg Total Assets", None))

        sloan = None
        if accruals_calc is not None and avg_total_assets not in (None, 0):
            # Ensure float division
            try:
                sloan = float(accruals_calc) / float(avg_total_assets)
            except Exception:
                sloan = None

        der_rec = {
            "Fiscal Year": to_python_types(row["Fiscal Year"]),
            INDICATOR_NAME: to_python_types(sloan)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()