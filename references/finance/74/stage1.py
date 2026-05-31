#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,-497000000,12846000000,-13343000000,262309000000.0
2017,9195000000,20338000000,-11143000000,256942000000.0
2018,14824000000,30618000000,-15794000000,253834500000.0
2019,2924000000,27300000000,-24376000000,245645500000.0
2020,-5543000000,10600000000,-16143000000,238609000000.0
2021,15625000000,29200000000,-13575000000,239662500000.0
2022,35465000000,49600000000,-14135000000,248622000000.0
2023,21369000000,35609000000,-14240000000,259670500000.0
2024,17661000000,31492000000,-13831000000,259285000000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def to_native(val):
    # Convert pandas/numpy scalar to native Python types for JSON serialization
    if pd.isna(val):
        return None
    try:
        if isinstance(val, (int,)):
            return val
        if isinstance(val, float):
            # If float is an integer value, keep it as float for consistency with input
            return float(val)
        # For numpy types
        return val.item()
    except Exception:
        return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the hardcoded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data exactly reflecting input CSV rows
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_native(row[col])
        scr_records.append(rec)

    # Calculate Sloan Ratio dynamically for each row
    der_records = []
    for _, row in df.iterrows():
        # Extract raw inputs needed for calculation
        net_income = row["Net Income"]
        operating_cf = row["Operating Cashflow"]
        avg_total_assets = row["Avg Total Assets"]

        # Compute accruals from fundamentals (Net Income - Operating Cashflow)
        computed_accruals = net_income - operating_cf

        # Sloan Ratio = Accruals / Avg Total Assets
        sloan = None
        try:
            if pd.isna(avg_total_assets) or avg_total_assets == 0:
                sloan = None
            else:
                sloan = float(computed_accruals) / float(avg_total_assets)
        except Exception:
            sloan = None

        der_rec = {
            "Fiscal Year": to_native(row["Fiscal Year"]),
            INDICATOR_NAME: to_native(sloan)
        }
        der_records.append(der_rec)

    output = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to the specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()