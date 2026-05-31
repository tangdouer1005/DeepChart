#!/usr/bin/env python3
import sys
import io
import json
import math
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,92400000000,18377000000,4782000000,5024000000,2348583333.333333
2017,43967000000,26425000000,4738000000,4655000000,2984833333.333333
2018,68900000000,17433000000,3415000000,4766000000,2134500000.0
2019,84900000000,17100000000,3118000000,2927000000,1928750000.0
2020,36530000000,14989000000,2565000000,3515000000,1755750000.0
2021,15770000000,10351000000,1682000000,1790000000,1151916666.6666667
2022,15810000000,12781000000,2813000000,1477000000,1422583333.3333333
2023,15204000000,6681000000,1011000000,1029000000,726750000.0
2024,13619000000,6347000000,1286000000,986000000,718250000.0
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_py_scalar(v):
    # Convert pandas / numpy scalars to native Python types for JSON serialization
    if pd.isna(v):
        return None
    # pandas.Timestamp etc. handled by pandas.isna above
    try:
        # numpy scalars have .item()
        if hasattr(v, "item"):
            return v.item()
    except Exception:
        pass
    return v

def compute_runway_months(cash, sg_a, rd, interest):
    """
    Based on:
    月度刚性流出 = (SG&A + R&D + Interest Expense) / 12
    Runway (Months) = Cash & Equivalents / 月度刚性流出

    If monthly outflow is zero or negative, return None.
    """
    monthly_outflow = (sg_a + rd + interest) / 12.0
    if monthly_outflow is None:
        return None
    # Guard against zero or negative outflow which would produce infinite or meaningless runway
    if monthly_outflow <= 0:
        return None
    return cash / monthly_outflow

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA), dtype=object)

    # Convert numeric-like strings to numbers where appropriate
    # We'll attempt to coerce columns (except Fiscal Year) to floats
    for col in df.columns:
        if col == "Fiscal Year":
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Prepare scr_data: raw input rows as dictionaries with original headers
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_scalar(row[col])
        scr_records.append(rec)

    # Prepare der_data: computed indicator per row
    der_records = []
    for _, row in df.iterrows():
        fiscal_year = to_py_scalar(row["Fiscal Year"]) if "Fiscal Year" in df.columns else None
        cash = to_py_scalar(row.get("Cash & Equivalents"))
        sg_a = to_py_scalar(row.get("SG&A"))
        rd = to_py_scalar(row.get("R&D"))
        interest = to_py_scalar(row.get("Interest Expense"))

        # If any required input is None, result is None
        if cash is None or sg_a is None or rd is None or interest is None:
            runway_months = None
        else:
            runway_months = compute_runway_months(float(cash), float(sg_a), float(rd), float(interest))

        rec = {}
        if fiscal_year is not None:
            rec["Fiscal Year"] = fiscal_year
        rec[INDICATOR_NAME] = to_py_scalar(runway_months)
        der_records.append(rec)

    out_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()