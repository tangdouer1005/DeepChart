#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,Cash & Equiv,Receivables,Operating Expenses,Cost of Revenue,Quick Assets,Daily Burn
2016,2216000000,1890000000,18491000000,58254000000,4106000000,210260273.97260275
2017,2538000000,2029000000,18886000000,62282000000,4567000000,222378082.19178084
2018,3595000000,1952000000,19675000000,66548000000,5547000000,236227397.260274
2019,1778000000,1936000000,21630000000,71043000000,3714000000,253898630.13698632
2020,2133000000,2106000000,21729000000,72653000000,4239000000,258580821.9178082
2021,7895000000,2992000000,26575000000,87257000000,10887000000,311868493.1506849
2022,2343000000,3426000000,27792000000,100325000000,5769000000,351005479.4520548
2023,2757000000,3317000000,28739000000,104625000000,6074000000,365380821.9178082
2024,3760000000,3328000000,29271000000,101709000000,7088000000,358849315.0684931
"""

INDICATOR_NAME = "防御区间比率 (Defensive Interval Ratio, DIR)"

def normalize_value(v):
    # Convert numpy and pandas scalar types to native Python types for JSON serialization
    if v is None:
        return None
    if isinstance(v, (np.generic,)):
        try:
            return v.item()
        except Exception:
            # Fallback conversions
            try:
                return int(v)
            except Exception:
                try:
                    return float(v)
                except Exception:
                    return str(v)
    # pandas NaN check
    if isinstance(v, float) and np.isnan(v):
        return None
    return v

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json")
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV data from the embedded multi-line string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Calculation for Defensive Interval Ratio (DIR)
    # Formula:
    # Quick Assets = Cash + Receivables + Trading Financial Assets
    # (If 'Quick Assets' column exists in input, use it as the quick assets value.)
    # Daily Cash Consumption = (Operating Expenses + Cost of Revenue) / 365
    # DIR = Quick Assets / Daily Cash Consumption

    # Determine quick assets source
    if "Quick Assets" in df.columns:
        quick_assets_series = df["Quick Assets"].astype(float)
    else:
        # If Quick Assets not provided, attempt to compute from Cash & Equiv and Receivables and a missing 'Trading Financial Assets' (assumed 0)
        cash_series = df.get("Cash & Equiv", pd.Series([0]*len(df))).astype(float)
        receivables_series = df.get("Receivables", pd.Series([0]*len(df))).astype(float)
        trading_fin_assets = df.get("Trading Financial Assets", pd.Series([0]*len(df))).astype(float) if "Trading Financial Assets" in df.columns else 0.0
        quick_assets_series = cash_series + receivables_series + trading_fin_assets

    # Compute daily cash consumption
    op_exp = df["Operating Expenses"].astype(float)
    cost_rev = df["Cost of Revenue"].astype(float)
    daily_cash_consumption = (op_exp + cost_rev) / 365.0

    # Compute DIR, handling potential division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        dir_values = quick_assets_series / daily_cash_consumption
        # Replace inf or NaN with None
        dir_values = dir_values.replace([np.inf, -np.inf], np.nan)

    # Prepare scr_data: original input rows as list of dicts with native types
    scr_records = df.to_dict(orient="records")
    scr_data = []
    for rec in scr_records:
        normalized = {k: normalize_value(v) for k, v in rec.items()}
        scr_data.append(normalized)

    # Prepare der_data: calculated DIR per row; include Fiscal Year if present
    der_data = []
    for idx, raw_row in enumerate(scr_records):
        entry = {}
        # Include year if present
        if "Fiscal Year" in raw_row:
            entry["Fiscal Year"] = normalize_value(raw_row["Fiscal Year"])
        # Obtain DIR value and normalize (convert numpy types)
        raw_dir = dir_values.iloc[idx]
        entry[INDICATOR_NAME] = None if (pd.isna(raw_dir)) else float(raw_dir)
        der_data.append(entry)

    output_obj = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Write JSON to specified output file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()