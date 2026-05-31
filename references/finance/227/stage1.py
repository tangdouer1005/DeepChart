#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numbers

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,786000000,4975900000,754800000,469600000,516691666.6666667
2017,1335000000,5492000000,888000000,592000000,581000000.0
2018,2103000000,6057000000,967000000,667000000,640916666.6666666
2019,2399000000,6144000000,1003000000,676000000,651916666.6666666
2020,10325000000,6930000000,1181000000,553000000,722000000.0
2021,4477000000,6842000000,1406000000,536000000,732000000.0
2022,8524000000,7127000000,1471000000,726000000,777000000.0
2023,8083000000,8612000000,1337000000,1375000000,943666666.6666666
2024,4009000000,8595000000,1390000000,1654000000,969916666.6666666
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_py_scalar(v):
    """Convert pandas/numpy scalar to native Python types for JSON serialization."""
    if pd.isna(v):
        return None
    if isinstance(v, numbers.Number):
        # convert to int if it's an integer value
        try:
            fv = float(v)
            if fv.is_integer():
                return int(fv)
            else:
                return fv
        except Exception:
            # fallback
            return float(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows with original headers
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_py_scalar(row[col])
        scr_records.append(rec)

    # Calculate derived indicator for each row
    der_records = []
    for _, row in df.iterrows():
        # Extract required fields
        cash = row["Cash & Equivalents"]
        sga = row["SG&A"]
        rd = row["R&D"]
        interest = row["Interest Expense"]

        # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
        # (explicitly excluding COGS as per definition)
        try:
            monthly_rigid_outflow = (float(sga) + float(rd) + float(interest)) / 12.0
        except Exception:
            monthly_rigid_outflow = None

        # Runway (Months) = Cash & Equivalents / monthly_rigid_outflow
        runway_months = None
        if monthly_rigid_outflow is None or monthly_rigid_outflow == 0:
            runway_months = None
        else:
            runway_months = float(cash) / monthly_rigid_outflow

        # Build record, include Fiscal Year if present
        der_rec = {}
        if "Fiscal Year" in df.columns:
            der_rec["Fiscal Year"] = to_py_scalar(row["Fiscal Year"])
        der_rec[INDICATOR_NAME] = to_py_scalar(runway_months)
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()