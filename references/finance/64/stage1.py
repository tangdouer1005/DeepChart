#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,10739000000,13570000000,-2831000000,117512500000.0
2017,9609000000,13876000000,-4267000000,125735000000.0
2018,110000000,13666000000,-13556000000,119301000000.0
2019,11621000000,15831000000,-4210000000,103288500000.0
2020,11214000000,15426000000,-4212000000,96323000000.0
2021,10591000000,15454000000,-4863000000,96175000000.0
2022,11812000000,13226000000,-1414000000,95749500000.0
2023,12613000000,19886000000,-7273000000,97927000000.0
2024,10320000000,10880000000,-560000000,113132500000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def numpy_safe(value):
    """
    Convert numpy scalar types to native Python types for JSON serialization.
    """
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    # For Python built-ins, just return
    return value

def dataframe_records_safe(df):
    """
    Convert DataFrame rows to JSON-serializable list of dicts,
    converting numpy types to native Python types.
    """
    records = df.to_dict(orient="records")
    safe_records = []
    for rec in records:
        safe_rec = {}
        for k, v in rec.items():
            safe_rec[k] = numpy_safe(v)
        safe_records.append(safe_rec)
    return safe_records

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are proper types
    numeric_cols = ["Net Income", "Operating Cashflow", "Accruals", "Avg Total Assets"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate accruals dynamically as Net Income - Operating Cashflow (per reference)
    # Even though an 'Accruals' column exists in the CSV, we derive it from raw inputs
    df["Accruals_Calc"] = df["Net Income"] - df["Operating Cashflow"]

    # For denominator, use Avg Total Assets (as provided). If missing, fallback to 'Total Assets' if present.
    denom_col = "Avg Total Assets"
    if denom_col not in df.columns:
        # fallback (not expected for this dataset)
        possible = [c for c in df.columns if "Total Asset" in c or "TotalAssets" in c]
        denom_col = possible[0] if possible else None
        if denom_col is None:
            raise ValueError("No suitable total assets column found for denominator.")

    # Compute Sloan Ratio = Accruals / Avg Total Assets
    df[INDICATOR_NAME] = df["Accruals_Calc"] / df[denom_col]

    # Prepare scr_data: original CSV columns and values (preserve original column names)
    scr_df = df[["Fiscal Year", "Net Income", "Operating Cashflow", "Accruals", "Avg Total Assets"]].copy()

    scr_data = dataframe_records_safe(scr_df)

    # Prepare der_data: include Fiscal Year and calculated indicator (derived dynamically)
    der_rows = []
    for _, row in df.iterrows():
        fy = numpy_safe(row["Fiscal Year"])
        val = numpy_safe(row[INDICATOR_NAME])
        der_rows.append({
            "Fiscal Year": fy,
            INDICATOR_NAME: val
        })

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_rows
    }

    # Write JSON to output file with ensure_ascii=False to keep Chinese characters readable
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()