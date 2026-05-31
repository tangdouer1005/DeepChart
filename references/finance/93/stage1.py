#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

def to_python_value(v):
    # Convert pandas/numpy scalar types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # Convert to Python float; if it's an integer value, still keep float for clarity
        return float(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Raw CSV data (hardcoded as required)
    csv_data = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,12918000000,14232000000,31418000000,35138000000,27150000000,182345205.47945204
2017,10715000000,18705000000,39094000000,45583000000,29420000000,231991780.8219178
2018,16701000000,21193000000,49746000000,59549000000,37894000000,299438356.1643836
2019,18498000000,27492000000,55730000000,71896000000,45990000000,349660273.9726027
2020,26465000000,31384000000,56571000000,84732000000,57849000000,387131506.8493151
2021,20945000000,40270000000,67984000000,110939000000,61215000000,490200000.0
2022,21879000000,40258000000,81791000000,126203000000,62137000000,569846575.3424658
2023,24048000000,47964000000,89769000000,133332000000,72012000000,611235616.4383562
2024,23466000000,52340000000,91322000000,146306000000,75806000000,651035616.4383562
"""

    # Load CSV into DataFrame
    df = pd.read_csv(io.StringIO(csv_data))

    # Calculation for Defensive Interval Ratio (DIR)
    # Formula:
    # Quick Assets = Cash + Receivables + Trading Financial Assets
    # (Here, use provided "Quick Assets" column as the quick assets measure)
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption

    # Ensure numeric columns are numeric
    numeric_cols = ["Cash & Equiv", "Receivables", "Operating Expenses", "Cost of Revenue", "Quick Assets"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["Daily Cash Consumption"] = (df["Operating Expenses"] + df["Cost of Revenue"]) / 365.0
    # Avoid division by zero; where daily consumption is zero or NaN, set DIR to None (will be serialized as null)
    df["DIR"] = df.apply(
        lambda row: (row["Quick Assets"] / row["Daily Cash Consumption"])
        if pd.notna(row["Quick Assets"]) and pd.notna(row["Daily Cash Consumption"]) and row["Daily Cash Consumption"] != 0
        else np.nan,
        axis=1
    )

    # Prepare scr_data: original CSV rows as list of dicts with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            # We want scr_data to reflect original input columns only (not computed ones)
            # So include only original CSV headers
            # The original CSV headers are the first 6 columns as per the hardcoded CSV:
            # Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
            # We'll include those exact headers.
            pass
        # Build record using original CSV column list explicitly to preserve order and names
        original_cols = ["Fiscal Year", "Cash & Equiv", "Receivables", "Operating Expenses", "Cost of Revenue", "Quick Assets", "Daily Burn"]
        for col in original_cols:
            rec[col] = to_python_value(row.get(col))
        scr_records.append(rec)

    # Prepare der_data: calculated DIR for each row, include Fiscal Year
    der_records = []
    for _, row in df.iterrows():
        der_rec = {
            "Fiscal Year": to_python_value(row["Fiscal Year"]),
            "防御区间比率 (Defensive Interval Ratio, DIR)": to_python_value(row["DIR"])
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file with ensure_ascii=False to keep Chinese characters readable
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()