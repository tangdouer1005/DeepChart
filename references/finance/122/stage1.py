#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,8555000000,3856000000,16741000000,16465000000,12411000000,90975342.46575342
2017,6006000000,3667000000,14736000000,13721000000,9673000000,77964383.56164384
2018,9077000000,3685000000,12081000000,13067000000,12762000000,68898630.1369863
2019,6480000000,3971000000,12561000000,14619000000,10451000000,74465753.42465754
2020,6795000000,3144000000,10584000000,13433000000,9939000000,65800000.0
2021,9684000000,3512000000,12990000000,15357000000,13196000000,77663013.69863014
2022,9519000000,3487000000,14095000000,18000000000,13006000000,87931506.84931506
2023,9366000000,3410000000,15923000000,18520000000,12776000000,94364383.56164384
2024,10828000000,3569000000,18745000000,18324000000,14397000000,101558904.10958904
"""

def to_native(val):
    # Convert numpy/pandas scalar types to native Python types for JSON serialization
    if pd.isna(val):
        return None
    # pandas/Numpy scalars have .item()
    if hasattr(val, "item"):
        try:
            return val.item()
        except Exception:
            pass
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data preserving original CSV values (converted to native Python types)
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_data.append(rec)

    # Calculate Defensive Interval Ratio (DIR) per reference:
    # Quick Assets = (use provided "Quick Assets" column as the raw quick assets)
    # Daily cash consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily cash consumption
    der_data = []
    indicator_name = "防御区间比率 (Defensive Interval Ratio, DIR)"
    for _, row in df.iterrows():
        quick_assets = row["Quick Assets"]
        operating_expenses = row["Operating Expenses"]
        cost_of_revenue = row["Cost of Revenue"]

        # Compute daily cash consumption
        daily_cash_consumption = (operating_expenses + cost_of_revenue) / 365.0

        # Guard against division by zero
        if daily_cash_consumption == 0 or pd.isna(daily_cash_consumption):
            dir_value = None
        else:
            dir_value = quick_assets / daily_cash_consumption

        rec = {}
        # include the fiscal year if present
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_native(row["Fiscal Year"])
        rec[indicator_name] = to_native(dir_value)
        der_data.append(rec)

    output = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON with UTF-8 and keep Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()