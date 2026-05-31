#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,10508000000,579000000,3342000000,3078000000
2017,15326000000,465000000,3063000000,2820000000
2018,9750000000,506000000,3465000000,2834000000
2019,3897000000,509000000,2103000000,2824000000
2020,13027000000,465000000,2731000000,3013000000
2021,14306000000,502000000,3263000000,2735000000
2022,14742000000,439000000,3202000000,2807000000
2023,14653000000,756000000,3615000000,2714000000
2024,14879000000,925000000,3787000000,2896000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are numeric (in case of parsing quirks)
    numeric_cols = ["Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate EBITDA per the provided formula:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation + Amortization
    df["EBITDA_CALC"] = (
        df["Net Income"]
        + df["Interest Expense"]
        + df["Income Tax"]
        + df["Depreciation & Amortization"]
    )

    # Prepare scr_data: original rows as list of dicts with original column headers
    scr_data = df.drop(columns=["EBITDA_CALC"]).to_dict(orient="records")

    # Prepare der_data: one dict per row with Fiscal Year (if present) and the calculated indicator
    der_data = []
    for _, row in df.iterrows():
        entry = {}
        # Include Fiscal Year if present in the original data
        if "Fiscal Year" in df.columns:
            # ensure native python int for year if possible
            try:
                entry["Fiscal Year"] = int(row["Fiscal Year"])
            except Exception:
                entry["Fiscal Year"] = row["Fiscal Year"]
        # Add the calculated EBITDA value (do not hardcode results; use computed value)
        # Convert to native python int if it's an integer value, otherwise float
        ebitda_val = row["EBITDA_CALC"]
        if pd.isna(ebitda_val):
            entry[INDICATOR_NAME] = None
        else:
            # If it's effectively an integer, cast to int to avoid unnecessary decimals
            if float(ebitda_val).is_integer():
                entry[INDICATOR_NAME] = int(ebitda_val)
            else:
                entry[INDICATOR_NAME] = float(ebitda_val)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified output file, ensure non-ASCII characters are preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()