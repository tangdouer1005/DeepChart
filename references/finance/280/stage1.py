import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2017,31673000000,22764000000,10080000000,32844000000
2018,28337000000,20437000000,10529000000,30966000000
2019,27753000000,21957000000,10678000000,32635000000
2020,25255000000,20568000000,10987000000,31555000000
2021,36074000000,22548000000,11152000000,33700000000
2022,24181000000,25942000000,10658000000,36600000000
2023,29101000000,20428000000,10945000000,31373000000
2024,35726000000,27012000000,11853000000,38865000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_python_native(v):
    # Convert pandas/numpy scalar to native Python types for JSON serialization
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        # If it's a whole number, represent as int to keep output tidy
        if float(v).is_integer():
            return int(v)
        return float(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data by converting each row to JSON-serializable Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_data.append(rec)

    # Calculate the Quality of Income Ratio for each row:
    # Ratio = CFO / (Operating Income + D&A)
    der_data = []
    for _, row in df.iterrows():
        cfo = row.get("CFO")
        op_inc = row.get("Operating Income")
        da = row.get("D&A")

        # Compute denominator from components to ensure dynamic calculation
        denom = None
        if (pd.notna(op_inc)) and (pd.notna(da)):
            denom = op_inc + da

        ratio = None
        if (pd.notna(cfo)) and (denom is not None) and (denom != 0):
            ratio = float(cfo) / float(denom)

        entry = {}
        # Include the fiscal year in the derived data to map results
        if pd.notna(row.get("Fiscal Year")):
            entry["Fiscal Year"] = to_python_native(row.get("Fiscal Year"))
        entry[INDICATOR_NAME] = to_python_native(ratio)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()