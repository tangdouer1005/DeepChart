#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,7102000000,11693000000,1879000000,579000000,1179250000.0
2017,5569000000,11536000000,1874000000,465000000,1156250000.0
2018,2569000000,11608000000,1908000000,506000000,1168500000.0
2019,4239000000,11909000000,1900000000,509000000,1193166666.6666667
2020,16181000000,12297000000,1800000000,465000000,1213500000.0
2021,10288000000,12824000000,1900000000,502000000,1268833333.3333333
2022,7214000000,11685000000,2000000000,439000000,1177000000.0
2023,8246000000,13112000000,2000000000,756000000,1322333333.3333333
2024,9482000000,12891000000,2000000000,925000000,1318000000.0
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_python_native(value):
    # Convert pandas / numpy types to native Python types for JSON serialization
    if pd.isna(value):
        return None
    # numpy scalars
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    # pandas Timestamp
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows (convert types to native)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculation for each row:
    # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
    # Runway (Months) = Cash & Equivalents / Monthly rigid outflow
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_python_native(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None

        # Extract raw inputs (ensure numeric)
        cash = row.get("Cash & Equivalents", None)
        sga = row.get("SG&A", 0)
        rd = row.get("R&D", 0)
        interest = row.get("Interest Expense", 0)

        # Convert to floats for calculation (handle missing as zeros where appropriate)
        try:
            cash_val = float(cash) if not pd.isna(cash) else None
        except Exception:
            cash_val = None
        def to_num(x):
            try:
                return 0.0 if pd.isna(x) else float(x)
            except Exception:
                return 0.0

        sga_val = to_num(sga)
        rd_val = to_num(rd)
        interest_val = to_num(interest)

        monthly_rigid_outflow = (sga_val + rd_val + interest_val) / 12.0

        # If monthly outflow is zero or negative or cash is None -> runway cannot be computed => null
        if monthly_rigid_outflow is None or monthly_rigid_outflow <= 0 or cash_val is None:
            runway_months = None
        else:
            runway_months = cash_val / monthly_rigid_outflow

        # Convert to native python numeric types where applicable
        runway_months_native = to_python_native(runway_months) if runway_months is not None else None

        rec = {}
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[INDICATOR_NAME] = runway_months_native
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()