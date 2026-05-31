#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,19334000000,8339000000,131801000000,121969000000,27673000000,695260273.9726027
2017,20522000000,13164000000,173760000000,111934000000,33686000000,782723287.6712328
2018,31750000000,16677000000,220466000000,139156000000,48427000000,985265753.4246576
2019,36092000000,20816000000,265981000000,165536000000,56908000000,1182238356.1643836
2020,42122000000,24542000000,363165000000,233307000000,66664000000,1634169863.0136986
2021,36220000000,32891000000,444943000000,272344000000,69111000000,1965169863.0136983
2022,53888000000,42360000000,501735000000,288831000000,96248000000,2165934246.5753427
2023,73387000000,52253000000,232427000000,304739000000,125640000000,1471687671.2328768
2024,78779000000,55451000000,243078000000,326288000000,134230000000,1559906849.3150685
"""

INDICATOR_NAME = "防御区间比率 (Defensive Interval Ratio, DIR)"

def py_cast(value):
    """Cast numpy/int/float types to native Python types for JSON serialization."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        # If it's an integer-valued float, keep as float to preserve possible large numbers
        return float(value)
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data: list of dicts reflecting the input CSV rows with native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = py_cast(row[col])
        scr_data.append(rec)

    # Calculate Defensive Interval Ratio (DIR) per reference:
    # Quick Assets = Cash + Receivables + Trading Financial Assets
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption
    der_data = []
    for _, row in df.iterrows():
        # Prefer using provided "Quick Assets" column (raw data). If missing or NaN, fall back to Cash & Receivables.
        if "Quick Assets" in df.columns and not pd.isna(row.get("Quick Assets")):
            quick_assets = float(row["Quick Assets"])
        else:
            # fallback: Cash & Equiv + Receivables (trading financial assets unknown)
            ca = row.get("Cash & Equiv", 0.0)
            rec = row.get("Receivables", 0.0)
            quick_assets = float((0 if pd.isna(ca) else ca) + (0 if pd.isna(rec) else rec))

        op_exp = 0.0 if pd.isna(row.get("Operating Expenses")) else float(row.get("Operating Expenses"))
        cost_rev = 0.0 if pd.isna(row.get("Cost of Revenue")) else float(row.get("Cost of Revenue"))

        daily_consumption = (op_exp + cost_rev) / 365.0

        # Guard against division by zero
        if daily_consumption == 0:
            dir_value = None
        else:
            dir_value = quick_assets / daily_consumption

        der_rec = {
            "Fiscal Year": py_cast(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None,
            INDICATOR_NAME: py_cast(dir_value) if dir_value is not None else None
        }
        der_data.append(der_rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file with UTF-8 encoding (ensure Chinese keys are preserved)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()