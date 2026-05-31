#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

# Embedded CSV data (raw inputs only)
CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,20152000000,5385000000,16964000000,7479000000,25537000000,66967123.28767123
2017,21784000000,5300000000,17427000000,7452000000,27084000000,68161643.83561644
2018,21620000000,5136000000,18077000000,8060000000,26756000000,71608219.1780822
2019,20514000000,5134000000,17976000000,7995000000,25648000000,71153424.65753424
2020,37239000000,5551000000,17234000000,7938000000,42790000000,68964383.56164384
2021,30098000000,5409000000,17411000000,7855000000,35507000000,69221917.80821918
2022,21383000000,5953000000,22637000000,8877000000,27336000000,86339726.02739726
2023,9765000000,6915000000,23297000000,13564000000,16680000000,100989041.09589042
2024,10454000000,7874000000,22465000000,15143000000,18328000000,103035616.43835616
"""

def to_python_native(value):
    # Convert numpy/pandas scalar types to built-in Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV into DataFrame
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure required columns exist
    required_cols = {"Cash & Equiv", "Receivables", "Operating Expenses", "Cost of Revenue", "Quick Assets"}
    if not required_cols.issubset(set(df.columns)):
        raise ValueError(f"Input CSV missing required columns. Required: {required_cols}")

    # Prepare scr_data (raw rows) with Python-native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate Defensive Interval Ratio (DIR) for each row
    der_records = []
    year_col = None
    # Determine a year-like column name if present
    for candidate in ["Fiscal Year", "Year", "FY", "Date"]:
        if candidate in df.columns:
            year_col = candidate
            break

    for _, row in df.iterrows():
        # According to reference:
        # Quick Assets = Cash + Receivables + Trading Financial Assets
        # Here "Quick Assets" is provided in CSV as a raw input, so use it directly.
        quick_assets = row["Quick Assets"]

        # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
        daily_cash_consumption = (row["Operating Expenses"] + row["Cost of Revenue"]) / 365.0

        # Defensive Interval Ratio
        # Protect against division by zero
        if daily_cash_consumption == 0 or pd.isna(daily_cash_consumption):
            dir_value = None
        else:
            dir_value = quick_assets / daily_cash_consumption

        der_entry = {}
        if year_col is not None:
            der_entry[year_col] = to_python_native(row[year_col])
        der_entry["防御区间比率 (Defensive Interval Ratio, DIR)"] = to_python_native(dir_value)
        der_records.append(der_entry)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()