#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2017,13643000000,31673000000,-18030000000,199203000000.0
2018,9862000000,28337000000,-18475000000,201673500000.0
2019,6670000000,27753000000,-21083000000,211908500000.0
2020,14881000000,25255000000,-10374000000,227895000000.0
2021,13510000000,36074000000,-22564000000,244495500000.0
2022,13673000000,24181000000,-10508000000,248678000000.0
2023,11680000000,29101000000,-17421000000,244158500000.0
2024,15511000000,35726000000,-20215000000,247928000000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def to_native_types(record):
    # Convert possible numpy types to native Python types for JSON serialization
    new = {}
    for k, v in record.items():
        if pd.isna(v):
            new[k] = None
        else:
            try:
                # numpy scalar to python native
                if hasattr(v, "item"):
                    new[k] = v.item()
                else:
                    new[k] = v
            except Exception:
                new[k] = v
    return new

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows (convert types to native)
    scr_records = [to_native_types(r) for r in df.to_dict(orient="records")]

    # Calculate Sloan Ratio for each row:
    # Accruals = Net Income - Operating Cashflow
    # Sloan Ratio = Accruals / Avg Total Assets
    der_records = []
    for _, row in df.iterrows():
        # Extract required raw values
        net_income = row["Net Income"]
        op_cashflow = row["Operating Cashflow"]
        avg_total_assets = row["Avg Total Assets"]

        # Calculate accruals dynamically (do not use the provided Accruals column directly)
        accruals_calc = net_income - op_cashflow

        # Protect against division by zero
        if avg_total_assets == 0 or pd.isna(avg_total_assets):
            sloan_ratio = None
        else:
            sloan_ratio = accruals_calc / avg_total_assets

        rec = {
            "Fiscal Year": int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None,
            INDICATOR_NAME: (sloan_ratio if sloan_ratio is None else float(sloan_ratio))
        }
        der_records.append(rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()