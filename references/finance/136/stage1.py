#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,4582100000,6330400000,5310300000,185200000,985491666.6666666
2017,6536200000,6180100000,5096200000,225000000,958441666.6666666
2018,7320700000,5734600000,5051200000,242500000,919025000.0
2019,2337500000,6003900000,5595000000,400600000,999958333.3333334
2020,3657100000,5869400000,5976300000,359600000,1017108333.3333334
2021,3818500000,6141900000,6930700000,339800000,1117700000.0
2022,2067000000,6067500000,7190800000,331600000,1132491666.6666667
2023,2818600000,6941200000,9313400000,485900000,1395041666.6666667
2024,3268400000,8132100000,10990600000,780600000,1658608333.3333333
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_python_native(val):
    # Convert pandas / numpy types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    # For Python scalars (int/float/str/bool) return as-is
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as dictionaries with native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate the Cash Burn Runway (Zero Revenue Scenario) for each row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_python_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        cash = row.get("Cash & Equivalents", np.nan)
        sg_and_a = row.get("SG&A", 0.0)
        r_and_d = row.get("R&D", 0.0)
        interest = row.get("Interest Expense", 0.0)

        # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
        monthly_rigid_outflow = (sg_and_a + r_and_d + interest) / 12.0

        # If monthly outflow is zero or negative, runway is undefined/infinite -> set to None
        if pd.isna(cash) or monthly_rigid_outflow <= 0:
            runway_months = None
        else:
            runway_months = float(cash / monthly_rigid_outflow)

        rec = {}
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[INDICATOR_NAME] = to_python_native(runway_months)
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output file (ensure Chinese characters preserved)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()