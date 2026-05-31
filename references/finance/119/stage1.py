#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd

CSV_DATA = """Fiscal Year,NOPAT,Avg Invested Capital,WACC,Capital Charge
2016,17448726960.56153,77925500000.0,0.1,7792550000.0
2017,1390035647.5980303,77744500000.0,0.1,7774450000.0
2018,17996220623.367966,74521000000.0,0.1,7452100000.0
2019,18296712257.61773,70993500000.0,0.1,7099350000.0
2020,17600252288.29484,77210500000.0,0.1,7721050000.0
2021,19439271196.16227,88923000000.0,0.1,8892300000.0
2022,17768624928.973602,98423000000.0,0.1,9842300000.0
2023,19334290134.11233,89903000000.0,0.1,8990300000.0
2024,18670092527.11692,80133000000.0,0.1,8013300000.0
"""

INDICATOR_NAME = "经济增加值 (Economic Value Added, EVA) - 简化版"

def normalize_value(v):
    # Convert pandas/numpy scalars to native Python types and handle NaN
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    # For numeric-like objects, float() will work; keep ints as ints when possible
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    try:
        f = float(v)
        # if it's integral, return int
        if f.is_integer():
            return int(f)
        return f
    except Exception:
        return v

def main():
    if len(sys.argv) < 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Build scr_data from input CSV (preserve header names)
    raw_records = df.to_dict(orient="records")
    scr_data = []
    for rec in raw_records:
        new_rec = {k: normalize_value(v) for k, v in rec.items()}
        scr_data.append(new_rec)

    # Calculate EVA for each row using: EVA = NOPAT - (Invested Capital * WACC)
    # Map columns (expecting these exact headers in the CSV)
    np_col = "NOPAT"
    ic_col = "Avg Invested Capital"
    wacc_col = "WACC"
    year_col = "Fiscal Year"

    der_data = []
    for rec in raw_records:
        nopat = rec.get(np_col)
        invested = rec.get(ic_col)
        wacc = rec.get(wacc_col)
        year = rec.get(year_col)

        # Ensure numeric types for calculation
        try:
            nopat_f = float(nopat) if nopat is not None else None
        except Exception:
            nopat_f = None
        try:
            invested_f = float(invested) if invested is not None else None
        except Exception:
            invested_f = None
        try:
            wacc_f = float(wacc) if wacc is not None else None
        except Exception:
            wacc_f = None

        eva = None
        if (nopat_f is not None) and (invested_f is not None) and (wacc_f is not None):
            eva = nopat_f - (invested_f * wacc_f)

        der_record = {
            year_col: normalize_value(year),
            INDICATOR_NAME: normalize_value(eva)
        }
        der_data.append(der_record)

    out_obj = {"scr_data": scr_data, "der_data": der_data}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()