#!/usr/bin/env python3
import sys
import io
import json
import math
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,3393216000.0,1384189000.0,834408000,198810000,201450583.3333333
2017,3367914000.0,2439500000.0,1378000000,471000000,357375000.0
2018,3686000000.0,2835000000.0,1460370000,663000000,413197500.0
2019,6268000000.0,2646000000.0,1343000000,685000000,389500000.0
2020,19384000000.0,3145000000.0,1491000000,748000000,448666666.6666667
2021,17576000000.0,4517000000.0,2593000000,371000000,623416666.6666666
2022,16253000000.0,3946000000.0,3075000000,191000000,601000000.0
2023,16398000000.0,4800000000.0,3969000000,156000000,743750000.0
2024,16139000000.0,5150000000.0,4540000000,350000000,836666666.6666666
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_native_python(val):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # Convert NaN/inf if any
        if math.isfinite(float(val)):
            return float(val)
        return None
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure necessary raw columns exist
    required_cols = ["Fiscal Year", "Cash & Equivalents", "SG&A", "R&D", "Interest Expense"]
    for c in required_cols:
        if c not in df.columns:
            raise KeyError(f"Missing required column in CSV data: {c}")

    # Build scr_data from the original CSV rows (convert types to native Python)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native_python(row[col])
        scr_records.append(rec)

    # Calculate the indicator for each row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_native_python(row["Fiscal Year"])
        cash = float(row["Cash & Equivalents"]) if not pd.isna(row["Cash & Equivalents"]) else None
        sg_a = float(row["SG&A"]) if not pd.isna(row["SG&A"]) else 0.0
        r_and_d = float(row["R&D"]) if not pd.isna(row["R&D"]) else 0.0
        interest = float(row["Interest Expense"]) if not pd.isna(row["Interest Expense"]) else 0.0

        # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
        monthly_rigid_outflow = (sg_a + r_and_d + interest) / 12.0

        # Runway (Months) = Cash & Equivalents / monthly_rigid_outflow
        if cash is None or monthly_rigid_outflow == 0:
            runway_months = None
        else:
            runway_months = cash / monthly_rigid_outflow

        # Convert to native python numeric if finite
        if runway_months is None or not math.isfinite(runway_months):
            runway_val = None
        else:
            runway_val = float(runway_months)

        der_rec = {
            "Fiscal Year": fiscal_year,
            INDICATOR_NAME: runway_val
        }
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()