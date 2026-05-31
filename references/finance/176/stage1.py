#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,6510000000,4563000000,11988000000,1243000000,1482833333.3333333
2017,7663000000,4481000000,13037000000,2222000000,1645000000.0
2018,11946000000,4754000000,14726000000,2733000000,1851083333.3333333
2019,11356000000,4885000000,16876000000,2686000000,2037250000.0
2020,13576000000,5111000000,19269000000,2591000000,2247583333.333333
2021,14224000000,5107000000,20716000000,2346000000,2347416666.6666665
2022,13931000000,5900000000,24512000000,2063000000,2706250000.0
2023,34704000000,7575000000,27195000000,1968000000,3061500000.0
2024,18315000000,7609000000,29510000000,2935000000,3337833333.333333
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def numpy_safe(val):
    """
    Convert numpy/pandas scalar types to native Python types for JSON serialization.
    """
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # convert NaN/inf to None for safety
        if np.isfinite(val):
            return float(val)
        return None
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw rows as list of dicts with native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = numpy_safe(row[col])
        scr_records.append(rec)

    # Calculate the Cash Burn Runway under Zero Revenue Scenario for each row.
    # Per specification:
    # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
    # Runway (Months) = Cash & Equivalents / Monthly rigid outflow
    der_records = []
    for _, row in df.iterrows():
        cash = row["Cash & Equivalents"]
        sga = row["SG&A"]
        rnd = row["R&D"]
        interest = row["Interest Expense"]

        # Compute monthly rigid outflow (do NOT include COGS)
        monthly_rigid_outflow = (sga + rnd + interest) / 12.0

        # Protect against division by zero
        if monthly_rigid_outflow == 0 or pd.isna(monthly_rigid_outflow):
            runway_months = None
        else:
            runway_months = cash / monthly_rigid_outflow

        rec = {
            "Fiscal Year": numpy_safe(row["Fiscal Year"]),
            INDICATOR_NAME: numpy_safe(runway_months)
        }
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write to output JSON file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()