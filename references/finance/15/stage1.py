#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equivalents,SG&A,R&D,Interest Expense,Monthly Burn
2016,18620000000,6672000000,1358000000,304000000,694500000.0
2017,9407000000,9117000000,2130000000,880000000,1010583333.3333334
2018,3844000000,9744000000,2288000000,729000000,1063416666.6666666
2019,3860000000,9765000000,2408000000,818000000,1082583333.3333333
2020,6838000000,9696000000,2418000000,708000000,1068500000.0
2021,9799000000,11324000000,2738000000,410000000,1206000000.0
2022,9882000000,11012000000,2852000000,315000000,1181583333.3333333
2023,6896000000,11198000000,2719000000,698000000,1217916666.6666667
2024,7616000000,11697000000,2823000000,603000000,1260250000.0
"""

INDICATOR_NAME = "现金消耗跑道 (Cash Burn Runway) - 零收入情景 (Zero Revenue Scenario)"

def to_builtin_types(record):
    """Convert numpy/pandas types to native Python types for JSON serialization."""
    new = {}
    for k, v in record.items():
        if isinstance(v, (np.integer,)):
            new[k] = int(v)
        elif isinstance(v, (np.floating,)):
            # convert NaN to None, otherwise float
            if np.isnan(v):
                new[k] = None
            else:
                new[k] = float(v)
        elif pd.isna(v):
            new[k] = None
        else:
            new[k] = v
    return new

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as list of dicts with native Python types
    scr_records = df.to_dict(orient="records")
    scr_data = [to_builtin_types(r) for r in scr_records]

    # Calculate the indicator for each row
    der_data = []
    for idx, row in df.iterrows():
        # Extract raw inputs (these are the only hardcoded/raw values used in calc)
        cash = row["Cash & Equivalents"]
        sgna = row["SG&A"]
        rnd = row["R&D"]
        interest = row["Interest Expense"]

        # Monthly rigid outflow = (SG&A + R&D + Interest Expense) / 12
        monthly_rigid_outflow = (sgna + rnd + interest) / 12.0

        # If monthly_rigid_outflow is zero or not a number, runway is None
        if monthly_rigid_outflow == 0 or pd.isna(monthly_rigid_outflow):
            runway_months = None
        else:
            runway_months = cash / monthly_rigid_outflow

        # Build output record; include Fiscal Year if available in input
        record = {}
        if "Fiscal Year" in df.columns:
            # ensure it's native Python type
            fy = row["Fiscal Year"]
            record["Fiscal Year"] = int(fy) if not pd.isna(fy) else None
        record[INDICATOR_NAME] = (None if runway_months is None else float(runway_months))
        der_data.append(record)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file with Chinese characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()