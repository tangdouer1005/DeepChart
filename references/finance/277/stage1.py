#!/usr/bin/env python3
import sys
import io
import json
import pandas as pd
import numpy as np

CSV_DATA = """Fiscal Year,CFO,Net Income,Total Assets,Avg Total Assets,CFO per Asset,NI per Asset
2017,31673000000,13643000000,198825000000,199203000000.0,0.1589986094586929,0.0684879243786489
2018,28337000000,9862000000,204522000000,201673500000.0,0.1405092885282399,0.0489008223688288
2019,27753000000,6670000000,219295000000,211908500000.0,0.1309669031681126,0.0314758492462548
2020,25255000000,14881000000,236495000000,227895000000.0,0.1108185787314333,0.0652976151297746
2021,36074000000,13510000000,252496000000,244495500000.0,0.1475446378358701,0.0552566407152687
2022,24181000000,13673000000,244860000000,248678000000.0,0.0972381955782176,0.0549827487755249
2023,29101000000,11680000000,243457000000,244158500000.0,0.1191889694604119,0.0478377775092818
2024,35726000000,15511000000,252399000000,247928000000.0,0.1440982865993353,0.0625625181504307
"""

INDICATOR_NAME = "盈余-现金质量剪刀差 (Earnings Quality Spread)"

def numpy_to_native(obj):
    """
    Recursively convert numpy/pandas scalar types in obj to native Python types
    so that json.dump can serialize them.
    """
    if isinstance(obj, dict):
        return {k: numpy_to_native(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [numpy_to_native(v) for v in obj]
    if isinstance(obj, (np.generic,)):
        return obj.item()
    # pandas NA / NaT handling
    if pd.isna(obj):
        return None
    return obj

def main():
    if len(sys.argv) != 2:
        print("Usage: python this.py output.json", file=sys.stderr)
        sys.exit(1)
    out_path = sys.argv[1]

    # Load CSV from the embedded string
    df = pd.read_csv(io.StringIO(CSV_DATA))

    # Prepare scr_data: original rows as dicts with native Python types
    scr_records = df.to_dict(orient="records")
    scr_records = numpy_to_native(scr_records)

    # Calculate Earnings Quality Spread for each row:
    der_records = []
    for idx, row in df.iterrows():
        # Extract raw inputs (ensure float conversion)
        try:
            cfo = float(row["CFO"])
        except Exception:
            cfo = None
        try:
            net_income = float(row["Net Income"])
        except Exception:
            net_income = None
        try:
            total_assets = float(row["Total Assets"])
        except Exception:
            total_assets = None

        # Compute spread = (CFO / TotalAssets) - (NetIncome / TotalAssets)
        spread = None
        if total_assets is None or total_assets == 0:
            spread = None
        else:
            # If any numerator is None, propagate None
            if cfo is None or net_income is None:
                spread = None
            else:
                spread = (cfo / total_assets) - (net_income / total_assets)

        record = {
            # include the fiscal year to map results
            "Fiscal Year": int(row["Fiscal Year"]) if not pd.isna(row["Fiscal Year"]) else None,
            INDICATOR_NAME: spread if spread is None else float(spread),
        }
        der_records.append(record)

    # Final JSON object
    output_obj = {
        "scr_data": scr_records,
        "der_data": numpy_to_native(der_records),
    }

    # Write to file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_obj, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()