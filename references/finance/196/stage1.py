#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,596000000,602000000,1331000000,47000000,165000000.0
2017,1766000000,663000000,1463000000,58000000,182000000.0
2018,4002000000,815000000,1797000000,61000000,222750000.0
2019,782000000,991000000,2376000000,58000000,285416666.6666667
2020,10896000000,1093000000,2829000000,52000000,331166666.6666667
2021,847000000,1940000000,3924000000,184000000,504000000.0
2022,1990000000,2166000000,5268000000,236000000,639166666.6666666
2023,3389000000,2440000000,7339000000,262000000,836750000.0
2024,7280000000,2654000000,8675000000,257000000,965500000.0
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def convert_value(v):
    # Convert pandas/numpy types to native Python types for JSON serialization
    if pd.isna(v):
        return None
    try:
        f = float(v)
        if f.is_integer():
            return int(f)
        return f
    except Exception:
        return str(v)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: a list of dicts mirroring input CSV, with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = convert_value(row[col])
        scr_records.append(rec)

    # Calculate the Cash Burn Runway (Zero Revenue Scenario) for each row
    der_records = []
    for _, row in df.iterrows():
        # Extract required raw inputs (these are hardcoded in the CSV above)
        cash = row["Cash & Equivalents"]
        sgna = row["SG&A"]
        rd = row["R&D"]
        interest = row["Interest Expense"]

        # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
        monthly_rigid_outflow = (sgna + rd + interest) / 12.0

        # If monthly outflow is zero or negative, runway is undefined (set to None)
        if monthly_rigid_outflow <= 0:
            runway_months = None
        else:
            runway_months = cash / monthly_rigid_outflow

        # Build derived record; include Fiscal Year if present
        der_rec = {}
        if "Fiscal Year" in df.columns:
            der_rec["Fiscal Year"] = convert_value(row["Fiscal Year"])
        # Indicator value must be computed, not hardcoded
        der_rec[INDICATOR_NAME] = convert_value(runway_months)
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write to output file as JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()