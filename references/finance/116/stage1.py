#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,18972000000,20067000000,9143000000,726000000,2494666666.6666665
2017,17824000000,21520000000,10594000000,934000000,2754000000.0
2018,18107000000,22540000000,10775000000,1005000000,2860000000.0
2019,17305000000,22178000000,11355000000,318000000,2820916666.6666665
2020,13985000000,22084000000,12340000000,201000000,2885416666.6666665
2021,14487000000,20118000000,14277000000,183000000,2881500000.0
2022,12889000000,20246000000,14135000000,276000000,2888083333.333333
2023,21859000000,21012000000,15048000000,1247000000,3108916666.6666665
2024,24105000000,21969000000,17232000000,755000000,3329666666.6666665
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_py_value(v):
    """Convert pandas/numpy scalar or Python value to native Python types for JSON serialization."""
    if pd.isna(v):
        return None
    # If it's a float that's actually an integer value, convert to int to keep JSON cleaner
    try:
        if isinstance(v, (float,)) and v.is_integer():
            return int(v)
    except Exception:
        pass
    # Attempt int conversion for numpy integer types
    try:
        if hasattr(v, "item"):
            py = v.item()
            # After item(), ensure NaN handled
            if py is None:
                return None
            return py
    except Exception:
        pass
    return v

def calculate_runway_months(cash, sga, rd, interest):
    """
    Calculate runway months under zero-revenue scenario.
    Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
    Runway (months) = Cash & Equivalents / Monthly rigid outflow
    If monthly outflow is zero or negative, return None.
    """
    monthly_rigid_outflow = (sga + rd + interest) / 12.0
    if monthly_rigid_outflow <= 0:
        return None
    return cash / monthly_rigid_outflow

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw rows from CSV (convert types to native Python)
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_value(row[col])
        scr_records.append(rec)

    # Prepare der_data: calculated indicator for each row
    der_records = []
    for _, row in df.iterrows():
        # Read raw inputs needed for calculation
        cash = float(row["Cash & Equivalents"]) if not pd.isna(row["Cash & Equivalents"]) else None
        sga = float(row["SG&A"]) if not pd.isna(row["SG&A"]) else 0.0
        rd = float(row["R&D"]) if not pd.isna(row["R&D"]) else 0.0
        interest = float(row["Interest Expense"]) if not pd.isna(row["Interest Expense"]) else 0.0

        runway_months = None
        if cash is not None:
            runway_months = calculate_runway_months(cash, sga, rd, interest)

        rec = {
            "Fiscal Year": to_py_value(row["Fiscal Year"]),
            INDICATOR_NAME: to_py_value(runway_months)
        }
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with UTF-8 and preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()