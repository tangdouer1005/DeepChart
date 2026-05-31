#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,5619000000,2740000000,4435000000,2764000000,8359000000,19723287.671232875
2017,9874000000,2554000000,2966000000,3248000000,12428000000,17024657.534246575
2018,8162000000,2790000000,3799000000,3856000000,10952000000,20972602.739726026
2019,7838000000,4590000000,3811000000,4165000000,12428000000,21852054.79452055
2020,16289000000,2882000000,3253000000,4512000000,19171000000,21273972.602739725
2021,16487000000,3726000000,3331000000,4970000000,20213000000,22742465.75342466
2022,15689000000,3952000000,4764000000,5733000000,19641000000,28758904.10958904
2023,16286000000,4474000000,5086000000,6567000000,20760000000,31926027.397260275
2024,11975000000,7015000000,5289000000,7042000000,18990000000,33783561.64383562
"""

def to_python_native(val):
    """
    Convert pandas/numpy scalar types to native Python types for JSON serialization.
    """
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # convert NaN handled above
        return float(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(2)
    out_path = sys.argv[1]

    # Load CSV from embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows as list of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate Defensive Interval Ratio (DIR) for each row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_python_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # According to reference:
        # Quick Assets = cash + receivables + trading financial assets
        # But the CSV already provides "Quick Assets" as a raw input column.
        quick_assets = to_python_native(row.get("Quick Assets", np.nan))

        # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
        op_exp = to_python_native(row.get("Operating Expenses", 0))
        cost_rev = to_python_native(row.get("Cost of Revenue", 0))

        # Ensure numeric types for calculation
        try:
            op_exp_f = float(op_exp) if op_exp is not None else 0.0
        except Exception:
            op_exp_f = 0.0
        try:
            cost_rev_f = float(cost_rev) if cost_rev is not None else 0.0
        except Exception:
            cost_rev_f = 0.0

        daily_cash_consumption = (op_exp_f + cost_rev_f) / 365.0

        # Compute DIR; guard divide-by-zero
        try:
            qa_f = float(quick_assets) if quick_assets is not None else 0.0
            if daily_cash_consumption == 0:
                dir_value = None
            else:
                dir_value = qa_f / daily_cash_consumption
        except Exception:
            dir_value = None

        # Round DIR for readability; keep None if cannot compute
        dir_out = round(dir_value, 6) if dir_value is not None else None

        der_rec = {
            "Fiscal Year": fiscal_year,
            "防御区间比率 (Defensive Interval Ratio, DIR)": dir_out
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()