#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Dividends,Net Income,Avg Total Assets,ROA(Avg),Retention Ratio
2016,1350000000.0,5991000000,51701000000.0,0.1158778360186456,0.7746619929894842
2017,1579000000.0,6699000000,66006000000.0,0.1014907735660394,0.7642931780862815
2018,1918000000.0,10301000000,68601000000.0,0.1501581609597527,0.8138044850014562
2019,2269000000.0,12080000000,70899500000.0,0.1703820196193203,0.8121688741721854
2020,2664000000.0,10866000000,76746500000.0,0.1415830037851889,0.7548315847598013
2021,2798000000.0,12311000000,81907500000.0,0.1503036962427128,0.7727235805377305
2022,3203000000.0,14957000000,84198500000.0,0.1776397441759651,0.7858527779634954
2023,3751000000.0,17273000000,88000000000.0,0.1962840909090909,0.7828402709430904
2024,4217000000.0,19743000000,92505000000.0,0.2134263012810118,0.786405308210505
"""

INDICATOR_NAME = "内部增长率 (Internal Growth Rate, IGR)"

def to_python_native(value):
    """
    Convert numpy/pandas scalar types to native Python types for JSON serialization.
    """
    if value is None:
        return None
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    # plain python numeric types
    if isinstance(value, (int, float, str, bool)):
        return value
    # fallback to string
    return str(value)

def compute_igr(row):
    """
    Compute Internal Growth Rate (IGR) for a single row.
    Formulas:
      b = 1 - (Dividends / Net Income)
      ROA = Net Income / Avg Total Assets
      IGR = (ROA * b) / (1 - (ROA * b))
    """
    # Extract raw inputs
    dividends = row.get("Dividends")
    net_income = row.get("Net Income")
    avg_total_assets = row.get("Avg Total Assets")

    # Guard against invalid inputs
    try:
        # Ensure numeric conversion
        d = float(dividends) if dividends is not None and not pd.isna(dividends) else None
        ni = float(net_income) if net_income is not None and not pd.isna(net_income) else None
        ata = float(avg_total_assets) if avg_total_assets is not None and not pd.isna(avg_total_assets) else None
    except Exception:
        return None

    if ni is None or ata is None or ni == 0 or ata == 0:
        return None

    # retention ratio
    b = 1.0 - (d / ni) if d is not None else None
    if b is None:
        return None

    # ROA
    roa = ni / ata

    product = roa * b
    denom = 1.0 - product
    if denom == 0:
        return None

    igr = product / denom
    return igr

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: convert each row to python-native types
    scr_records = []
    for _, row in df.iterrows():
        rec = {}
        for col in df.columns:
            rec[col] = to_python_native(row[col])
        scr_records.append(rec)

    # Compute derived data (IGR) per row
    der_records = []
    for _, row in df.iterrows():
        igr_value = compute_igr(row)
        record = {}
        # include Fiscal Year if present
        if "Fiscal Year" in df.columns:
            fy = row["Fiscal Year"]
            record["Fiscal Year"] = to_python_native(fy)
        # ensure igr is python native (float or None)
        record[INDICATOR_NAME] = to_python_native(igr_value)
        der_records.append(record)

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    # Write JSON output with UTF-8 and ensure Chinese characters are preserved
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()