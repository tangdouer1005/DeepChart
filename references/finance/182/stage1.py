#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,1467576000,3726307000.0,2420975000,6029901000,5193883000.0,23153084.93150685
2017,2822795000,4310934000.0,3194368000,7659666000,7133729000.0,29737079.452054795
2018,3794483000,5513898000.0,4221577000,9967538000,9308381000.0,38874287.67123288
2019,5018437000,979068000.0,5111980000,12440213000,5997505000.0,48088200.0
2020,8205550000,610819000.0,5134448000,15276319000,8816369000.0,55919909.5890411
2021,6027804000,804320000.0,6170652000,17332683000,6832124000.0,64392698.63013699
2022,5147176000,1586898000.0,6814434000,19168285000,6734074000.0,71185531.50684932
2023,7116913000,1842054000.0,7053926000,19715368000,8958967000.0,73340531.50684932
2024,7804733000,1988304000.0,7544888000,21038464000,9793037000.0,78310553.42465754
"""

def to_py(val):
    """Convert numpy types to native Python types for JSON serialization."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure expected columns exist
    # Column names from CSV: Fiscal Year, Cash & Equiv, Receivables, Operating Expenses, Cost of Revenue, Quick Assets, Daily Burn
    # Calculation for DIR:
    # Quick Assets = Cash & Equiv + Receivables + Trading Financial Assets (if Quick Assets column exists, prefer it)
    # Daily Cash Consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily Cash Consumption

    # Prepare scr_data: original rows
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py(row[col])
        scr_records.append(rec)

    # Compute DIR for each row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_py(row.get("Fiscal Year"))
        # Determine quick assets: prefer provided "Quick Assets" column when available and not null
        quick_assets = None
        if "Quick Assets" in row and not pd.isna(row["Quick Assets"]):
            quick_assets = float(row["Quick Assets"])
        else:
            # Fallback: sum Cash & Equiv and Receivables (assume trading financial assets = 0)
            cash = row.get("Cash & Equiv", 0.0)
            receivables = row.get("Receivables", 0.0)
            # handle NaN
            cash = 0.0 if pd.isna(cash) else float(cash)
            receivables = 0.0 if pd.isna(receivables) else float(receivables)
            quick_assets = cash + receivables

        # Daily cash consumption
        op_exp = row.get("Operating Expenses", 0.0)
        cost_rev = row.get("Cost of Revenue", 0.0)
        op_exp = 0.0 if pd.isna(op_exp) else float(op_exp)
        cost_rev = 0.0 if pd.isna(cost_rev) else float(cost_rev)
        daily_cash_consumption = (op_exp + cost_rev) / 365.0

        # Avoid division by zero
        if daily_cash_consumption == 0:
            dir_value = None
        else:
            dir_value = quick_assets / daily_cash_consumption

        der_rec = {
            "Fiscal Year": fiscal_year,
            "防御区间比率 (Defensive Interval Ratio, DIR)": to_py(dir_value)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()