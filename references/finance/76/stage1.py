#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Current Assets,Total Liabilities,Shares,Net-Net Value
2016,29619000000,113356000000,1872789000,-83737000000
2017,28560000000,104487000000,1897633000,-75927000000
2018,34021000000,98221000000,1914107000,-64200000000
2019,28329000000,92220000000,1895126000,-63891000000
2020,26078000000,107064000000,1870027000,-80986000000
2021,33738000000,99595000000,1920275000,-65857000000
2022,50343000000,97467000000,1940277000,-47124000000
2023,41128000000,99703000000,1880307000,-58575000000
2024,40911000000,103781000000,1817000000,-62870000000
"""

INDICATOR_NAME = "格雷厄姆“烟蒂股”净值 (Graham's Net-Net Working Capital, NNWC)"
PER_SHARE_NAME = "格雷厄姆每股清算价值 (Per-Share Net-Net Value)"

def to_py_val(v):
    """Convert numpy/pandas scalar types to native Python types for JSON serialization."""
    if pd.isna(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        # If it's a whole float, keep as float (JSON will show without trailing .0 if possible)
        return float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multiline string
    df = pd.read_csv(io.StringIO(CSV_DATA.strip()))

    # Ensure required columns exist
    required_cols = {"Current Assets", "Total Liabilities", "Shares"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Input CSV is missing required columns: {missing}")

    # Calculation:
    # Net-Net Value = Total Current Assets - Total Liabilities
    # Per-share liquidation value = Net-Net Value / Shares
    df_calc = df.copy()
    df_calc["NNWC_Total"] = df_calc["Current Assets"] - df_calc["Total Liabilities"]
    # Avoid division by zero; if Shares == 0 then per-share is set to None
    df_calc["NNWC_PerShare"] = df_calc.apply(
        lambda r: (r["NNWC_Total"] / r["Shares"]) if (r["Shares"] not in (0, 0.0, None)) else None,
        axis=1
    )

    # Prepare scr_data: reflect the original CSV rows (use original headers)
    scr_records_raw = df.to_dict(orient="records")
    scr_records = []
    for rec in scr_records_raw:
        cleaned = {}
        for k, v in rec.items():
            cleaned[k] = to_py_val(v)
        scr_records.append(cleaned)

    # Prepare der_data: for each row include Fiscal Year (if present) and the calculated indicator(s)
    der_records = []
    for _, row in df_calc.iterrows():
        rec = {}
        # include Year if present in original data
        if "Fiscal Year" in df_calc.columns:
            rec_key_year = "Fiscal Year"
            rec[rec_key_year] = to_py_val(row[rec_key_year])
        # Main indicator: total Net-Net value
        rec[INDICATOR_NAME] = to_py_val(row["NNWC_Total"])
        # Also include per-share liquidation value as an additional derived field
        rec[PER_SHARE_NAME] = to_py_val(row["NNWC_PerShare"])
        der_records.append(rec)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON to output file with ensure_ascii=False to preserve Chinese characters
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()