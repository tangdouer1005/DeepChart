import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Operating Income,D&A,Denominator (OpInc+D&A)
2016,3203000000,3249000000,1353000000,4602000000
2017,5570000000,1972000000,3021000000,4993000000
2018,6300000000,3844000000,3278000000,7122000000
2019,6136000000,4591000000,3014000000,7605000000
2020,7901000000,5291000000,3327000000,8618000000
2021,10533000000,9200000000,3538000000,12738000000
2022,9581000000,8362000000,3267000000,11629000000
2023,7261000000,6435000000,3243000000,9678000000
2024,8558000000,6825000000,3218000000,10043000000
"""

INDICATOR_NAME = "自由现金流收益质量 (Quality of Income Ratio)"

def to_python_native(val):
    # Convert pandas / numpy types to native python types for JSON serialization
    if pd.isna(val):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    # For plain python numeric types
    if isinstance(val, (int, float, str, bool)):
        return val
    # Fallback: try to convert
    try:
        return int(val)
    except Exception:
        try:
            return float(val)
        except Exception:
            return val

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: raw input rows as list of dicts with native python types
    raw_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        raw_records.append(rec)

    # Calculate the Quality of Income Ratio for each row:
    # Ratio = CFO / (Operating Income + D&A)
    derived_records = []
    for _, row in df.iterrows():
        # get values (use explicit column names)
        cfo = row.get("CFO")
        op_inc = row.get("Operating Income")
        da = row.get("D&A")

        # Ensure values are numeric or treat as missing
        try:
            cfo_val = float(cfo) if not pd.isna(cfo) else None
        except Exception:
            cfo_val = None
        try:
            op_inc_val = float(op_inc) if not pd.isna(op_inc) else None
        except Exception:
            op_inc_val = None
        try:
            da_val = float(da) if not pd.isna(da) else 0.0  # if missing, treat as 0 for denom calc
        except Exception:
            da_val = 0.0

        # Compute denominator per reference: Operating Income + D&A
        if (op_inc_val is None) and ("Denominator (OpInc+D&A)" in df.columns):
            # fallback to provided Denominator column if Operating Income missing
            denom_raw = row.get("Denominator (OpInc+D&A)")
            try:
                denom = float(denom_raw) if not pd.isna(denom_raw) else None
            except Exception:
                denom = None
        else:
            if op_inc_val is None:
                denom = None
            else:
                denom = op_inc_val + da_val

        if (cfo_val is None) or (denom is None) or denom == 0:
            ratio = None
        else:
            ratio = cfo_val / denom

        # Build derived record, include the year column to match input
        derived_rec = {
            "Fiscal Year": to_python_native(row.get("Fiscal Year")),
            INDICATOR_NAME: to_python_native(ratio)
        }
        derived_records.append(derived_rec)

    output_obj = {
        "scr_data": raw_records,
        "der_data": derived_records
    }

    # Write JSON to file with UTF-8 encoding and preserving non-ascii chars
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()