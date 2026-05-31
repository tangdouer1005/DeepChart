#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,4484000000,5761000000,373000000,6134000000
2017,5555000000,6622000000,437000000,7059000000
2018,6223000000,7282000000,459000000,7741000000
2019,8183000000,9664000000,522000000,10186000000
2020,7224000000,8081000000,580000000,8661000000
2021,9463000000,10082000000,726000000,10808000000
2022,11195000000,12264000000,750000000,13014000000
2023,11980000000,14008000000,799000000,14807000000
2024,14780000000,15582000000,897000000,16479000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric types (in case)
    numeric_cols = ["CFO", "Operating Income", "D&A"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate the Quality of Income Ratio for each row:
    # Ratio = CFO / (Operating Income + D&A)
    # If D&A or Operating Income missing, fall back to using Operating Income only (per note).
    ratios = []
    for _, row in df.iterrows():
        cfo = row.get("CFO", None)
        opinc = row.get("Operating Income", None)
        da = row.get("D&A", None)

        # Determine denominator: prefer Operating Income + D&A if D&A present and not null.
        denom = None
        if pd.notna(opinc):
            if pd.notna(da):
                denom = opinc + da
            else:
                denom = opinc  # fallback if no D&A
        else:
            # If Operating Income missing but Denominator column exists, try that
            denom_col = "Denominator (OpInc+D&A)"
            if denom_col in row and pd.notna(row[denom_col]):
                denom = row[denom_col]

        ratio_value = None
        if pd.notna(cfo) and denom not in (None, 0) and pd.notna(denom):
            try:
                ratio_value = float(cfo) / float(denom)
            except Exception:
                ratio_value = None

        ratios.append(ratio_value)

    # Prepare scr_data: list of dicts matching the CSV headers
    scr_data = df.fillna("").to_dict(orient="records")

    # Prepare der_data: each dict contains Fiscal Year (if present) and the calculated indicator
    der_data = []
    year_col = "Fiscal Year" if "Fiscal Year" in df.columns else None
    for i, r in enumerate(ratios):
        entry = {}
        if year_col:
            entry[year_col] = scr_data[i].get(year_col)
        # Use None for missing calculations to be JSON serializable as null
        entry[INDICATOR_NAME] = (None if r is None else r)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to the specified file path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()