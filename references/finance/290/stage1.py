#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import math

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,22082000000,2771000000,22308000000,25079000000
2017,30066000000,13819000000,19893000000,33712000000
2018,36014000000,22124000000,18745000000,40869000000
2019,29716000000,12766000000,18998000000,31764000000
2020,14668000000,-29448000000,46009000000,16561000000
2021,48129000000,24019000000,20607000000,44626000000
2022,76797000000,64028000000,24040000000,88068000000
2023,55369000000,44461000000,20641000000,65102000000
2024,55022000000,39652000000,23442000000,63094000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def py_native_value(val):
    """
    Convert pandas/numpy scalar to native Python type for JSON serialization.
    """
    if pd.isna(val):
        return None
    # booleans first
    if isinstance(val, (bool,)):
        return bool(val)
    # integers (numpy int64 etc.)
    if isinstance(val, (int,)) or (hasattr(val, "dtype") and pd.api.types.is_integer_dtype(getattr(val, "dtype"))):
        try:
            return int(val)
        except Exception:
            pass
    # floats
    if isinstance(val, float) or (hasattr(val, "dtype") and pd.api.types.is_float_dtype(getattr(val, "dtype"))):
        # handle nan/inf
        if math.isfinite(val):
            return float(val)
        return None
    # fallback to string
    return val if isinstance(val, str) else str(val)

def compute_quality_of_income_ratio(cfo, operating_income, da):
    """
    Ratio = CFO / (Operating Income + D&A)
    If denominator is zero or None, return None.
    """
    if cfo is None or operating_income is None or da is None:
        return None
    try:
        denom = operating_income + da
        # guard against zero denominator
        if denom == 0:
            return None
        return float(cfo) / float(denom)
    except Exception:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: each row as a dict with original column headers and native python types
    scr_data = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            row_dict[col] = py_native_value(row[col])
        scr_data.append(row_dict)

    # Prepare der_data: compute indicator per row
    der_data = []
    for _, row in df.iterrows():
        # extract needed fields
        fiscal = py_native_value(row.get("Fiscal Year"))
        # Ensure numeric types for computation
        cfo = row.get("CFO")
        opinc = row.get("Operating Income")
        da = row.get("D&A")

        # convert numpy types to python numbers or None
        try:
            cfo_val = None if pd.isna(cfo) else int(cfo)
        except Exception:
            cfo_val = None
        try:
            opinc_val = None if pd.isna(opinc) else int(opinc)
        except Exception:
            opinc_val = None
        try:
            da_val = None if pd.isna(da) else int(da)
        except Exception:
            da_val = None

        ratio = compute_quality_of_income_ratio(cfo_val, opinc_val, da_val)

        entry = {}
        # include Fiscal Year if present in input
        if fiscal is not None:
            entry["Fiscal Year"] = fiscal
        entry[INDICATOR_NAME] = py_native_value(ratio)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # write JSON to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()