#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,Net Income,Interest Expense,Income Tax,Depreciation & Amortization
2016,2021800000,469600000,1400000,1758000000
2017,2225000000,592000000,201000000,2033000000
2018,2938000000,667000000,324000000,2266000000
2019,3696000000,676000000,374000000,2277000000
2020,6375000000,553000000,850000000,2325000000
2021,7725000000,536000000,1109000000,2592000000
2022,6950000000,726000000,703000000,3381000000
2023,5995000000,1375000000,284000000,3406000000
2024,6335000000,1654000000,657000000,3108000000
"""

INDICATOR_NAME = "息税折旧摊销前利润 (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)"

def to_py_scalar(v):
    """
    Convert pandas / numpy scalar types to native Python types for JSON serialization.
    Leave strings as-is, convert NA to None.
    """
    if pd.isna(v):
        return None
    # numpy/pandas scalars have .item() to convert to Python native
    try:
        return v.item()
    except Exception:
        return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculate EBITDA per provided formula:
    # EBITDA = Net Income + Interest Expense + Income Tax + Depreciation & Amortization
    # Ensure columns exist
    required_cols = ["Net Income", "Interest Expense", "Income Tax", "Depreciation & Amortization"]
    for c in required_cols:
        if c not in df.columns:
            raise KeyError(f"Required column missing from input data: {c}")

    df["EBITDA"] = df["Net Income"] + df["Interest Expense"] + df["Income Tax"] + df["Depreciation & Amortization"]

    # Prepare scr_data: original rows with native Python types
    scr_data = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            if col == "EBITDA":
                # Skip derived column in scr_data; scr_data should reflect input CSV rows only
                continue
            rec[col] = to_py_scalar(row[col])
        scr_data.append(rec)

    # Prepare der_data: one dictionary per row with Fiscal Year and calculated indicator
    der_data = []
    for _, row in df.iterrows():
        rec = {}
        # Include Year key if present in original data
        if "Fiscal Year" in df.columns:
            rec["Fiscal Year"] = to_py_scalar(row["Fiscal Year"])
        rec[INDICATOR_NAME] = to_py_scalar(row["EBITDA"])
        der_data.append(rec)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()