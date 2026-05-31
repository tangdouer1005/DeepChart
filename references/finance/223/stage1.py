#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,2021800000,3156300000,-1134500000,43371150000.0
2017,2225000000,4005000000,-1780000000,51288500000.0
2018,2938000000,4543000000,-1605000000,56450500000.0
2019,3696000000,4973000000,-1277000000,57306500000.0
2020,6375000000,8289000000,-1914000000,63716500000.0
2021,7725000000,9543000000,-1818000000,82087500000.0
2022,6950000000,9154000000,-2204000000,96138500000.0
2023,5995000000,8406000000,-2411000000,97940000000.0
2024,6335000000,8667000000,-2332000000,98023500000.0
"""

INDICATOR_NAME = "斯隆比率 (Sloan Ratio / Accruals Ratio)"

def to_python_native(value):
    # Convert numpy / pandas scalar types to native Python types for JSON serialization
    if value is None:
        return None
    # handle pandas NA
    if pd.isna(value):
        return None
    # try .item() for numpy/pandas scalars
    try:
        if hasattr(value, "item"):
            v = value.item()
            # item() may return numpy types still for some edge cases, try again
            if isinstance(v, (np.generic,)):
                return to_python_native(v.item())
            return v
    except Exception:
        pass
    # fallback conversions
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (int, float, str, bool)):
        return value
    return str(value)

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data as list of dicts (mirror input). Ensure native Python types.
    raw_records = df.to_dict(orient="records")
    scr_data = []
    for rec in raw_records:
        cleaned = {k: to_python_native(v) for k, v in rec.items()}
        scr_data.append(cleaned)

    # Calculate Sloan Ratio for each row:
    # Accruals = Net Income - Operating Cashflow
    # Sloan Ratio = Accruals / Avg Total Assets
    der_data = []
    for idx, row in df.iterrows():
        fiscal_year = to_python_native(row.get("Fiscal Year"))
        # Extract necessary raw inputs
        net_income = row.get("Net Income")
        operating_cf = row.get("Operating Cashflow")
        avg_total_assets = row.get("Avg Total Assets")

        # Defensive handling: coerce to float for division
        try:
            ni = float(net_income)
        except Exception:
            ni = None
        try:
            cfo = float(operating_cf)
        except Exception:
            cfo = None
        try:
            ata = float(avg_total_assets)
        except Exception:
            ata = None

        # Compute accruals using formula (do not use precomputed CSV "Accruals" directly for the indicator)
        accruals = None
        sloan_ratio = None
        if (ni is not None) and (cfo is not None):
            accruals = ni - cfo
            # Compute Sloan Ratio if denominator available and not zero
            if (ata is not None) and ata != 0:
                sloan_ratio = accruals / ata

        # Prepare output dict; include Fiscal Year if present and the computed indicator value
        out_rec = {"Fiscal Year": fiscal_year, INDICATOR_NAME: to_python_native(sloan_ratio)}
        der_data.append(out_rec)

    # Compose final JSON object
    result = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write to output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()