#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Net Income,Operating Cashflow,Accruals,Avg Total Assets
2016,1460000000,6135000000,-4675000000,64163500000.0
2017,4536000000,3831000000,705000000,68227000000.0
2018,2888000000,3899000000,-1011000000,71515500000.0
2019,3468000000,6824000000,-3356000000,79694500000.0
2020,3064000000,8640000000,-5576000000,143541500000.0
2021,3024000000,13917000000,-10893000000,203362500000.0
2022,2590000000,16781000000,-14191000000,208950500000.0
2023,8317000000,18559000000,-10242000000,209510000000.0
2024,11339000000,22293000000,-10954000000,207858500000.0
"""

def normalize_value(v):
    # Convert numpy types to native Python types for JSON serialization
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.ndarray,)):
        return v.tolist()
    if pd.isna(v):
        return None
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation for Sloan Ratio (Accruals Ratio)
    # Accruals = Net Income - Operating Cashflow
    # Sloan Ratio = Accruals / Avg Total Assets
    # We compute accruals dynamically (do not hardcode values).
    net_income = df["Net Income"].astype(float)
    operating_cfo = df["Operating Cashflow"].astype(float)
    avg_total_assets = df["Avg Total Assets"].astype(float)

    calculated_accruals = net_income - operating_cfo
    sloan_ratio = calculated_accruals / avg_total_assets

    # Prepare scr_data (raw input rows) - convert types to native Python types
    scr_records = []
    for rec in df.to_dict(orient="records"):
        norm_rec = {k: normalize_value(v) for k, v in rec.items()}
        scr_records.append(norm_rec)

    # Prepare der_data with calculated Sloan Ratio for each row
    der_records = []
    for i, row in df.iterrows():
        fiscal_year = normalize_value(row["Fiscal Year"])
        ratio_value = normalize_value(sloan_ratio.iloc[i])
        der_records.append({
            "Fiscal Year": fiscal_year,
            "斯隆比率 (Sloan Ratio / Accruals Ratio)": ratio_value
        })

    output_obj = {
        "scr_data": scr_records,
        "der_data": der_records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()