#!/usr/bin/env python3
import sys
import io
import json
import math
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,3393216000.0,499142000.0,2266597000,5400875000,3892358000.0,21006772.602739725
2017,3367914000.0,515381000.0,3855000000,9536000000,3883295000.0,36687671.23287671
2018,3686000000.0,949000000.0,4430000000,17419247000,4635000000.0,59860950.68493151
2019,6268000000.0,1324000000.0,4000000000,20509000000,7592000000.0,67147945.20547946
2020,19384000000.0,1886000000.0,4636000000,24906000000,21270000000.0,80936986.30136986
2021,17576000000.0,1913000000.0,7110000000,40217000000,19489000000.0,129663013.69863014
2022,16253000000.0,2952000000.0,7021000000,60609000000,19205000000.0,185287671.23287672
2023,16398000000.0,3508000000.0,8769000000,79113000000,19906000000.0,240772602.73972604
2024,16139000000.0,4418000000.0,10374000000,80240000000,20557000000.0,248257534.24657536
"""

INDICATOR_NAME = "防御区间比率 (Defensive Interval Ratio, DIR)"

def py_native(v):
    # Convert numpy/pandas scalar types to Python natives for JSON serialization
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    # numpy scalar has .item()
    if hasattr(v, "item"):
        try:
            return v.item()
        except Exception:
            pass
    # fallback
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: original raw rows (converted to Python native types)
    scr_data = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            row_dict[col] = py_native(row[col])
        scr_data.append(row_dict)

    # Calculate DIR for each row based on reference:
    # Quick Assets = use provided "Quick Assets" column (raw data)
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption
    der_data = []
    for _, row in df.iterrows():
        fy = py_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # Retrieve raw inputs
        quick_assets = row.get("Quick Assets", None)
        op_exp = row.get("Operating Expenses", None)
        cost_rev = row.get("Cost of Revenue", None)

        # Convert to floats if possible
        try:
            qa_val = float(quick_assets) if quick_assets is not None and not pd.isna(quick_assets) else None
        except Exception:
            qa_val = None
        try:
            op_val = float(op_exp) if op_exp is not None and not pd.isna(op_exp) else None
        except Exception:
            op_val = None
        try:
            cr_val = float(cost_rev) if cost_rev is not None and not pd.isna(cost_rev) else None
        except Exception:
            cr_val = None

        # Compute daily cash consumption safely
        dir_value = None
        if op_val is not None and cr_val is not None:
            daily_cash_consumption = (op_val + cr_val) / 365.0
            if daily_cash_consumption == 0:
                dir_value = None
            else:
                if qa_val is None:
                    # If Quick Assets not present, try to approximate from Cash & Equiv + Receivables
                    cash = row.get("Cash & Equiv", None)
                    rec = row.get("Receivables", None)
                    try:
                        cash_val = float(cash) if cash is not None and not pd.isna(cash) else 0.0
                    except Exception:
                        cash_val = 0.0
                    try:
                        rec_val = float(rec) if rec is not None and not pd.isna(rec) else 0.0
                    except Exception:
                        rec_val = 0.0
                    qa_val = cash_val + rec_val  # conservative approximation
                # Final DIR computation
                try:
                    dir_value = qa_val / daily_cash_consumption
                except Exception:
                    dir_value = None

        # convert dir_value to native type (float or None)
        dir_value_native = py_native(dir_value) if dir_value is not None else None

        entry = {}
        if fy is not None:
            entry["Fiscal Year"] = fy
        entry[INDICATOR_NAME] = dir_value_native
        der_data.append(entry)

    output_obj = {"scr_data": scr_data, "der_data": der_data}

    # Write JSON with ensure_ascii=False to keep Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()