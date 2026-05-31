#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numbers

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,596000000,505000000,2064000000,2199000000,1101000000,11679452.05479452
2017,1766000000,826000000,2129000000,2847000000,2592000000,13632876.712328767
2018,4002000000,1265000000,2612000000,3892000000,5267000000,17819178.08219178
2019,782000000,1424000000,3367000000,4545000000,2206000000,21676712.328767125
2020,10896000000,1657000000,3922000000,4150000000,12553000000,22115068.493150685
2021,847000000,2429000000,5864000000,6279000000,3276000000,33268493.15068493
2022,1990000000,4650000000,7434000000,9439000000,6640000000,46227397.26027397
2023,3389000000,3827000000,11132000000,11618000000,7216000000,62328767.12328767
2024,7280000000,9999000000,11329000000,16621000000,17279000000,76575342.46575342
"""

def to_native(value):
    # Convert pandas/numpy numeric types to native Python types; leave strings as-is.
    if value is None:
        return None
    # pandas uses numpy types which are instances of numbers.Number
    if isinstance(value, numbers.Number):
        # Convert to int if integer-valued
        try:
            if float(value).is_integer():
                return int(int(value))
        except Exception:
            pass
        return float(value)
    # For numpy bools or python bools
    if isinstance(value, (bool,)):
        return value
    # Handle pandas NaT or NaN as None
    try:
        if pd.isna(value):
            return None
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

    # Build scr_data: preserve original column headers and values
    scr_records_raw = df.to_dict(orient='records')
    scr_records = []
    for rec in scr_records_raw:
        converted = {k: to_native(v) for k, v in rec.items()}
        scr_records.append(converted)

    # Calculate 防御区间比率 (Defensive Interval Ratio, DIR) for each row
    der_records = []
    indicator_name = "防御区间比率 (Defensive Interval Ratio, DIR)"
    for _, row in df.iterrows():
        # Use Quick Assets column if present; fallback to sum of Cash & Equiv and Receivables if not
        if "Quick Assets" in row and not pd.isna(row["Quick Assets"]):
            quick_assets = float(row["Quick Assets"])
        else:
            # trading financial assets not provided in CSV; use available components
            ca = 0.0
            if "Cash & Equiv" in row and not pd.isna(row["Cash & Equiv"]):
                ca += float(row["Cash & Equiv"])
            if "Receivables" in row and not pd.isna(row["Receivables"]):
                ca += float(row["Receivables"])
            quick_assets = ca

        # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
        oe = float(row["Operating Expenses"]) if ("Operating Expenses" in row and not pd.isna(row["Operating Expenses"])) else 0.0
        cog = float(row["Cost of Revenue"]) if ("Cost of Revenue" in row and not pd.isna(row["Cost of Revenue"])) else 0.0
        daily_consumption = (oe + cog) / 365.0

        # Avoid division by zero
        if daily_consumption == 0:
            dir_value = None
        else:
            dir_value = quick_assets / daily_consumption

        # Prepare record: include Year if present
        der_rec = {}
        if "Fiscal Year" in row and not pd.isna(row["Fiscal Year"]):
            # convert year to native int if possible
            y = row["Fiscal Year"]
            der_rec["Year"] = to_native(y)
        der_rec[indicator_name] = to_native(dir_value) if dir_value is not None else None
        der_records.append(der_rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write to output JSON file with non-ASCII characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()