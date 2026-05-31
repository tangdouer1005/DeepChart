#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,786000000,3049000000,5723000000,9692200000,3835000000,42233424.65753425
2017,1335000000,3879000000,6412000000,11239000000,5214000000,48358904.10958904
2018,2103000000,4595000000,7116000000,13370000000,6698000000,56126027.39726027
2019,2399000000,4952000000,7085000000,14198000000,7351000000,58309589.04109589
2020,10325000000,6472000000,8130000000,16191000000,16797000000,66632876.71232877
2021,4477000000,8945000000,9316000000,19577000000,13422000000,79158904.10958904
2022,8524000000,9427000000,10486000000,25904000000,17951000000,99698630.1369863
2023,8083000000,9664000000,10703000000,25295000000,17747000000,98624657.53424658
2024,4009000000,9626000000,10066000000,25151000000,13635000000,96484931.50684932
"""

def to_python_native(value):
    # Convert pandas/numpy scalar types to native Python types for JSON serialization
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    # numpy and pandas scalar types have .item()
    try:
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass
    return value

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original CSV rows as array of dicts, converting to native Python types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Calculate Defensive Interval Ratio (DIR) for each row
    der_records = []
    indicator_name = "防御区间比率 (Defensive Interval Ratio, DIR)"
    for _, row in df.iterrows():
        fiscal_year = to_python_native(row["Fiscal Year"])
        # According to reference:
        # Quick Assets = Cash + Receivables + Trading Financial Assets
        # Here the CSV provides a Quick Assets column; use it as the quick assets value.
        quick_assets = float(row["Quick Assets"])
        # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
        operating_expenses = float(row["Operating Expenses"])
        cost_of_revenue = float(row["Cost of Revenue"])
        daily_consumption = (operating_expenses + cost_of_revenue) / 365.0

        if daily_consumption == 0:
            dir_value = None
        else:
            dir_value = quick_assets / daily_consumption

        # convert dir_value to native Python type (float) if not None
        if dir_value is not None:
            dir_value = float(dir_value)

        der_rec = {
            "Fiscal Year": fiscal_year,
            indicator_name: dir_value
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()