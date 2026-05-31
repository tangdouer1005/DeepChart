#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,7631000000,1814000000,6296000000,676000000,732166666.6666666
2017,11708000000,1993000000,6059000000,861000000,742750000.0
2018,8934000000,2144000000,6332000000,943000000,784916666.6666666
2019,11750000000,1827000000,6577000000,859000000,771916666.6666666
2020,11809000000,1925000000,6347000000,585000000,738083333.3333334
2021,9175000000,2152000000,6549000000,434000000,761250000.0
2022,7079000000,2101000000,6774000000,360000000,769583333.3333334
2023,10123000000,2478000000,7551000000,427000000,871333333.3333334
2024,9023000000,2813000000,7983000000,1006000000,983500000.0
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_python_native(val):
    # Convert numpy types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # If it's a whole number, keep as int to match typical expectations
        if float(val).is_integer():
            return int(round(float(val)))
        return float(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculate the indicator for each row:
    # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
    # Runway (Months) = Cash & Equivalents / Monthly rigid outflow
    # Note: Per specification, do NOT include COGS.
    runway_values = []
    for _, row in df.iterrows():
        cash = row.get("Cash & Equivalents", np.nan)
        sga = row.get("SG&A", 0.0)
        rnd = row.get("R&D", 0.0)
        interest = row.get("Interest Expense", 0.0)

        # Compute monthly rigid outflow
        monthly_rigid_outflow = (sga + rnd + interest) / 12.0

        # Avoid division by zero; if outflow is zero or not positive, set None
        if monthly_rigid_outflow is None or monthly_rigid_outflow == 0 or pd.isna(monthly_rigid_outflow) or monthly_rigid_outflow <= 0:
            runway_months = None
        else:
            runway_months = cash / monthly_rigid_outflow

        runway_values.append(runway_months)

    # Prepare scr_data: original CSV rows as list of dicts, converting types for JSON
    scr_records = []
    for rec in df.to_dict(orient="records"):
        converted = {k: to_python_native(v) for k, v in rec.items()}
        scr_records.append(converted)

    # Prepare der_data: list of dicts with Fiscal Year (if present) and the calculated indicator
    der_records = []
    for idx, val in enumerate(runway_values):
        record = {}
        # Include Year if present in original data
        if "Fiscal Year" in df.columns:
            record["Fiscal Year"] = to_python_native(df.at[idx, "Fiscal Year"])
        # Include the calculated indicator value (do not hardcode values)
        record[INDICATOR_NAME] = to_python_native(val)
        der_records.append(record)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output file (ensure Chinese characters are preserved)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()