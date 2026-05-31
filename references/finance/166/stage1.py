#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,6515000000,255000000,10261000000,693000000,934083333.3333334
2017,6092000000,244000000,10339000000,754000000,944750000.0
2018,7965000000,8002000000,9752000000,772000000,1543833333.3333333
2019,9676000000,8715000000,9724000000,893000000,1611000000.0
2020,8050000000,6769000000,13397000000,831000000,1749750000.0
2021,8096000000,7403000000,12245000000,806000000,1704500000.0
2022,12694000000,7469000000,13548000000,962000000,1831583333.3333333
2023,6841000000,7584000000,30531000000,1146000000,3271750000.0
2024,13242000000,7700000000,17938000000,1271000000,2242416666.6666665
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_native(value):
    # Convert numpy/pandas scalars to native Python types for JSON serialization
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric
    numeric_cols = ["Cash & Equivalents", "SG&A", "R&D", "Interest Expense"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    der_data = []
    for _, row in df.iterrows():
        cash = row["Cash & Equivalents"]
        sgna = row["SG&A"]
        rd = row["R&D"]
        interest = row["Interest Expense"]

        # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
        monthly_rigid_outflow = None
        runway_months = None
        try:
            monthly_rigid_outflow = (float(sgna) + float(rd) + float(interest)) / 12.0
            if monthly_rigid_outflow > 0:
                runway_months = float(cash) / monthly_rigid_outflow
            else:
                runway_months = None
        except Exception:
            monthly_rigid_outflow = None
            runway_months = None

        entry = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(runway_months)
        }
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()