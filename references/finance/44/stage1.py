#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,2350000000,3292000000,-942000000,33090000000.0
2017,2679000000,6726000000,-4047000000,34755000000.0
2018,3134000000,5774000000,-2640000000,38588500000.0
2019,3659000000,6356000000,-2697000000,43115000000.0
2020,4002000000,8861000000,-4859000000,50478000000.0
2021,5007000000,8958000000,-3951000000,57412000000.0
2022,5844000000,7392000000,-1548000000,61717000000.0
2023,6292000000,11068000000,-4776000000,66580000000.0
2024,7367000000,11339000000,-3972000000,69412500000.0
"""

def to_python_scalar(v):
    if pd.isna(v):
        return None
    # Convert numpy types to native python
    if isinstance(v, (pd.Timestamp,)):
        return str(v)
    try:
        if isinstance(v, (int, float, bool, str)):
            return v
        # numpy numeric types
        return v.item()
    except Exception:
        return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as Python-native types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_scalar(row[col])
        scr_data.append(rec)

    # Calculate Sloan Ratio for each row
    der_data = []
    indicator_name = "斯隆比率 (Sloan Ratio / Accruals Ratio)"
    for _, row in df.iterrows():
        # Use raw components to compute accruals: Accruals = Net Income - Operating Cashflow
        net_income = float(row["Net Income"]) if not pd.isna(row["Net Income"]) else None
        operating_cf = float(row["Operating Cashflow"]) if not pd.isna(row["Operating Cashflow"]) else None
        avg_total_assets = float(row["Avg Total Assets"]) if not pd.isna(row["Avg Total Assets"]) else None

        accruals_computed = None
        sloan_ratio = None
        if net_income is not None and operating_cf is not None:
            accruals_computed = net_income - operating_cf
        if accruals_computed is not None and avg_total_assets not in (None, 0):
            sloan_ratio = accruals_computed / avg_total_assets

        rec = {
            "Fiscal Year": to_python_scalar(row["Fiscal Year"]),
            indicator_name: to_python_scalar(sloan_ratio) if sloan_ratio is not None else None
        }
        der_data.append(rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON output
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()