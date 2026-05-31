import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,4582100000,4766300000,11640700000,5710100000,9348400000,47536438.35616438
2017,6536200000,5262200000,11276300000,4447700000,11798400000,43079452.05479452
2018,7320700000,5776800000,10785800000,4681700000,13097500000,42376712.32876712
2019,2337500000,5541500000,11598900000,4721200000,7879000000,44712602.73972603
2020,3657100000,6929000000,11845700000,5483300000,10586100000,47476712.32876712
2021,3818500000,8127200000,13072600000,7312800000,11945700000,55850410.95890411
2022,2067000000,8558900000,13258300000,6629800000,10625900000,54487945.20547945
2023,2818600000,11336200000,16254600000,7082200000,14154800000,63936438.35616438
2024,3268400000,13275400000,19122700000,8418300000,16543800000,75454794.52054794
"""

def to_python_scalar(val):
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # If it's an integer value in float form, convert to int to keep JSON tidy
        if float(val).is_integer():
            return int(val)
        return float(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as dictionaries with native python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_scalar(row[col])
        scr_records.append(rec)

    # Calculate Defensive Interval Ratio (DIR) per reference:
    # Quick Assets = Cash + Receivables + Trading Financial Assets (we use provided 'Quick Assets' column)
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_python_scalar(row['Fiscal Year'])
        quick_assets = row.get('Quick Assets', None)
        # Fallback: if Quick Assets not present or null, compute from Cash & Equiv + Receivables (assumes no trading financial assets available)
        if pd.isna(quick_assets):
            cash = row.get('Cash & Equiv', 0) if not pd.isna(row.get('Cash & Equiv', np.nan)) else 0
            receivables = row.get('Receivables', 0) if not pd.isna(row.get('Receivables', np.nan)) else 0
            quick_assets = cash + receivables

        operating_expenses = row.get('Operating Expenses', 0)
        cost_of_revenue = row.get('Cost of Revenue', 0)

        # Ensure numeric and avoid division by zero
        try:
            daily_cash_consumption = float(operating_expenses + cost_of_revenue) / 365.0
        except Exception:
            daily_cash_consumption = None

        if daily_cash_consumption in (0, None) or pd.isna(daily_cash_consumption):
            dir_value = None
        else:
            dir_value = float(quick_assets) / daily_cash_consumption

        der_rec = {
            "Fiscal Year": fiscal_year,
            "防御区间比率 (Defensive Interval Ratio, DIR)": to_python_scalar(dir_value)
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file with UTF-8 and preserve non-ASCII (Chinese) characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()