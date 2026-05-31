#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,3379000000,1252000000,12146000000,102901000000,4631000000,315197260.27397263
2017,4546000000,1432000000,13032000000,111882000000,5978000000,342230136.98630136
2018,6055000000,1669000000,13944000000,123152000000,7724000000,375605479.4520548
2019,8384000000,1535000000,15080000000,132886000000,9919000000,405386301.36986303
2020,12277000000,1550000000,16387000000,144939000000,13827000000,441989041.0958904
2021,11258000000,1803000000,18537000000,170684000000,13061000000,518413698.63013697
2022,10203000000,2241000000,19779000000,199382000000,12444000000,600441095.8904109
2023,13700000000,2285000000,21590000000,212586000000,15985000000,641578082.1917808
2024,9906000000,2721000000,22810000000,222358000000,12627000000,671693150.6849315
"""

INDICATOR_NAME = "防御区间比率 (Defensive Interval Ratio, DIR)"

def to_json_serializable(obj):
    # Convert numpy/pandas scalar types to native Python types if needed
    # Works for numpy scalars (have .item()), pandas types, and leaves others unchanged
    try:
        if hasattr(obj, "item"):
            return obj.item()
    except Exception:
        pass
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(2)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculate DIR for each row:
    # Quick Assets = from CSV column "Quick Assets"
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption
    der_rows = []
    for _, row in df.iterrows():
        # Extract raw values required for calculation
        quick_assets = row["Quick Assets"]
        operating_expenses = row["Operating Expenses"]
        cost_of_revenue = row["Cost of Revenue"]

        # Compute daily cash consumption
        daily_cash_consumption = (operating_expenses + cost_of_revenue) / 365.0

        # Guard against division by zero
        if daily_cash_consumption == 0:
            dir_value = None
        else:
            dir_value = quick_assets / daily_cash_consumption

        # Build result entry; include Fiscal Year if present
        entry = {
            "Fiscal Year": to_json_serializable(row["Fiscal Year"]),
            INDICATOR_NAME: to_json_serializable(dir_value)
        }
        der_rows.append(entry)

    # Prepare scr_data: original CSV rows as array of dicts
    scr_records = df.to_dict(orient="records")
    # Convert any non-JSON-native types
    scr_rows = []
    for rec in scr_records:
        newrec = {}
        for k, v in rec.items():
            newrec[k] = to_json_serializable(v)
        scr_rows.append(newrec)

    output_obj = {
        "scr_data": scr_rows,
        "der_data": der_rows
    }

    # Write JSON to specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()