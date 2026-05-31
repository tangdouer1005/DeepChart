#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,-674914000,198810000,26698000,947099000
2017,-1962000000,471000000,32000000,1636000000
2018,-976000000,663000000,58000000,1901000000
2019,-862000000,685000000,110000000,2154000000
2020,721000000,748000000,292000000,2322000000
2021,5644000000,371000000,699000000,2911000000
2022,12587000000,191000000,1132000000,3543000000
2023,14974000000,156000000,5001000000,4667000000
2024,7130000000,350000000,1837000000,5368000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def py_value(v):
    # Convert pandas/numpy scalars to native Python types for JSON serialization
    try:
        # numpy/pandas scalar
        return v.item()
    except Exception:
        # plain python types (int, str, etc.) or objects without .item()
        # handle NaN
        try:
            if pd.isna(v):
                return None
        except Exception:
            pass
        return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(2)
    out_path = sys.argv[1]

    # Load CSV from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: rows from the input CSV with native python types
    scr_data = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            row_dict[col] = py_value(row[col])
        scr_data.append(row_dict)

    # Calculate EBITDA for each row:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
    der_data = []
    for _, row in df.iterrows():
        # Safely extract numeric values, treating missing as 0
        ni = row.get("Net Income", 0)
        ie = row.get("Interest Expense", 0)
        tax = row.get("Income Tax", 0)
        da = row.get("Depreciation & Amortization", 0)

        # Convert possible NaN to 0
        ni = 0 if pd.isna(ni) else ni
        ie = 0 if pd.isna(ie) else ie
        tax = 0 if pd.isna(tax) else tax
        da = 0 if pd.isna(da) else da

        # Compute EBITDA
        ebitda = ni + ie + tax + da

        # Convert to native Python type
        ebitda_py = py_value(ebitda)

        # Include Fiscal Year if present
        entry = {}
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = py_value(row["Fiscal Year"])
        entry[INDICATOR_NAME] = ebitda_py
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, separators=(",", ":"))

if __name__ == "__main__":
    main()