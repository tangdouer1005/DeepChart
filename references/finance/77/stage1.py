#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import math

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,6988000000,4684000000,476000000,201000000,446750000.0
2017,4813000000,4448000000,433000000,307000000,432333333.3333333
2018,9342000000,3838000000,453000000,748000000,419916666.6666667
2019,5686000000,4143000000,500000000,798000000,453416666.6666667
2020,5596000000,4213000000,435000000,697000000,445416666.6666667
2021,5640000000,32268000000,268000000,712000000,2770666666.6666665
2022,17678000000,33353000000,268000000,516000000,2844750000.0
2023,8178000000,4141000000,320000000,469000000,410833333.3333333
2024,6781000000,4834000000,353000000,594000000,481750000.0
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def numpy_safe(o):
    # json default handler to convert numpy/pandas scalars to native python types
    try:
        # pandas / numpy scalars have .item()
        return o.item()
    except Exception:
        # fallback
        if pd.isna(o):
            return None
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: list of dicts representing input rows
    scr_records = df.to_dict(orient="records")

    # Compute derived indicator for each row
    der_records = []
    for idx, row in df.iterrows():
        # Extract required fields
        cash = row.get("Cash & Equivalents", None)
        sgna = row.get("SG&A", 0) or 0
        rnd = row.get("R&D", 0) or 0
        interest = row.get("Interest Expense", 0) or 0

        # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
        monthly_rigid_outflow = None
        runway_months = None
        try:
            monthly_rigid_outflow = (float(sgna) + float(rnd) + float(interest)) / 12.0
        except Exception:
            monthly_rigid_outflow = None

        if monthly_rigid_outflow is None or monthly_rigid_outflow <= 0:
            runway_months = None
        else:
            try:
                runway_months = float(cash) / monthly_rigid_outflow
            except Exception:
                runway_months = None

        # Build output entry. Include Fiscal Year if present.
        entry = {}
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = row["Fiscal Year"]
        entry[INDICATOR_NAME] = runway_months
        der_records.append(entry)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with unicode preserved and numpy-safe handler
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, default=numpy_safe, indent=4)

if __name__ == "__main__":
    main()