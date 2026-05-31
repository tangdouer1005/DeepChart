#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2017,6867000000,5835000000,101853000000,361256000000,12702000000,1268791780.8219178
2018,6756000000,5614000000,106510000000,373396000000,12370000000,1314810958.9041097
2019,7722000000,6283000000,107147000000,385301000000,14005000000,1349172602.739726
2020,9465000000,6284000000,108791000000,394605000000,15749000000,1379167123.287671
2021,17741000000,6516000000,116288000000,420315000000,24257000000,1470145205.479452
2022,14760000000,8280000000,117812000000,429000000000,23040000000,1498115068.4931507
2023,8885000000,7933000000,127140000000,463721000000,16818000000,1618797260.2739725
2024,9867000000,8796000000,130971000000,490142000000,18663000000,1701679452.0547943
"""

INDICATOR_NAME = "防御区间比率 (Defensive Interval Ratio, DIR)"

def to_python_native(obj):
    # Convert numpy / pandas scalar types to native python types for JSON serialization
    if obj is None:
        return None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_ , bool)):
        return bool(obj)
    if pd.isna(obj):
        return None
    # Pandas Timestamp
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj

def row_to_native_dict(row_dict):
    return {k: to_python_native(v) for k, v in row_dict.items()}

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["Cash & Equiv", "Receivables", "Operating Expenses", "Cost of Revenue", "Quick Assets", "Daily Burn"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate Defensive Interval Ratio (DIR) for each row using the reference formula:
    # Quick Assets = given "Quick Assets" column (assumed to represent cash + receivables + trading financial assets)
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption
    dir_values = []
    for _, row in df.iterrows():
        quick_assets = row.get("Quick Assets", None)
        op_exp = row.get("Operating Expenses", None)
        cost_rev = row.get("Cost of Revenue", None)

        # Compute daily cash consumption safely
        if pd.isna(op_exp) or pd.isna(cost_rev) or pd.isna(quick_assets):
            dir_val = None
        else:
            daily_cash_consumption = (float(op_exp) + float(cost_rev)) / 365.0
            # Avoid division by zero
            if daily_cash_consumption == 0:
                dir_val = None
            else:
                dir_val = float(quick_assets) / daily_cash_consumption

        dir_values.append(dir_val)

    # Prepare scr_data (original input rows) as list of dicts with native python types
    scr_records = df.to_dict(orient="records")
    scr_data = [row_to_native_dict(rec) for rec in scr_records]

    # Prepare der_data: one dict per row with Fiscal Year (if present) and the calculated DIR
    der_data = []
    for rec, dir_val in zip(scr_records, dir_values):
        entry = {}
        # Include the year if present in the CSV
        if "Fiscal Year" in rec:
            entry["Fiscal Year"] = to_python_native(rec["Fiscal Year"])
        entry[INDICATOR_NAME] = to_python_native(dir_val)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()