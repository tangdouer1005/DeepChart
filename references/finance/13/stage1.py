#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,1400000000,304000000,350000000,1353000000
2017,477000000,880000000,1878000000,3021000000
2018,2368000000,729000000,539000000,3278000000
2019,3687000000,818000000,390000000,3014000000
2020,4495000000,708000000,497000000,3327000000
2021,7071000000,410000000,1140000000,3538000000
2022,6933000000,315000000,1373000000,3267000000
2023,5723000000,698000000,941000000,3243000000
2024,13402000000,603000000,6389000000,3218000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_native_number(v):
    # Convert pandas/numpy scalars to native Python int/float where appropriate.
    # Preserve None for missing values.
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    try:
        # try integer conversion without losing information
        iv = int(v)
        if float(v) == iv:
            return iv
        else:
            return float(v)
    except Exception:
        # fallback: return as-is (likely a string)
        return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(2)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation: EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
    # All components are expected to be numeric columns in the CSV.
    df[INDICATOR_NAME] = (
        df["Net Income"]
        + df["Interest Expense"]
        + df["Income Tax"]
        + df["Depreciation & Amortization"]
    )

    # Build scr_data: original rows with column headers preserved
    scr_records = []
    for rec in df.drop(columns=[INDICATOR_NAME]).to_dict(orient="records"):
        converted = {k: to_native_number(v) for k, v in rec.items()}
        scr_records.append(converted)

    # Build der_data: for each row, include Fiscal Year and the calculated EBITDA
    der_records = []
    for rec in df.to_dict(orient="records"):
        fiscal_year = rec.get("Fiscal Year")
        ebitda_value = rec.get(INDICATOR_NAME)
        der_rec = {
            "Fiscal Year": to_native_number(fiscal_year),
            INDICATOR_NAME: to_native_number(ebitda_value),
        }
        der_records.append(der_rec)

    output_obj = {"scr_data": scr_records, "der_data": der_records}

    # Write JSON to specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()