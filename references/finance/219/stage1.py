#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,15435000000,13441000000,3078000000,16519000000
2017,12753000000,13766000000,2820000000,16586000000
2018,14867000000,13363000000,2834000000,16197000000
2019,15242000000,5487000000,2824000000,8311000000
2020,17403000000,15706000000,3013000000,18719000000
2021,18371000000,17986000000,2735000000,20721000000
2022,16723000000,17813000000,2807000000,20620000000
2023,16848000000,18134000000,2714000000,20848000000
2024,19846000000,18545000000,2896000000,21441000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_python_native(val):
    # Convert numpy types to native Python types for JSON serialization
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        # If it's nan or inf, convert to None
        if np.isnan(val) or np.isinf(val):
            return None
        return float(val)
    if pd.isna(val):
        return None
    return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Ensure numeric columns are proper dtype
    for col in ["CFO", "Operating Income", "D&A"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate the denominator as Operating Income + D&A if possible
    # Fall back to column "Denominator (OpInc+D&A)" if needed
    denom_col = "Denominator (OpInc+D&A)"
    calculated_denoms = []
    ratios = []
    for idx, row in df.iterrows():
        op_inc = row.get("Operating Income", None)
        da = row.get("D&A", None)
        denom = None
        if pd.notna(op_inc) and pd.notna(da):
            denom = op_inc + da
        else:
            # fallback to provided denominator column if present
            if denom_col in df.columns and pd.notna(row.get(denom_col)):
                denom = row.get(denom_col)
        calculated_denoms.append(denom)

        cfo = row.get("CFO", None)
        ratio = None
        # Compute ratio = CFO / (Operating Income + D&A)
        try:
            if pd.notna(cfo) and denom is not None and denom != 0:
                ratio = float(cfo) / float(denom)
            else:
                ratio = None
        except Exception:
            ratio = None
        ratios.append(ratio)

    # Build scr_data: original input rows as list of dicts with native types
    raw_records = df.to_dict(orient="records")
    scr_data = []
    for i, rec in enumerate(raw_records):
        converted = {}
        for k, v in rec.items():
            converted[k] = to_python_native(v)
        scr_data.append(converted)

    # Build der_data: one dict per row with Fiscal Year (if present) and calculated indicator
    der_data = []
    for i, row in df.iterrows():
        entry = {}
        # Preserve Fiscal Year column name if present
        if "Fiscal Year" in df.columns:
            entry["Fiscal Year"] = to_python_native(row["Fiscal Year"])
        entry[INDICATOR_NAME] = to_python_native(ratios[i])
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to file with Chinese characters preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()